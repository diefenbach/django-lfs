from typing import Dict, Any, List
from django.db.models import QuerySet
from reviews.models import Review


class ReviewFilterService:
    """Service for handling review filtering logic."""

    def filter_reviews(self, queryset: QuerySet, filters: Dict[str, Any]) -> QuerySet:
        """Apply filters to review queryset."""

        # Filter by name
        name = filters.get("name", "")
        if name:
            queryset = queryset.filter(user_name__icontains=name)

        # Filter by active status
        active = filters.get("active", "")
        if active:
            queryset = queryset.filter(active=active)

        return queryset

    def get_ordering(self, ordering: str, ordering_order: str = "") -> str:
        """Get proper ordering string for queryset."""
        if ordering == "product":
            # Special handling for product ordering (done in view)
            return ordering
        else:
            return f"{ordering_order}{ordering}"


class ReviewDataService:
    """Service for handling review data calculations and enrichment."""

    def get_reviews_with_data(self, reviews: List[Review]) -> List[Dict[str, Any]]:
        """Get list of reviews with calculated data."""
        result = []

        for review in reviews:
            review_data = {
                "review": review,
                "product_name": review.content.get_name() if review.content else "N/A",
                "user_display": review.user_name or "Anonymous",
                "rating_display": "★" * int(review.score) if hasattr(review, "score") else "N/A",
            }
            result.append(review_data)

        return result

    def get_review_with_data(self, review: Review) -> Dict[str, Any]:
        """Get a single review enriched with calculated data."""
        result = self.get_reviews_with_data([review])
        return result[0] if result else None
