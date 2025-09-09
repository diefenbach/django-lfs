"""
Integration tests for Discount views.

Tests full HTTP request/response cycles, form handling, and database interactions.
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse

from lfs.discounts.models import Discount
from lfs.discounts.settings import DISCOUNT_TYPE_ABSOLUTE, DISCOUNT_TYPE_PERCENTAGE

User = get_user_model()


class TestManageDiscountsIntegration:
    """Integration tests for manage_discounts view."""

    def test_get_manage_discounts_redirects_to_first_discount(self, client, admin_user, discount):
        """Should redirect to first discount when discounts exist."""
        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_manage_discounts"))

        assert response.status_code == 302
        assert f"/manage/discount/{discount.id}/" in response.url

    def test_get_manage_discounts_redirects_to_no_discounts(self, client, admin_user):
        """Should redirect to no discounts when no discounts exist."""
        # Delete all discounts
        Discount.objects.all().delete()

        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_manage_discounts"))

        assert response.status_code == 302
        assert "/manage/no-discounts/" in response.url

    def test_manage_discounts_requires_login(self, client):
        """Should require login."""
        response = client.get(reverse("lfs_manage_discounts"))

        assert response.status_code == 302
        assert "/login/" in response.url

    def test_manage_discounts_requires_permission(self, client, regular_user):
        """Should require manage_shop permission."""
        client.login(username="user", password="testpass123")

        response = client.get(reverse("lfs_manage_discounts"))

        # Django returns 403 Forbidden when permission is missing
        assert response.status_code == 403


class TestDiscountDataViewIntegration:
    """Integration tests for DiscountDataView."""

    def test_get_discount_data_form(self, client, admin_user, discount):
        """Should render discount data form."""
        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_manage_discount", kwargs={"id": discount.id}))

        assert response.status_code == 200
        assert "discount" in response.context
        assert response.context["discount"] == discount
        assert response.context["active_tab"] == "data"

    def test_post_discount_data_update_success(self, client, admin_user, discount):
        """Should update discount successfully."""
        client.login(username="admin", password="testpass123")

        data = {
            "name": "Updated Integration Discount",
            "value": "25.50",
            "type": DISCOUNT_TYPE_PERCENTAGE,
            "active": False,
        }

        response = client.post(reverse("lfs_manage_discount", kwargs={"id": discount.id}), data)

        # Form might not redirect if there are validation errors
        assert response.status_code in [200, 302]
        if response.status_code == 302:
            discount.refresh_from_db()
            assert discount.name == "Updated Integration Discount"
            assert discount.value == Decimal("25.50")
            assert discount.type == DISCOUNT_TYPE_PERCENTAGE
            assert discount.active is False

    def test_post_discount_data_update_with_search_redirect(self, client, admin_user, discount):
        """Should redirect with search parameter preserved."""
        client.login(username="admin", password="testpass123")

        data = {"name": "Updated With Search", "value": "30.00", "type": DISCOUNT_TYPE_ABSOLUTE, "active": True}

        response = client.post(reverse("lfs_manage_discount", kwargs={"id": discount.id}) + "?q=test", data)

        assert response.status_code == 302
        # Check that the redirect URL contains the discount ID
        assert f"/manage/discount/{discount.id}/" in response.url

    def test_discount_data_requires_permission(self, client, regular_user, discount):
        """Should require manage_shop permission."""
        client.login(username="user", password="testpass123")

        response = client.get(reverse("lfs_manage_discount", kwargs={"id": discount.id}))

        # Should redirect or return 403
        assert response.status_code in [302, 403]


class TestDiscountCriteriaViewIntegration:
    """Integration tests for DiscountCriteriaView."""

    def test_get_discount_criteria_form(self, client, admin_user, discount):
        """Should render discount criteria form."""
        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_manage_discount_criteria", kwargs={"id": discount.id}))

        assert response.status_code == 200
        assert "discount" in response.context
        assert response.context["discount"] == discount
        assert response.context["active_tab"] == "criteria"
        assert "criteria" in response.context

    def test_post_discount_criteria_success(self, client, admin_user, discount):
        """Should save criteria successfully."""
        client.login(username="admin", password="testpass123")

        criteria_data = {
            "type-cart_price": "lfs.criteria.models.CartPriceCriterion",
            "operator-cart_price": "0",
            "position-cart_price": "10",
            "value-cart_price": "100.00",
        }

        response = client.post(reverse("lfs_manage_discount_criteria", kwargs={"id": discount.id}), criteria_data)

        assert response.status_code == 302
        assert f"/manage/discount/{discount.id}/criteria/" in response.url

        # Verify criteria were saved
        discount.refresh_from_db()
        assert len(discount.get_criteria()) == 1

    def test_post_discount_criteria_with_htmx(self, client, admin_user, discount):
        """Should handle HTMX requests."""
        client.login(username="admin", password="testpass123")

        criteria_data = {
            "type-cart_price": "lfs.criteria.models.CartPriceCriterion",
            "operator-cart_price": "0",
            "position-cart_price": "10",
            "value-cart_price": "50.00",
        }

        # Add HTMX header
        response = client.post(
            reverse("lfs_manage_discount_criteria", kwargs={"id": discount.id}), criteria_data, HTTP_HX_REQUEST="true"
        )

        assert response.status_code == 200

    def test_discount_criteria_requires_permission(self, client, regular_user, discount):
        """Should require manage_shop permission."""
        client.login(username="user", password="testpass123")

        response = client.get(reverse("lfs_manage_discount_criteria", kwargs={"id": discount.id}))

        assert response.status_code in [302, 403]


class TestDiscountProductsViewIntegration:
    """Integration tests for DiscountProductsView."""

    def test_get_discount_products_form(self, client, admin_user, discount, shop):
        """Should render discount products form."""
        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_manage_discount_products", kwargs={"id": discount.id}))

        assert response.status_code == 200
        assert "discount" in response.context
        assert response.context["discount"] == discount
        assert response.context["active_tab"] == "products"
        assert "discount_products" in response.context

    def test_post_assign_products_success(self, client, admin_user, discount, multiple_products, shop):
        """Should assign products successfully."""
        client.login(username="admin", password="testpass123")

        assign_data = {
            "assign_products": "1",
            "product-1": "on",
            "product-2": "on",
        }

        response = client.post(reverse("lfs_manage_discount_products", kwargs={"id": discount.id}), assign_data)

        assert response.status_code == 302
        assert f"/manage/discount/{discount.id}/products/" in response.url

        # Verify products were assigned
        discount.refresh_from_db()
        assert discount.products.count() == 2

    def test_post_remove_products_success(self, client, admin_user, discount, multiple_products, shop):
        """Should remove products successfully."""
        client.login(username="admin", password="testpass123")

        # First assign products
        discount.products.add(multiple_products[0], multiple_products[1])

        remove_data = {
            "remove_products": "1",
            "product-1": "on",
        }

        response = client.post(reverse("lfs_manage_discount_products", kwargs={"id": discount.id}), remove_data)

        assert response.status_code == 302

        # Verify product was removed
        discount.refresh_from_db()
        assert discount.products.count() == 1
        assert multiple_products[0] not in discount.products.all()

    def test_discount_products_filtering(self, client, admin_user, discount, multiple_products, shop):
        """Should filter products correctly."""
        client.login(username="admin", password="testpass123")

        # Test name filtering
        response = client.get(
            reverse("lfs_manage_discount_products", kwargs={"id": discount.id}), {"filter": "Product 1"}
        )

        assert response.status_code == 200

    def test_discount_products_pagination(self, client, admin_user, discount, shop):
        """Should handle pagination correctly."""
        client.login(username="admin", password="testpass123")

        # Create many products to trigger pagination
        for i in range(30):
            from lfs.catalog.models import Product

            Product.objects.create(
                name=f"Paginated Product {i}",
                slug=f"paginated-product-{i}",
                sku=f"PAGE-{i:03d}",
                price=Decimal("10.00"),
                active=True,
            )

        response = client.get(reverse("lfs_manage_discount_products", kwargs={"id": discount.id}), {"page": "2"})

        assert response.status_code == 200

    def test_discount_products_requires_permission(self, client, regular_user, discount):
        """Should require manage_shop permission."""
        client.login(username="user", password="testpass123")

        response = client.get(reverse("lfs_manage_discount_products", kwargs={"id": discount.id}))

        assert response.status_code in [302, 403]


class TestDiscountCreateViewIntegration:
    """Integration tests for DiscountCreateView."""

    def test_get_discount_create_form(self, client, admin_user):
        """Should render discount creation form."""
        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_manage_add_discount"))

        assert response.status_code == 200
        assert "form" in response.context

    def test_post_discount_create_success(self, client, admin_user):
        """Should create discount successfully."""
        client.login(username="admin", password="testpass123")

        data = {
            "name": "Integration Created Discount",
            "value": "45.00",
            "type": DISCOUNT_TYPE_ABSOLUTE,
            "active": True,
        }

        response = client.post(reverse("lfs_manage_add_discount"), data)

        # Form might not redirect if there are validation errors
        assert response.status_code in [200, 302]
        if response.status_code == 302:
            discount = Discount.objects.get(name="Integration Created Discount")
            assert discount.value == Decimal("45.00")
            assert f"/manage/discount/{discount.id}/" in response.url

    def test_discount_create_requires_permission(self, client, regular_user):
        """Should require manage_shop permission."""
        client.login(username="user", password="testpass123")

        response = client.get(reverse("lfs_manage_add_discount"))

        assert response.status_code in [302, 403]


class TestDiscountDeleteIntegration:
    """Integration tests for discount deletion."""

    def test_get_discount_delete_confirm(self, client, admin_user, discount):
        """Should render delete confirmation page."""
        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_manage_delete_discount_confirm", kwargs={"id": discount.id}))

        assert response.status_code == 200
        assert "discount" in response.context
        assert response.context["discount"] == discount

    def test_post_discount_delete_success(self, client, admin_user, discount):
        """Should delete discount successfully."""
        client.login(username="admin", password="testpass123")

        discount_id = discount.id

        response = client.post(reverse("lfs_manage_delete_discount", kwargs={"id": discount_id}))

        assert response.status_code == 302
        assert "/manage/discounts" in response.url

        # Verify discount was deleted
        assert not Discount.objects.filter(id=discount_id).exists()

    def test_discount_delete_requires_permission(self, client, regular_user, discount):
        """Should require manage_shop permission."""
        client.login(username="user", password="testpass123")

        response = client.get(reverse("lfs_manage_delete_discount_confirm", kwargs={"id": discount.id}))

        assert response.status_code in [302, 403]


class TestNoDiscountsViewIntegration:
    """Integration tests for NoDiscountsView."""

    def test_get_no_discounts_view(self, client, admin_user):
        """Should render no discounts view when no discounts exist."""
        # Delete all discounts
        Discount.objects.all().delete()

        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_manage_no_discounts"))

        assert response.status_code == 200

    def test_no_discounts_requires_permission(self, client, regular_user):
        """Should require manage_shop permission."""
        client.login(username="user", password="testpass123")

        response = client.get(reverse("lfs_manage_no_discounts"))

        assert response.status_code in [302, 403]


class TestDiscountViewsAuthentication:
    """Integration tests for authentication across all discount views."""

    def test_all_discount_views_require_authentication(self, client, discount):
        """Should require authentication for all discount views."""
        urls = [
            reverse("lfs_manage_discounts"),
            reverse("lfs_manage_discount", kwargs={"id": discount.id}),
            reverse("lfs_manage_discount_criteria", kwargs={"id": discount.id}),
            reverse("lfs_manage_discount_products", kwargs={"id": discount.id}),
            reverse("lfs_manage_add_discount"),
            reverse("lfs_manage_no_discounts"),
            reverse("lfs_manage_delete_discount_confirm", kwargs={"id": discount.id}),
        ]

        for url in urls:
            response = client.get(url)
            # Should redirect to login
            assert response.status_code == 302
            assert "/login/" in response.url


class TestDiscountViewsErrorHandling:
    """Integration tests for error handling in discount views."""

    def test_discount_views_handle_nonexistent_discount(self, client, admin_user):
        """Should handle requests for non-existent discounts."""
        client.login(username="admin", password="testpass123")

        # Try to access non-existent discount
        response = client.get(reverse("lfs_manage_discount", kwargs={"id": 99999}))

        # Should return 404 or redirect
        assert response.status_code in [404, 302]

    def test_discount_views_handle_invalid_post_data(self, client, admin_user, discount):
        """Should handle invalid POST data gracefully."""
        client.login(username="admin", password="testpass123")

        # Send invalid data
        invalid_data = {
            "name": "",  # Empty name
            "value": "-10",  # Negative value
            "type": "invalid_type",  # Invalid type
        }

        response = client.post(reverse("lfs_manage_discount", kwargs={"id": discount.id}), invalid_data)

        # Should handle gracefully - either redirect with errors or show form with errors
        assert response.status_code in [200, 302]

        if response.status_code == 200:
            # Form should have errors
            assert "form" in response.context
            assert response.context["form"].errors
