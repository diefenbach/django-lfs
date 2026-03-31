from typing import Dict, Any

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, DeleteView, RedirectView, TemplateView

from reviews.models import Review
from lfs.manage.reviews.forms import ReviewFilterForm, ReviewStateForm
from lfs.manage.reviews.services import ReviewFilterService, ReviewDataService
from lfs.manage.mixins import DirectDeleteMixin


class ReviewListView(PermissionRequiredMixin, TemplateView):
    """Shows a table view of all reviews with filtering and pagination."""

    permission_required = "core.manage_shop"
    template_name = "manage/reviews/review_list.html"

    def get_context_data(self, **kwargs):
        """Extends context with reviews and filter form."""
        from django.core.paginator import Paginator

        ctx = super().get_context_data(**kwargs)

        # Initialize services
        filter_service = ReviewFilterService()
        data_service = ReviewDataService()

        # Get filters from session
        review_filters = self.request.session.get("review-filters", {})

        # Filter reviews
        queryset = Review.objects.all()
        filtered_reviews = filter_service.filter_reviews(queryset, review_filters)

        # Apply ordering
        ordering = self.request.session.get("review-ordering", "id")
        ordering_order = self.request.session.get("review-ordering-order", "")

        if ordering == "product":
            # Special handling for product ordering (requires Python sorting)
            reviews_list = list(filtered_reviews)
            if ordering_order == "-":
                reviews_list.sort(key=lambda k: k.content.get_name() if k.content else "", reverse=True)
            else:
                reviews_list.sort(key=lambda k: k.content.get_name() if k.content else "")
            filtered_reviews = reviews_list
        else:
            ordering_str = filter_service.get_ordering(ordering, ordering_order)
            filtered_reviews = filtered_reviews.order_by(ordering_str)

        # Paginate reviews
        paginator = Paginator(filtered_reviews, 30)
        page_number = self.request.GET.get("page", 1)
        reviews_page = paginator.get_page(page_number)

        # Enrich reviews with data
        reviews_with_data = data_service.get_reviews_with_data(reviews_page)

        # Prepare filter form
        filter_form = ReviewFilterForm(
            initial={
                "name": review_filters.get("name", ""),
                "active": review_filters.get("active", ""),
            }
        )

        ctx.update(
            {
                "reviews_page": reviews_page,
                "reviews_with_data": reviews_with_data,
                "review_filters": review_filters,
                "filter_form": filter_form,
                "ordering": ordering,
            }
        )
        return ctx


class NoReviewsView(PermissionRequiredMixin, TemplateView):
    """Displays that no reviews exist."""

    permission_required = "core.manage_shop"
    template_name = "manage/reviews/no_reviews.html"


class ReviewDataView(PermissionRequiredMixin, TemplateView):
    """View for displaying review data tab."""

    template_name = "manage/reviews/review.html"
    tab_name = "data"
    permission_required = "core.manage_shop"

    def get_review(self) -> Review:
        """Gets the Review object."""
        return get_object_or_404(Review, pk=self.kwargs["id"])

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context for data tab."""
        from django.core.paginator import Paginator

        ctx = super().get_context_data(**kwargs)

        # Initialize services
        filter_service = ReviewFilterService()
        data_service = ReviewDataService()

        # Get current review
        review = self.get_review()

        # Get filters from session
        review_filters = self.request.session.get("review-filters", {})

        # Get paginated reviews for sidebar
        queryset = Review.objects.all()
        filtered_reviews = filter_service.filter_reviews(queryset, review_filters)

        # Apply ordering
        ordering = self.request.session.get("review-ordering", "id")
        ordering_order = self.request.session.get("review-ordering-order", "")

        if ordering == "product":
            # Special handling for product ordering (requires Python sorting)
            reviews_list = list(filtered_reviews)
            if ordering_order == "-":
                reviews_list.sort(key=lambda k: k.content.get_name() if k.content else "", reverse=True)
            else:
                reviews_list.sort(key=lambda k: k.content.get_name() if k.content else "")
            filtered_reviews = reviews_list
        else:
            ordering_str = filter_service.get_ordering(ordering, ordering_order)
            filtered_reviews = filtered_reviews.order_by(ordering_str)

        # Paginate for sidebar
        paginator = Paginator(filtered_reviews, 10)
        page_number = self.request.GET.get("page", 1)
        reviews_page = paginator.get_page(page_number)

        # Get enriched review data via service
        review_data = data_service.get_review_with_data(review)

        # Prepare filter form
        filter_form = ReviewFilterForm(
            initial={
                "name": review_filters.get("name", ""),
                "active": review_filters.get("active", ""),
            }
        )

        ctx.update(
            {
                "review": review,
                "reviews_page": reviews_page,
                "active_tab": self.tab_name,
                "review_filters": review_filters,
                "filter_form": filter_form,
                "ordering": ordering,
                "review_data": review_data,
                "state_form": ReviewStateForm(initial={"active": "1" if review.active else "0"}),
            }
        )
        return ctx


class ApplyReviewFiltersView(PermissionRequiredMixin, FormView):
    """Handles filter form submissions and redirects back to review view."""

    permission_required = "core.manage_shop"
    form_class = ReviewFilterForm

    def form_valid(self, form):
        """Process filter form and update session."""
        review_filters = self.request.session.get("review-filters", {})

        # Update filters based on form data
        name = form.cleaned_data.get("name", "")
        if name:
            review_filters["name"] = name
        elif "name" in review_filters:
            del review_filters["name"]

        active = form.cleaned_data.get("active", "")
        if active:
            review_filters["active"] = active
        elif "active" in review_filters:
            del review_filters["active"]

        self.request.session["review-filters"] = review_filters
        messages.success(self.request, _("Review filters have been applied"))

        return self.get_success_response()

    def form_invalid(self, form):
        """Handle invalid form."""
        messages.error(self.request, _("Invalid filter data"))
        return self.get_success_response()

    def get_success_response(self):
        """Determine where to redirect after filter application."""
        # Check if we came from a specific review
        review_id = self.request.POST.get("review_id") or self.request.GET.get("review_id")
        if review_id:
            return redirect("lfs_manage_review", id=review_id)
        else:
            return redirect("lfs_manage_reviews")


class ResetReviewFiltersView(PermissionRequiredMixin, RedirectView):
    """Resets all review filters."""

    permission_required = "core.manage_shop"

    def get_redirect_url(self, *args, **kwargs):
        """Reset filters and redirect."""
        if "review-filters" in self.request.session:
            del self.request.session["review-filters"]

        messages.success(self.request, _("Review filters have been reset"))

        # Check if we came from a specific review
        review_id = self.request.GET.get("review_id")
        if review_id:
            return reverse("lfs_manage_review", kwargs={"id": review_id})
        else:
            return reverse("lfs_manage_reviews")


class SetReviewOrderingView(PermissionRequiredMixin, RedirectView):
    """Sets review ordering."""

    permission_required = "core.manage_shop"

    def get_redirect_url(self, *args, **kwargs):
        """Set ordering and redirect."""
        ordering = kwargs.get("ordering", "id")

        # Toggle ordering direction if same field
        if ordering == self.request.session.get("review-ordering"):
            if self.request.session.get("review-ordering-order", "") == "":
                self.request.session["review-ordering-order"] = "-"
            else:
                self.request.session["review-ordering-order"] = ""
        else:
            self.request.session["review-ordering-order"] = ""

        self.request.session["review-ordering"] = ordering

        # Check if we came from a specific review
        review_id = self.request.GET.get("review_id")
        if review_id:
            return reverse("lfs_manage_review", kwargs={"id": review_id})
        else:
            return reverse("lfs_manage_reviews")


class ReviewDeleteConfirmView(PermissionRequiredMixin, TemplateView):
    """Confirmation view for review deletion."""

    permission_required = "core.manage_shop"
    template_name = "manage/reviews/delete_review.html"

    def get_context_data(self, **kwargs):
        """Add review to context."""
        ctx = super().get_context_data(**kwargs)
        review = get_object_or_404(Review, pk=self.kwargs["id"])
        ctx["review"] = review
        return ctx


class ReviewDeleteView(PermissionRequiredMixin, DirectDeleteMixin, SuccessMessageMixin, DeleteView):
    """Deletes a review."""

    permission_required = "core.manage_shop"
    model = Review
    pk_url_kwarg = "id"
    success_message = _("Review has been deleted")

    def get_success_url(self):
        """Redirect based on where the delete request came from."""
        # Check if the request came from the individual review page
        referer = self.request.META.get("HTTP_REFERER", "")
        # Individual review page URLs have pattern: /manage/reviews/{id}/
        # Review list page URL is: /manage/reviews/
        # Check if referer contains a review ID pattern (digits after /manage/reviews/)
        import re

        if re.search(r"/manage/reviews/\d+/", referer):
            # This means it came from an individual review page
            # Try to find next review with same ordering
            try:
                ordering = "%s%s" % (
                    self.request.session.get("review-ordering-order", ""),
                    self.request.session.get("review-ordering", "id"),
                )
                # Exclude the current object being deleted from the query
                current_id = self.kwargs.get(self.pk_url_kwarg)
                next_review = Review.objects.exclude(id=current_id).order_by(ordering).first()
                if next_review:
                    return reverse("lfs_manage_review", kwargs={"id": next_review.id})
            except (Review.DoesNotExist, IndexError):
                pass

        # Default: redirect to review list (for requests from review list page)
        return reverse("lfs_manage_reviews")


class SetReviewStateView(PermissionRequiredMixin, FormView):
    """Sets the active state for a review."""

    permission_required = "core.manage_shop"
    form_class = ReviewStateForm

    def form_valid(self, form):
        """Update review state."""
        review_id = self.kwargs.get("id")
        try:
            review = Review.objects.get(pk=review_id)
            review.active = int(form.cleaned_data["active"])
            review.save()
            messages.success(self.request, _("Review state has been updated"))
        except Review.DoesNotExist:
            messages.error(self.request, _("Review not found"))

        return redirect("lfs_manage_review", id=review_id)

    def form_invalid(self, form):
        """Handle invalid form."""
        review_id = self.kwargs.get("id")
        messages.error(self.request, _("Invalid state data"))
        return redirect("lfs_manage_review", id=review_id)
