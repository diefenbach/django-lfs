"""The review management, tested through real requests as a shop manager: the list with its filters, ordering and
paging, a review's page, switching a review on and off, and deleting."""

import pytest
from django.contrib.messages import get_messages
from django.urls import reverse
from reviews.models import Review

from lfs.catalog.models import Product

pytestmark = pytest.mark.django_db

LIST = reverse("lfs_manage_reviews")


@pytest.fixture
def manager(client, admin_user, shop):
    """A test client logged in as a shop manager."""
    client.force_login(admin_user)
    return client


def review(name: str, product: str = "Lamp", active: bool = True, score: float = 4.0) -> Review:
    """Create a review by ``name`` of the product called ``product``."""
    content = Product.objects.get_or_create(slug=product.lower(), defaults={"name": product})[0]
    return Review.objects.create(content=content, user_name=name, score=score, active=active, comment="Nice")


def listed(manager, **params) -> list[str]:
    """Return the reviewers' names in the order the list shows them."""
    return [row["review"].user_name for row in manager.get(LIST, params).context["reviews_with_data"]]


def messages_of(response) -> list[str]:
    """Return the messages the request added for the manager."""
    return [str(m) for m in get_messages(response.wsgi_request)]


class TestList:
    def test_shows_each_review_with_its_product_and_reviewer(self, manager):
        review("Anna", product="Chair", score=3)
        review("", product="Gone", score=0)
        Product.objects.filter(slug="gone").delete()  # a review of a deleted product, without a name

        rows = manager.get(LIST).context["reviews_with_data"]

        assert [(r["product_name"], r["user_display"], r["rating_display"]) for r in rows] == [
            ("Chair", "Anna", "★★★"),
            ("N/A", "Anonymous", ""),
        ]

    def test_filters_by_name_and_state(self, manager):
        review("Anna")
        review("Annabel", active=False)
        review("Bob")

        response = manager.post(reverse("lfs_apply_review_filters_list"), {"name": "ann", "active": "1"})

        assert manager.session["review-filters"] == {"name": "ann", "active": "1"}
        assert response["Location"] == LIST
        assert messages_of(response) == ["Review filters have been applied"]
        assert listed(manager) == ["Anna"]

    def test_an_emptied_filter_is_removed(self, manager):
        manager.post(reverse("lfs_apply_review_filters_list"), {"name": "ann", "active": "0"})

        manager.post(reverse("lfs_apply_review_filters_list"), {"name": "", "active": ""})

        assert manager.session["review-filters"] == {}

    def test_an_invalid_state_filter_is_refused(self, manager):
        response = manager.post(reverse("lfs_apply_review_filters_list"), {"active": "maybe"})

        assert "review-filters" not in manager.session
        assert messages_of(response) == ["Invalid filter data"]

    def test_reset_clears_the_filters_and_returns_to_the_review(self, manager):
        anna = review("Anna")
        manager.post(reverse("lfs_apply_review_filters_list"), {"name": "bob"})

        response = manager.get(reverse("lfs_reset_review_filters"), {"review_id": anna.id})

        assert "review-filters" not in manager.session
        assert response["Location"] == reverse("lfs_manage_review", kwargs={"id": anna.id})

    def test_ordering_by_a_column_and_again_reverses_it(self, manager):
        review("Bob", product="Chair")
        review("Anna", product="Table")
        review("Carl", product="Armchair")

        manager.get(reverse("lfs_set_review_ordering", kwargs={"ordering": "user_name"}))
        by_name = listed(manager)
        manager.get(reverse("lfs_set_review_ordering", kwargs={"ordering": "user_name"}))
        by_name_reversed = listed(manager)
        manager.get(reverse("lfs_set_review_ordering", kwargs={"ordering": "product"}))
        by_product = listed(manager)

        assert by_name == ["Anna", "Bob", "Carl"]
        assert by_name_reversed == ["Carl", "Bob", "Anna"]
        assert by_product == ["Carl", "Bob", "Anna"]

    def test_shows_30_reviews_per_page(self, manager):
        for i in range(32):
            review(f"Reviewer {i}")

        assert len(listed(manager)) == 30
        assert len(listed(manager, page=2)) == 2


class TestReview:
    def test_shows_the_review_and_its_state(self, manager):
        anna = review("Anna", product="Chair", active=False)

        context = manager.get(reverse("lfs_manage_review", kwargs={"id": anna.id})).context

        assert (context["review"], context["review_data"]["product_name"]) == (anna, "Chair")
        assert context["state_form"].initial == {"active": "0"}

    def test_an_unknown_review_is_not_found(self, manager):
        assert manager.get(reverse("lfs_manage_review", kwargs={"id": 99999})).status_code == 404

    @pytest.mark.parametrize("state,active", [("1", True), ("0", False)])
    def test_switches_a_review_on_and_off(self, manager, state: str, active: bool):
        anna = review("Anna", active=not active)

        response = manager.post(reverse("lfs_set_review_state", kwargs={"id": anna.id}), {"active": state})

        assert Review.objects.get(pk=anna.pk).active is active
        assert response["Location"] == reverse("lfs_manage_review", kwargs={"id": anna.id})
        assert messages_of(response) == ["Review state has been updated"]

    def test_an_invalid_state_is_refused(self, manager):
        anna = review("Anna", active=True)

        response = manager.post(reverse("lfs_set_review_state", kwargs={"id": anna.id}), {"active": "2"})

        assert Review.objects.get(pk=anna.pk).active is True
        assert messages_of(response) == ["Invalid state data"]


class TestDelete:
    def test_confirmation_names_the_review(self, manager):
        anna = review("Anna")

        assert (
            manager.get(reverse("lfs_manage_delete_review_confirm", kwargs={"id": anna.id})).context["review"] == anna
        )

    def test_deleting_from_the_list_returns_to_the_list(self, manager):
        anna = review("Anna")

        response = manager.post(reverse("lfs_delete_review", kwargs={"id": anna.id}), HTTP_REFERER=LIST)

        assert not Review.objects.exists()
        assert response["Location"] == LIST
        assert messages_of(response) == ["Review has been deleted"]

    def test_deleting_from_a_review_shows_the_next_one(self, manager):
        anna, bob = review("Anna"), review("Bob")

        response = manager.post(
            reverse("lfs_delete_review", kwargs={"id": anna.id}),
            HTTP_REFERER="http://testserver" + reverse("lfs_manage_review", kwargs={"id": anna.id}),
        )

        assert response["Location"] == reverse("lfs_manage_review", kwargs={"id": bob.id})


def test_an_unknown_ordering_is_ignored(manager):
    """The ordering comes from the URL and is kept in the session; an unknown one must not break the pages."""
    review("Anna")

    manager.get(reverse("lfs_set_review_ordering", kwargs={"ordering": "no_such_field"}))

    assert listed(manager) == ["Anna"]
    assert manager.get(reverse("lfs_manage_review", kwargs={"id": Review.objects.get().id})).status_code == 200
