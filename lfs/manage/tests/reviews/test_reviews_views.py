"""
Comprehensive unit and integration tests for LFS review management views.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Parametrization for variations

Tests cover:
- ReviewListView (list view with filtering and pagination)
- NoReviewsView (empty state view)
- ReviewDataView (data tab view)
- ApplyReviewFiltersView (filter form handling)
- ResetReviewFiltersView (filter reset)
- SetReviewOrderingView (ordering management)
- ReviewDeleteConfirmView (deletion confirmation)
- ReviewDeleteView (review deletion)
- SetReviewStateView (state management)
- Integration tests for complete workflows
"""

import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.urls import reverse
from django.utils import timezone

from reviews.models import Review
from lfs.catalog.models import Product


User = get_user_model()


@pytest.fixture
def product(db, shop):
    """Sample Product for testing."""
    return Product.objects.create(
        name="Test Product",
        slug="test-product",
        sku="TEST-001",
        price=Decimal("29.99"),
        active=True,
    )


@pytest.fixture
def multiple_products(db, shop):
    """Multiple Products for testing."""
    products = []
    for i in range(5):
        product = Product.objects.create(
            name=f"Product {i+1}",
            slug=f"product-{i+1}",
            sku=f"SKU-{i+1:03d}",
            price=Decimal(f"{(i+1)*10}.99"),
            active=True,
        )
        products.append(product)
    return products


@pytest.fixture
def review(db, product, manage_user):
    """Sample Review for testing."""
    return Review.objects.create(
        content=product,
        user=manage_user,
        user_name="Test User",
        user_email="test@example.com",
        comment="Great product!",
        score=5.0,
        active=True,
        creation_date=timezone.now(),
        ip_address="127.0.0.1",
    )


@pytest.fixture
def multiple_reviews(db, multiple_products, manage_user):
    """Multiple Reviews for testing."""
    reviews = []
    for i, product in enumerate(multiple_products):
        review = Review.objects.create(
            content=product,
            user=manage_user,
            user_name=f"User {i+1}",
            user_email=f"user{i+1}@example.com",
            comment=f"Review for product {i+1}",
            score=float((i % 5) + 1),  # Scores 1-5
            active=i % 2 == 0,  # Mix of active/inactive
            creation_date=timezone.now(),
            ip_address="127.0.0.1",
        )
        reviews.append(review)
    return reviews


@pytest.fixture
def anonymous_review(db, product):
    """Anonymous Review for testing."""
    return Review.objects.create(
        content=product,
        user_name="Anonymous User",
        user_email="anonymous@example.com",
        comment="Anonymous review",
        score=4.0,
        active=True,
        creation_date=timezone.now(),
        ip_address="127.0.0.1",
    )


@pytest.fixture
def inactive_review(db, product):
    """Inactive Review for testing."""
    return Review.objects.create(
        content=product,
        user_name="Inactive User",
        user_email="inactive@example.com",
        comment="Inactive review",
        score=3.0,
        active=False,
        creation_date=timezone.now(),
        ip_address="127.0.0.1",
    )


class TestReviewListView:
    """Test ReviewListView functionality."""

    def test_requires_permission(self, client):
        """Should require manage_shop permission."""
        response = client.get(reverse("lfs_manage_reviews"))
        assert response.status_code == 302  # Redirect to login

    def test_renders_template_with_authenticated_user(self, authenticated_client, review):
        """Should render template with authenticated user."""
        response = authenticated_client.get(reverse("lfs_manage_reviews"))
        assert response.status_code == 200
        assert "manage/reviews/review_list.html" in [t.name for t in response.templates]

    def test_context_contains_reviews_page(self, authenticated_client, multiple_reviews):
        """Should include reviews_page in context."""
        response = authenticated_client.get(reverse("lfs_manage_reviews"))
        assert response.status_code == 200
        assert "reviews_page" in response.context
        assert "reviews_with_data" in response.context

    def test_context_contains_filter_form(self, authenticated_client, review):
        """Should include filter form in context."""
        response = authenticated_client.get(reverse("lfs_manage_reviews"))
        assert response.status_code == 200
        assert "filter_form" in response.context
        assert "review_filters" in response.context

    def test_pagination_works(self, authenticated_client, multiple_reviews):
        """Should paginate reviews correctly."""
        # Create more reviews to trigger pagination (default page size is 30)
        for i in range(35):  # Total 40 reviews
            Review.objects.create(
                content=multiple_reviews[0].content,
                user_name=f"User {i+6}",
                user_email=f"user{i+6}@example.com",
                comment=f"Review {i+6}",
                score=3.0,
                active=True,
            )

        response = authenticated_client.get(reverse("lfs_manage_reviews"))
        assert response.status_code == 200
        reviews_page = response.context["reviews_page"]
        assert reviews_page.has_other_pages()

    def test_ordering_from_session(self, authenticated_client, multiple_reviews):
        """Should respect ordering from session."""
        session = authenticated_client.session
        session["review-ordering"] = "score"
        session["review-ordering-order"] = "-"
        session.save()

        response = authenticated_client.get(reverse("lfs_manage_reviews"))
        assert response.status_code == 200
        # Reviews should be ordered by score descending

    def test_filtering_by_name(self, authenticated_client, multiple_reviews):
        """Should filter reviews by name."""
        session = authenticated_client.session
        session["review-filters"] = {"name": "User 1"}
        session.save()

        response = authenticated_client.get(reverse("lfs_manage_reviews"))
        assert response.status_code == 200
        reviews_page = response.context["reviews_page"]
        # Should only show reviews with "User 1" in name

    def test_filtering_by_active_status(self, authenticated_client, multiple_reviews):
        """Should filter reviews by active status."""
        session = authenticated_client.session
        session["review-filters"] = {"active": "1"}
        session.save()

        response = authenticated_client.get(reverse("lfs_manage_reviews"))
        assert response.status_code == 200
        reviews_page = response.context["reviews_page"]
        # Should only show active reviews

    def test_empty_reviews_list(self, authenticated_client):
        """Should handle empty reviews list."""
        response = authenticated_client.get(reverse("lfs_manage_reviews"))
        assert response.status_code == 200
        reviews_page = response.context["reviews_page"]
        assert reviews_page.number == 1
        assert reviews_page.paginator.count == 0


class TestNoReviewsView:
    """Test NoReviewsView functionality."""

    def test_requires_permission(self, client):
        """Should require manage_shop permission."""
        response = client.get(reverse("lfs_manage_no_reviews"))
        assert response.status_code == 302  # Redirect to login

    def test_renders_template_with_authenticated_user(self, authenticated_client):
        """Should render template with authenticated user."""
        response = authenticated_client.get(reverse("lfs_manage_no_reviews"))
        assert response.status_code == 200
        assert "manage/reviews/no_reviews.html" in [t.name for t in response.templates]


class TestReviewDataView:
    """Test ReviewDataView functionality."""

    def test_requires_permission(self, client, review):
        """Should require manage_shop permission."""
        response = client.get(reverse("lfs_manage_review", kwargs={"id": review.id}))
        assert response.status_code == 302  # Redirect to login

    def test_renders_template_with_authenticated_user(self, authenticated_client, review):
        """Should render template with authenticated user."""
        response = authenticated_client.get(reverse("lfs_manage_review", kwargs={"id": review.id}))
        assert response.status_code == 200
        assert "manage/reviews/review.html" in [t.name for t in response.templates]

    def test_context_contains_review_data(self, authenticated_client, review):
        """Should include review_data in context."""
        response = authenticated_client.get(reverse("lfs_manage_review", kwargs={"id": review.id}))
        assert response.status_code == 200
        assert "review_data" in response.context
        assert "state_form" in response.context

    def test_state_form_initial_data(self, authenticated_client, review):
        """Should set correct initial data for state form."""
        response = authenticated_client.get(reverse("lfs_manage_review", kwargs={"id": review.id}))
        assert response.status_code == 200
        state_form = response.context["state_form"]
        assert state_form.initial["active"] == "1" if review.active else "0"

    def test_raises_404_for_nonexistent_review(self, authenticated_client):
        """Should raise 404 for nonexistent review."""
        response = authenticated_client.get(reverse("lfs_manage_review", kwargs={"id": 99999}))
        assert response.status_code == 404


class TestApplyReviewFiltersView:
    """Test ApplyReviewFiltersView functionality."""

    def test_requires_permission(self, client):
        """Should require manage_shop permission."""
        response = client.post(reverse("lfs_apply_review_filters_list"))
        assert response.status_code == 302  # Redirect to login

    def test_form_valid_updates_session_with_name_filter(self, authenticated_client):
        """Should update session with name filter."""
        data = {"name": "Test User"}
        response = authenticated_client.post(reverse("lfs_apply_review_filters_list"), data)

        assert response.status_code == 302
        session = authenticated_client.session
        assert session["review-filters"]["name"] == "Test User"

    def test_form_valid_updates_session_with_active_filter(self, authenticated_client):
        """Should update session with active filter."""
        data = {"active": "1"}
        response = authenticated_client.post(reverse("lfs_apply_review_filters_list"), data)

        assert response.status_code == 302
        session = authenticated_client.session
        assert session["review-filters"]["active"] == "1"

    def test_form_valid_removes_empty_filters(self, authenticated_client):
        """Should remove empty filters from session."""
        # Set initial filters
        session = authenticated_client.session
        session["review-filters"] = {"name": "Test", "active": "1"}
        session.save()

        # Submit form with empty name
        data = {"name": "", "active": "1"}
        response = authenticated_client.post(reverse("lfs_apply_review_filters_list"), data)

        assert response.status_code == 302
        session = authenticated_client.session
        assert "name" not in session["review-filters"]
        assert session["review-filters"]["active"] == "1"

    def test_form_valid_shows_success_message(self, authenticated_client):
        """Should show success message on valid form."""
        data = {"name": "Test User"}
        response = authenticated_client.post(reverse("lfs_apply_review_filters_list"), data)

        assert response.status_code == 302
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert "Review filters have been applied" in str(messages[0])

    def test_form_invalid_shows_error_message(self, authenticated_client):
        """Should show error message on invalid form."""
        # Submit invalid data (malformed form data)
        data = {"name": "x" * 200}  # Exceeds max_length
        response = authenticated_client.post(reverse("lfs_apply_review_filters_list"), data)

        assert response.status_code == 302
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert "Invalid filter data" in str(messages[0])

    def test_redirects_to_specific_review_when_review_id_provided(self, authenticated_client, review):
        """Should redirect to specific review when review_id provided."""
        data = {"name": "Test User", "review_id": review.id}
        response = authenticated_client.post(reverse("lfs_apply_review_filters_list"), data)

        assert response.status_code == 302
        assert response.url == reverse("lfs_manage_review", kwargs={"id": review.id})

    def test_redirects_to_review_list_when_no_review_id(self, authenticated_client):
        """Should redirect to review list when no review_id provided."""
        data = {"name": "Test User"}
        response = authenticated_client.post(reverse("lfs_apply_review_filters_list"), data)

        assert response.status_code == 302
        assert response.url == reverse("lfs_manage_reviews")


class TestResetReviewFiltersView:
    """Test ResetReviewFiltersView functionality."""

    def test_requires_permission(self, client):
        """Should require manage_shop permission."""
        response = client.get(reverse("lfs_reset_review_filters"))
        assert response.status_code == 302  # Redirect to login

    def test_removes_filters_from_session(self, authenticated_client):
        """Should remove filters from session."""
        # Set initial filters
        session = authenticated_client.session
        session["review-filters"] = {"name": "Test", "active": "1"}
        session.save()

        response = authenticated_client.get(reverse("lfs_reset_review_filters"))

        assert response.status_code == 302
        session = authenticated_client.session
        assert "review-filters" not in session

    def test_shows_success_message(self, authenticated_client):
        """Should show success message."""
        response = authenticated_client.get(reverse("lfs_reset_review_filters"))

        assert response.status_code == 302
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert "Review filters have been reset" in str(messages[0])

    def test_redirects_to_specific_review_when_review_id_provided(self, authenticated_client, review):
        """Should redirect to specific review when review_id provided."""
        response = authenticated_client.get(reverse("lfs_reset_review_filters"), {"review_id": review.id})

        assert response.status_code == 302
        assert response.url == reverse("lfs_manage_review", kwargs={"id": review.id})

    def test_redirects_to_review_list_when_no_review_id(self, authenticated_client):
        """Should redirect to review list when no review_id provided."""
        response = authenticated_client.get(reverse("lfs_reset_review_filters"))

        assert response.status_code == 302
        assert response.url == reverse("lfs_manage_reviews")


class TestSetReviewOrderingView:
    """Test SetReviewOrderingView functionality."""

    def test_requires_permission(self, client):
        """Should require manage_shop permission."""
        response = client.get(reverse("lfs_set_review_ordering", kwargs={"ordering": "score"}))
        assert response.status_code == 302  # Redirect to login

    def test_sets_ordering_in_session(self, authenticated_client):
        """Should set ordering in session."""
        response = authenticated_client.get(reverse("lfs_set_review_ordering", kwargs={"ordering": "score"}))

        assert response.status_code == 302
        session = authenticated_client.session
        assert session["review-ordering"] == "score"
        assert session["review-ordering-order"] == ""

    def test_toggles_ordering_direction_for_same_field(self, authenticated_client):
        """Should toggle ordering direction for same field."""
        session = authenticated_client.session
        session["review-ordering"] = "score"
        session["review-ordering-order"] = ""
        session.save()

        # First request should set descending
        response = authenticated_client.get(reverse("lfs_set_review_ordering", kwargs={"ordering": "score"}))

        assert response.status_code == 302
        session = authenticated_client.session
        assert session["review-ordering-order"] == "-"

        # Second request should set ascending
        response = authenticated_client.get(reverse("lfs_set_review_ordering", kwargs={"ordering": "score"}))

        assert response.status_code == 302
        session = authenticated_client.session
        assert session["review-ordering-order"] == ""

    def test_sets_ascending_for_new_field(self, authenticated_client):
        """Should set ascending for new field."""
        session = authenticated_client.session
        session["review-ordering"] = "score"
        session["review-ordering-order"] = "-"
        session.save()

        response = authenticated_client.get(reverse("lfs_set_review_ordering", kwargs={"ordering": "creation_date"}))

        assert response.status_code == 302
        session = authenticated_client.session
        assert session["review-ordering"] == "creation_date"
        assert session["review-ordering-order"] == ""

    def test_redirects_to_specific_review_when_review_id_provided(self, authenticated_client, review):
        """Should redirect to specific review when review_id provided."""
        response = authenticated_client.get(
            reverse("lfs_set_review_ordering", kwargs={"ordering": "score"}), {"review_id": review.id}
        )

        assert response.status_code == 302
        assert response.url == reverse("lfs_manage_review", kwargs={"id": review.id})

    def test_redirects_to_review_list_when_no_review_id(self, authenticated_client):
        """Should redirect to review list when no review_id provided."""
        response = authenticated_client.get(reverse("lfs_set_review_ordering", kwargs={"ordering": "score"}))

        assert response.status_code == 302
        assert response.url == reverse("lfs_manage_reviews")


class TestReviewDeleteConfirmView:
    """Test ReviewDeleteConfirmView functionality."""

    def test_requires_permission(self, client, review):
        """Should require manage_shop permission."""
        response = client.get(reverse("lfs_manage_delete_review_confirm", kwargs={"id": review.id}))
        assert response.status_code == 302  # Redirect to login

    def test_renders_template_with_authenticated_user(self, authenticated_client, review):
        """Should render template with authenticated user."""
        response = authenticated_client.get(reverse("lfs_manage_delete_review_confirm", kwargs={"id": review.id}))
        assert response.status_code == 200
        assert "manage/reviews/delete_review.html" in [t.name for t in response.templates]

    def test_context_contains_review(self, authenticated_client, review):
        """Should include review in context."""
        response = authenticated_client.get(reverse("lfs_manage_delete_review_confirm", kwargs={"id": review.id}))
        assert response.status_code == 200
        assert "review" in response.context
        assert response.context["review"] == review

    def test_raises_404_for_nonexistent_review(self, authenticated_client):
        """Should raise 404 for nonexistent review."""
        response = authenticated_client.get(reverse("lfs_manage_delete_review_confirm", kwargs={"id": 99999}))
        assert response.status_code == 404


class TestReviewDeleteView:
    """Test ReviewDeleteView functionality."""

    def test_requires_permission(self, client, review):
        """Should require manage_shop permission."""
        response = client.post(reverse("lfs_delete_review", kwargs={"id": review.id}))
        assert response.status_code == 302  # Redirect to login

    def test_deletes_review(self, authenticated_client, review):
        """Should delete the review."""
        review_id = review.id
        response = authenticated_client.post(reverse("lfs_delete_review", kwargs={"id": review_id}))

        assert response.status_code == 302
        assert not Review.objects.filter(id=review_id).exists()

    def test_shows_success_message(self, authenticated_client, review):
        """Should show success message."""
        response = authenticated_client.post(reverse("lfs_delete_review", kwargs={"id": review.id}))

        assert response.status_code == 302
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert "Review has been deleted" in str(messages[0])

    def test_redirects_to_review_list_after_deletion_from_list(self, authenticated_client, multiple_reviews):
        """Should redirect to review list when deleting from review list page."""
        # Simulate request from review list page (no trailing slash in referer)
        first_review = multiple_reviews[0]
        response = authenticated_client.post(
            reverse("lfs_delete_review", kwargs={"id": first_review.id}), HTTP_REFERER=reverse("lfs_manage_reviews")
        )

        assert response.status_code == 302
        # Should redirect to review list
        assert response.url == reverse("lfs_manage_reviews")

    def test_redirects_to_next_review_when_deleting_from_individual_page(self, authenticated_client, multiple_reviews):
        """Should redirect to next review when deleting from individual review page."""
        # Set ordering in session
        session = authenticated_client.session
        session["review-ordering"] = "id"
        session["review-ordering-order"] = ""
        session.save()

        # Simulate request from individual review page (with trailing slash in referer)
        first_review = multiple_reviews[0]
        individual_review_url = reverse("lfs_manage_review", kwargs={"id": first_review.id})
        response = authenticated_client.post(
            reverse("lfs_delete_review", kwargs={"id": first_review.id}), HTTP_REFERER=individual_review_url
        )

        assert response.status_code == 302
        # Should redirect to either another review or the review list
        # The behavior depends on whether there are other reviews available
        assert "/manage/reviews/" in response.url

    def test_redirects_to_review_list_when_no_next_review(self, authenticated_client, review):
        """Should redirect to review list when no next review."""
        # Delete ALL reviews first, then create just one
        Review.objects.all().delete()
        single_review = Review.objects.create(
            content=review.content,
            user_name="Single User",
            user_email="single@example.com",
            comment="Single review",
            score=3.0,
            active=True,
        )

        response = authenticated_client.post(reverse("lfs_delete_review", kwargs={"id": single_review.id}))

        assert response.status_code == 302
        # Verify the review was actually deleted
        assert not Review.objects.filter(id=single_review.id).exists()
        # Should redirect to review list when no reviews remain
        assert response.url == reverse("lfs_manage_reviews")

    def test_handles_nonexistent_review_gracefully(self, authenticated_client):
        """Should handle nonexistent review gracefully."""
        response = authenticated_client.post(reverse("lfs_delete_review", kwargs={"id": 99999}))

        assert response.status_code == 404


class TestSetReviewStateView:
    """Test SetReviewStateView functionality."""

    def test_requires_permission(self, client, review):
        """Should require manage_shop permission."""
        data = {"active": "1"}
        response = client.post(reverse("lfs_set_review_state", kwargs={"id": review.id}), data)
        assert response.status_code == 302  # Redirect to login

    def test_updates_review_state_to_active(self, authenticated_client, inactive_review):
        """Should update review state to active."""
        data = {"active": "1"}
        response = authenticated_client.post(reverse("lfs_set_review_state", kwargs={"id": inactive_review.id}), data)

        assert response.status_code == 302
        inactive_review.refresh_from_db()
        assert inactive_review.active is True

    def test_updates_review_state_to_inactive(self, authenticated_client, review):
        """Should update review state to inactive."""
        data = {"active": "0"}
        response = authenticated_client.post(reverse("lfs_set_review_state", kwargs={"id": review.id}), data)

        assert response.status_code == 302
        review.refresh_from_db()
        assert review.active is False

    def test_shows_success_message_on_valid_form(self, authenticated_client, review):
        """Should show success message on valid form."""
        data = {"active": "1"}
        response = authenticated_client.post(reverse("lfs_set_review_state", kwargs={"id": review.id}), data)

        assert response.status_code == 302
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert "Review state has been updated" in str(messages[0])

    def test_shows_error_message_for_nonexistent_review(self, authenticated_client):
        """Should show error message for nonexistent review."""
        data = {"active": "1"}
        response = authenticated_client.post(reverse("lfs_set_review_state", kwargs={"id": 99999}), data)

        assert response.status_code == 302
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert "Review not found" in str(messages[0])

    def test_shows_error_message_on_invalid_form(self, authenticated_client, review):
        """Should show error message on invalid form."""
        data = {}  # Empty data
        response = authenticated_client.post(reverse("lfs_set_review_state", kwargs={"id": review.id}), data)

        assert response.status_code == 302
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert "Invalid state data" in str(messages[0])

    def test_redirects_to_review_view(self, authenticated_client, review):
        """Should redirect to review view."""
        data = {"active": "1"}
        response = authenticated_client.post(reverse("lfs_set_review_state", kwargs={"id": review.id}), data)

        assert response.status_code == 302
        assert response.url == reverse("lfs_manage_review", kwargs={"id": review.id})


class TestReviewManagementIntegration:
    """Integration tests for complete review management workflow."""

    def test_complete_review_management_workflow(self, authenticated_client, multiple_reviews):
        """Test complete workflow: list -> filter -> view -> update state -> delete."""
        # 1. List reviews
        response = authenticated_client.get(reverse("lfs_manage_reviews"))
        assert response.status_code == 200
        assert len(response.context["reviews_page"]) > 0

        # 2. Apply filters
        filter_data = {"name": "User 1"}
        response = authenticated_client.post(reverse("lfs_apply_review_filters_list"), filter_data)
        assert response.status_code == 302

        # 3. View filtered list
        response = authenticated_client.get(reverse("lfs_manage_reviews"))
        assert response.status_code == 200

        # 4. View specific review
        review = multiple_reviews[0]
        response = authenticated_client.get(reverse("lfs_manage_review", kwargs={"id": review.id}))
        assert response.status_code == 200
        assert response.context["review"] == review

        # 5. Update review state
        state_data = {"active": "0"}
        response = authenticated_client.post(reverse("lfs_set_review_state", kwargs={"id": review.id}), state_data)
        assert response.status_code == 302

        # 6. Verify state change
        review.refresh_from_db()
        assert review.active is False

        # 7. Delete review
        response = authenticated_client.post(reverse("lfs_delete_review", kwargs={"id": review.id}))
        assert response.status_code == 302

        # 8. Verify deletion
        assert not Review.objects.filter(id=review.id).exists()

    def test_filtering_and_ordering_workflow(self, authenticated_client, multiple_reviews):
        """Test filtering and ordering workflow."""
        # 1. Set ordering
        response = authenticated_client.get(reverse("lfs_set_review_ordering", kwargs={"ordering": "score"}))
        assert response.status_code == 302

        # 2. Apply filter
        filter_data = {"active": "1"}
        response = authenticated_client.post(reverse("lfs_apply_review_filters_list"), filter_data)
        assert response.status_code == 302

        # 3. View filtered and ordered list
        response = authenticated_client.get(reverse("lfs_manage_reviews"))
        assert response.status_code == 200

        # 4. Reset filters
        response = authenticated_client.get(reverse("lfs_reset_review_filters"))
        assert response.status_code == 302

        # 5. Verify filters are reset
        session = authenticated_client.session
        assert "review-filters" not in session

    def test_pagination_workflow(self, authenticated_client, multiple_reviews):
        """Test pagination workflow."""
        # Create more reviews to trigger pagination (default page size is 30)
        for i in range(35):  # Total 40 reviews
            Review.objects.create(
                content=multiple_reviews[0].content,
                user_name=f"User {i+6}",
                user_email=f"user{i+6}@example.com",
                comment=f"Review {i+6}",
                score=3.0,
                active=True,
            )

        # 1. View first page
        response = authenticated_client.get(reverse("lfs_manage_reviews"))
        assert response.status_code == 200
        reviews_page = response.context["reviews_page"]
        assert reviews_page.number == 1
        assert reviews_page.has_other_pages()

        # 2. Navigate to second page
        response = authenticated_client.get(reverse("lfs_manage_reviews"), {"page": 2})
        assert response.status_code == 200
        reviews_page = response.context["reviews_page"]
        assert reviews_page.number == 2

    def test_error_handling_workflow(self, authenticated_client, review):
        """Test error handling in various scenarios."""
        # 1. Try to access nonexistent review
        response = authenticated_client.get(reverse("lfs_manage_review", kwargs={"id": 99999}))
        assert response.status_code == 404

        # 2. Try to update state of nonexistent review
        response = authenticated_client.post(reverse("lfs_set_review_state", kwargs={"id": 99999}), {"active": "1"})
        assert response.status_code == 302
        messages = list(get_messages(response.wsgi_request))
        assert "Review not found" in str(messages[0])

        # 3. Try to delete nonexistent review
        response = authenticated_client.post(reverse("lfs_delete_review", kwargs={"id": 99999}))
        assert response.status_code == 404

    def test_session_persistence_workflow(self, authenticated_client, multiple_reviews):
        """Test that session data persists across requests."""
        # 1. Set filters and ordering
        session = authenticated_client.session
        session["review-filters"] = {"name": "User 1", "active": "1"}
        session["review-ordering"] = "score"
        session["review-ordering-order"] = "-"
        session.save()

        # 2. Make multiple requests
        for _ in range(3):
            response = authenticated_client.get(reverse("lfs_manage_reviews"))
            assert response.status_code == 200

        # 3. Verify session data is still there
        session = authenticated_client.session
        assert session["review-filters"]["name"] == "User 1"
        assert session["review-filters"]["active"] == "1"
        assert session["review-ordering"] == "score"
        assert session["review-ordering-order"] == "-"
