from django.core.paginator import Paginator
from reviews.models import Review
from .services import ReviewFilterService, ReviewDataService
from .forms import ReviewFilterForm


class ReviewFilterMixin:
    """Mixin for handling review filtering logic."""

    def get_review_filters(self):
        """Get review filters from session."""
        return self.request.session.get("review-filters", {})

    def get_filtered_reviews_queryset(self):
        """Get filtered reviews based on session filters."""
        queryset = Review.objects.all()
        review_filters = self.get_review_filters()

        # Get ordering from session
        ordering = self.request.session.get("review-ordering", "id")
        ordering_order = self.request.session.get("review-ordering-order", "")

        filter_service = ReviewFilterService()
        queryset = filter_service.filter_reviews(queryset, review_filters)

        # Apply ordering
        if ordering == "product":
            # Special handling for product ordering (done in view as it requires Python sorting)
            reviews = list(queryset)
            if ordering_order == "-":
                reviews.sort(key=lambda k: k.content.get_name() if k.content else "", reverse=True)
            else:
                reviews.sort(key=lambda k: k.content.get_name() if k.content else "")
            return reviews
        else:
            ordering_str = filter_service.get_ordering(ordering, ordering_order)
            return queryset.order_by(ordering_str)

    def get_filter_form_initial(self):
        """Get initial data for filter form."""
        review_filters = self.get_review_filters()
        return {
            "name": review_filters.get("name", ""),
            "active": review_filters.get("active", ""),
        }


class ReviewPaginationMixin:
    """Mixin for handling review pagination."""

    def get_paginated_reviews(self, page_size=30):
        """Get paginated reviews."""
        queryset = self.get_filtered_reviews_queryset()

        # Handle both QuerySet and list (for product ordering)
        if isinstance(queryset, list):
            paginator = Paginator(queryset, page_size)
        else:
            paginator = Paginator(queryset, page_size)

        page_number = self.request.GET.get("page", 1)
        return paginator.get_page(page_number)


class ReviewDataMixin:
    """Mixin for handling review data calculations."""

    def get_reviews_with_data(self, reviews):
        """Get list of reviews with calculated data."""
        data_service = ReviewDataService()
        return data_service.get_reviews_with_data(reviews)

    def get_review_with_data(self, review):
        """Get a single review enriched with calculated data."""
        data_service = ReviewDataService()
        return data_service.get_review_with_data(review)


class ReviewContextMixin:
    """Mixin for providing common review context data."""

    def get_review_context_data(self, **kwargs):
        """Get common context data for review views."""
        review_filters = self.get_review_filters()
        filter_form = ReviewFilterForm(initial=self.get_filter_form_initial())

        return {
            "review_filters": review_filters,
            "filter_form": filter_form,
            "ordering": self.request.session.get("review-ordering", "id"),
        }
