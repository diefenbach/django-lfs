"""
Comprehensive integration tests for payment method management views.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Integration testing with real HTTP requests

Tests cover:
- ManagePaymentsView (redirect logic)
- NoPaymentMethodsView (empty state)
- PaymentMethodDataView (data tab with form handling)
- PaymentMethodCriteriaView (criteria tab with HTMX)
- PaymentMethodPricesView (prices tab with CRUD operations)
- PaymentMethodCreateView (creation workflow)
- PaymentMethodDeleteConfirmView and PaymentMethodDeleteView (deletion workflow)
- PaymentMethodPriceCriteriaView and PaymentMethodPriceCriteriaSaveView (price criteria)
- Authentication and permission requirements
- Session handling
- Template rendering
- Error handling
- HTMX interactions
"""

import pytest
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.urls import reverse
from django.test import Client

from lfs.payment.models import PaymentMethod, PaymentMethodPrice
from lfs.customer.models import Customer

User = get_user_model()


@pytest.fixture
def client():
    """Django test client."""
    return Client()


@pytest.fixture
def admin_user(db):
    """Admin user with proper permissions."""
    return User.objects.create_user(
        username="admin", email="admin@example.com", password="testpass123", is_staff=True, is_superuser=True
    )


@pytest.fixture
def regular_user(db):
    """Regular user without admin permissions."""
    return User.objects.create_user(username="regular", email="regular@example.com", password="testpass123")


class TestManagePaymentsViewIntegration:
    """Integration tests for ManagePaymentsView."""

    def test_redirects_to_first_payment_method_when_authenticated_and_authorized(
        self, client, admin_user, payment_method
    ):
        """Test redirect to first payment method for authorized user."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_payment_methods"))

        assert response.status_code == 302
        expected_url = reverse("lfs_manage_payment_method", kwargs={"id": payment_method.id})
        assert response.url == expected_url

    def test_redirects_to_no_payment_methods_when_none_exist(self, client, admin_user):
        """Test redirect to no payment methods page when none exist."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_payment_methods"))

        assert response.status_code == 302
        expected_url = reverse("lfs_manage_no_payment_methods")
        assert response.url == expected_url

    def test_requires_authentication(self, client):
        """Test that view requires authentication."""
        response = client.get(reverse("lfs_manage_payment_methods"))

        # Should redirect to login or return 403
        assert response.status_code in [302, 403]

    def test_requires_manage_shop_permission(self, client, regular_user):
        """Test that view requires manage_shop permission."""
        client.force_login(regular_user)

        response = client.get(reverse("lfs_manage_payment_methods"))

        assert response.status_code == 403

    def test_orders_payment_methods_alphabetically(self, client, admin_user):
        """Test that payment methods are ordered alphabetically."""
        # Create payment methods in reverse order
        zebra_method = PaymentMethod.objects.create(name="Zebra Payment", active=True, priority=10)
        alpha_method = PaymentMethod.objects.create(name="Alpha Payment", active=True, priority=20)

        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_payment_methods"))

        # Should redirect to Alpha Payment (first alphabetically)
        expected_url = reverse("lfs_manage_payment_method", kwargs={"id": alpha_method.id})
        assert response.url == expected_url


class TestNoPaymentMethodsViewIntegration:
    """Integration tests for NoPaymentMethodsView."""

    def test_renders_no_payment_methods_template(self, client, admin_user):
        """Test that view renders the correct template."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_no_payment_methods"))

        assert response.status_code == 200
        assert "manage/payment_methods/no_payment_methods.html" in [t.name for t in response.templates]

    def test_requires_authentication(self, client):
        """Test that view requires authentication."""
        response = client.get(reverse("lfs_manage_no_payment_methods"))

        assert response.status_code in [302, 403]

    def test_requires_manage_shop_permission(self, client, regular_user):
        """Test that view requires manage_shop permission."""
        client.force_login(regular_user)

        response = client.get(reverse("lfs_manage_no_payment_methods"))

        assert response.status_code == 403


class TestPaymentMethodDataViewIntegration:
    """Integration tests for PaymentMethodDataView."""

    def test_get_renders_payment_method_form(self, client, admin_user, payment_method):
        """Test GET request renders payment method form."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_payment_method", kwargs={"id": payment_method.id}))

        assert response.status_code == 200
        assert "payment_method" in response.context
        assert response.context["payment_method"] == payment_method
        assert "form" in response.context
        assert response.context["active_tab"] == "data"

    def test_post_updates_payment_method_successfully(self, client, admin_user, payment_method):
        """Test POST request updates payment method successfully."""
        client.force_login(admin_user)

        updated_data = {
            "name": "Updated Payment Method",
            "description": "Updated description",
            "active": False,
        }

        response = client.post(
            reverse("lfs_manage_payment_method", kwargs={"id": payment_method.id}), data=updated_data
        )

        assert response.status_code == 302

        payment_method.refresh_from_db()
        assert payment_method.name == "Updated Payment Method"
        assert payment_method.description == "Updated description"
        assert payment_method.active is False

    def test_post_shows_success_message(self, client, admin_user, payment_method):
        """Test POST request shows success message."""
        client.force_login(admin_user)

        updated_data = {
            "name": "Updated Payment Method",
            "description": "Updated description",
            "active": True,
        }

        response = client.post(
            reverse("lfs_manage_payment_method", kwargs={"id": payment_method.id}), data=updated_data, follow=True
        )

        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert "Payment method has been saved" in str(messages[0])

    def test_post_with_invalid_data_shows_form_errors(self, client, admin_user, payment_method):
        """Test POST with invalid data shows form errors."""
        client.force_login(admin_user)

        invalid_data = {
            "name": "",  # Required field
            "description": "Updated description",
            "active": True,
        }

        response = client.post(
            reverse("lfs_manage_payment_method", kwargs={"id": payment_method.id}), data=invalid_data
        )

        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["form"].errors

    def test_get_with_search_query_includes_search_in_context(self, client, admin_user, payment_method):
        """Test GET with search query includes search in context."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_payment_method", kwargs={"id": payment_method.id}) + "?q=test")

        assert response.status_code == 200
        assert response.context["search_query"] == "test"

    def test_requires_authentication(self, client, payment_method):
        """Test that view requires authentication."""
        response = client.get(reverse("lfs_manage_payment_method", kwargs={"id": payment_method.id}))

        assert response.status_code in [302, 403]

    def test_requires_manage_shop_permission(self, client, regular_user, payment_method):
        """Test that view requires manage_shop permission."""
        client.force_login(regular_user)

        response = client.get(reverse("lfs_manage_payment_method", kwargs={"id": payment_method.id}))

        assert response.status_code == 403

    def test_get_with_nonexistent_payment_method_returns_404(self, client, admin_user):
        """Test GET with nonexistent payment method returns 404."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_payment_method", kwargs={"id": 999}))

        assert response.status_code == 404


class TestPaymentMethodCriteriaViewIntegration:
    """Integration tests for PaymentMethodCriteriaView."""

    def test_get_renders_criteria_tab(self, client, admin_user, payment_method):
        """Test GET request renders criteria tab."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_payment_method_criteria", kwargs={"id": payment_method.id}))

        assert response.status_code == 200
        assert response.context["active_tab"] == "criteria"
        assert "criteria" in response.context

    @patch.object(PaymentMethod, "save_criteria")
    def test_post_saves_criteria_and_redirects(self, mock_save_criteria, client, admin_user, payment_method):
        """Test POST saves criteria and redirects."""
        client.force_login(admin_user)

        response = client.post(
            reverse("lfs_manage_payment_method_criteria", kwargs={"id": payment_method.id}),
            data={"criteria_data": "test"},
        )

        mock_save_criteria.assert_called_once()
        assert response.status_code == 302

    @patch.object(PaymentMethod, "save_criteria")
    def test_post_shows_success_message(self, mock_save_criteria, client, admin_user, payment_method):
        """Test POST shows success message."""
        client.force_login(admin_user)

        response = client.post(
            reverse("lfs_manage_payment_method_criteria", kwargs={"id": payment_method.id}),
            data={"criteria_data": "test"},
            follow=True,
        )

        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert "Criteria have been saved" in str(messages[0])

    @patch.object(PaymentMethod, "save_criteria")
    def test_post_with_htmx_returns_template_fragment(self, mock_save_criteria, client, admin_user, payment_method):
        """Test POST with HTMX returns template fragment."""
        client.force_login(admin_user)

        response = client.post(
            reverse("lfs_manage_payment_method_criteria", kwargs={"id": payment_method.id}),
            data={"criteria_data": "test"},
            HTTP_HX_REQUEST="true",
        )

        assert response.status_code == 200
        # Should return criteria tab template fragment
        assert "criteria" in response.context

    def test_requires_authentication(self, client, payment_method):
        """Test that view requires authentication."""
        response = client.get(reverse("lfs_manage_payment_method_criteria", kwargs={"id": payment_method.id}))

        assert response.status_code in [302, 403]

    def test_requires_manage_shop_permission(self, client, regular_user, payment_method):
        """Test that view requires manage_shop permission."""
        client.force_login(regular_user)

        response = client.get(reverse("lfs_manage_payment_method_criteria", kwargs={"id": payment_method.id}))

        assert response.status_code == 403


class TestPaymentMethodPricesViewIntegration:
    """Integration tests for PaymentMethodPricesView."""

    def test_get_renders_prices_tab(self, client, admin_user, payment_method_with_prices):
        """Test GET request renders prices tab."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_payment_method_prices", kwargs={"id": payment_method_with_prices.id}))

        assert response.status_code == 200
        assert response.context["active_tab"] == "prices"
        assert "prices" in response.context
        assert response.context["prices"].count() == 2

    def test_post_add_price_creates_new_price(self, client, admin_user, payment_method):
        """Test POST with add_price creates new price."""
        client.force_login(admin_user)

        response = client.post(
            reverse("lfs_manage_payment_method_prices", kwargs={"id": payment_method.id}),
            data={"add_price": "true", "price": "15.00"},
        )

        assert response.status_code == 302
        assert payment_method.prices.filter(price=Decimal("15.00")).exists()

    def test_post_add_price_shows_success_message(self, client, admin_user, payment_method):
        """Test POST add_price shows success message."""
        client.force_login(admin_user)

        response = client.post(
            reverse("lfs_manage_payment_method_prices", kwargs={"id": payment_method.id}),
            data={"add_price": "true", "price": "15.00"},
            follow=True,
        )

        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert "Price has been added" in str(messages[0])

    def test_post_update_prices_modifies_existing_prices(self, client, admin_user, payment_method_with_prices):
        """Test POST with update action modifies existing prices."""
        client.force_login(admin_user)
        price = payment_method_with_prices.prices.first()

        response = client.post(
            reverse("lfs_manage_payment_method_prices", kwargs={"id": payment_method_with_prices.id}),
            data={"action": "update", f"price-{price.id}": "25.00", f"priority-{price.id}": "15"},
        )

        assert response.status_code == 302
        price.refresh_from_db()
        assert price.price == Decimal("25.00")

    def test_post_delete_prices_removes_existing_prices(self, client, admin_user, payment_method_with_prices):
        """Test POST with delete action removes existing prices."""
        client.force_login(admin_user)
        price = payment_method_with_prices.prices.first()
        price_id = price.id

        response = client.post(
            reverse("lfs_manage_payment_method_prices", kwargs={"id": payment_method_with_prices.id}),
            data={"action": "delete", f"delete-{price_id}": "true"},
        )

        assert response.status_code == 302
        assert not PaymentMethodPrice.objects.filter(id=price_id).exists()

    def test_post_update_prices_shows_success_message(self, client, admin_user, payment_method_with_prices):
        """Test POST update prices shows success message."""
        client.force_login(admin_user)
        price = payment_method_with_prices.prices.first()

        response = client.post(
            reverse("lfs_manage_payment_method_prices", kwargs={"id": payment_method_with_prices.id}),
            data={"action": "update", f"price-{price.id}": "25.00", f"priority-{price.id}": "15"},
            follow=True,
        )

        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert "Prices have been updated" in str(messages[0])

    def test_post_delete_prices_shows_success_message(self, client, admin_user, payment_method_with_prices):
        """Test POST delete prices shows success message."""
        client.force_login(admin_user)
        price = payment_method_with_prices.prices.first()

        response = client.post(
            reverse("lfs_manage_payment_method_prices", kwargs={"id": payment_method_with_prices.id}),
            data={"action": "delete", f"delete-{price.id}": "true"},
            follow=True,
        )

        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert "Prices have been deleted" in str(messages[0])

    def test_post_add_price_with_invalid_price_uses_zero(self, client, admin_user, payment_method):
        """Test POST add_price with invalid price uses zero."""
        client.force_login(admin_user)

        response = client.post(
            reverse("lfs_manage_payment_method_prices", kwargs={"id": payment_method.id}),
            data={"add_price": "true", "price": "invalid"},
        )

        assert response.status_code == 302
        assert payment_method.prices.filter(price=Decimal("0.0")).exists()

    def test_requires_authentication(self, client, payment_method):
        """Test that view requires authentication."""
        response = client.get(reverse("lfs_manage_payment_method_prices", kwargs={"id": payment_method.id}))

        assert response.status_code in [302, 403]

    def test_requires_manage_shop_permission(self, client, regular_user, payment_method):
        """Test that view requires manage_shop permission."""
        client.force_login(regular_user)

        response = client.get(reverse("lfs_manage_payment_method_prices", kwargs={"id": payment_method.id}))

        assert response.status_code == 403


class TestPaymentMethodCreateViewIntegration:
    """Integration tests for PaymentMethodCreateView."""

    def test_get_renders_create_form(self, client, admin_user):
        """Test GET request renders create form."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_add_payment_method"))

        assert response.status_code == 200
        assert "form" in response.context
        assert "manage/payment_methods/add_payment_method.html" in [t.name for t in response.templates]

    def test_post_creates_payment_method_successfully(self, client, admin_user):
        """Test POST creates payment method successfully."""
        client.force_login(admin_user)

        response = client.post(reverse("lfs_manage_add_payment_method"), data={"name": "New Payment Method"})

        assert response.status_code == 302
        assert PaymentMethod.objects.filter(name="New Payment Method").exists()

    def test_post_redirects_to_payment_method_detail(self, client, admin_user):
        """Test POST redirects to payment method detail."""
        client.force_login(admin_user)

        response = client.post(reverse("lfs_manage_add_payment_method"), data={"name": "New Payment Method"})

        payment_method = PaymentMethod.objects.get(name="New Payment Method")
        expected_url = reverse("lfs_manage_payment_method", kwargs={"id": payment_method.id})
        assert response.url == expected_url

    def test_post_shows_success_message(self, client, admin_user):
        """Test POST shows success message."""
        client.force_login(admin_user)

        response = client.post(
            reverse("lfs_manage_add_payment_method"), data={"name": "New Payment Method"}, follow=True
        )

        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert "Payment method has been created" in str(messages[0])

    def test_post_with_invalid_data_shows_form_errors(self, client, admin_user):
        """Test POST with invalid data shows form errors."""
        client.force_login(admin_user)

        response = client.post(reverse("lfs_manage_add_payment_method"), data={"name": ""})  # Empty name

        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["form"].errors

    def test_requires_authentication(self, client):
        """Test that view requires authentication."""
        response = client.get(reverse("lfs_manage_add_payment_method"))

        assert response.status_code in [302, 403]

    def test_requires_manage_shop_permission(self, client, regular_user):
        """Test that view requires manage_shop permission."""
        client.force_login(regular_user)

        response = client.get(reverse("lfs_manage_add_payment_method"))

        assert response.status_code == 403


class TestPaymentMethodDeleteConfirmViewIntegration:
    """Integration tests for PaymentMethodDeleteConfirmView."""

    def test_get_renders_delete_confirmation(self, client, admin_user, payment_method):
        """Test GET renders delete confirmation."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_delete_payment_method_confirm", kwargs={"id": payment_method.id}))

        assert response.status_code == 200
        assert response.context["payment_method"] == payment_method
        assert "manage/payment_methods/delete_payment_method.html" in [t.name for t in response.templates]

    def test_requires_authentication(self, client, payment_method):
        """Test that view requires authentication."""
        response = client.get(reverse("lfs_manage_delete_payment_method_confirm", kwargs={"id": payment_method.id}))

        assert response.status_code in [302, 403]

    def test_requires_manage_shop_permission(self, client, regular_user, payment_method):
        """Test that view requires manage_shop permission."""
        client.force_login(regular_user)

        response = client.get(reverse("lfs_manage_delete_payment_method_confirm", kwargs={"id": payment_method.id}))

        assert response.status_code == 403

    def test_get_with_nonexistent_payment_method_returns_404(self, client, admin_user):
        """Test GET with nonexistent payment method returns 404."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_delete_payment_method_confirm", kwargs={"id": 999}))

        assert response.status_code == 404


class TestPaymentMethodDeleteViewIntegration:
    """Integration tests for PaymentMethodDeleteView."""

    @patch("lfs.payment.utils.get_default_payment_method")
    def test_post_deletes_payment_method_successfully(self, mock_get_default, client, admin_user, payment_method):
        """Test POST deletes payment method successfully."""
        client.force_login(admin_user)

        # Mock default payment method
        default_method = PaymentMethod.objects.create(name="Default", active=True, priority=1)
        mock_get_default.return_value = default_method

        payment_method_id = payment_method.id

        response = client.post(reverse("lfs_manage_delete_payment_method", kwargs={"id": payment_method_id}))

        assert response.status_code == 302
        assert not PaymentMethod.objects.filter(id=payment_method_id).exists()

    @patch("lfs.payment.utils.get_default_payment_method")
    def test_post_redirects_to_payment_methods_list(self, mock_get_default, client, admin_user, payment_method):
        """Test POST redirects to payment methods list."""
        client.force_login(admin_user)

        # Mock default payment method
        default_method = PaymentMethod.objects.create(name="Default", active=True, priority=1)
        mock_get_default.return_value = default_method

        response = client.post(reverse("lfs_manage_delete_payment_method", kwargs={"id": payment_method.id}))

        expected_url = reverse("lfs_manage_payment_methods")
        assert response.url == expected_url

    @patch("lfs.payment.utils.get_default_payment_method")
    def test_post_shows_success_message(self, mock_get_default, client, admin_user, payment_method):
        """Test POST shows success message."""
        client.force_login(admin_user)

        # Mock default payment method
        default_method = PaymentMethod.objects.create(name="Default", active=True, priority=1)
        mock_get_default.return_value = default_method

        response = client.post(
            reverse("lfs_manage_delete_payment_method", kwargs={"id": payment_method.id}), follow=True
        )

        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert "Payment method has been deleted" in str(messages[0])

    @patch("lfs.payment.utils.get_default_payment_method")
    def test_post_updates_customer_payment_methods(self, mock_get_default, client, admin_user, payment_method):
        """Test POST updates customers using the deleted payment method."""
        client.force_login(admin_user)

        # Create customer using the payment method
        customer = Customer.objects.create(user=admin_user, selected_payment_method=payment_method)

        # Mock default payment method
        default_method = PaymentMethod.objects.create(name="Default", active=True, priority=1)
        mock_get_default.return_value = default_method

        response = client.post(reverse("lfs_manage_delete_payment_method", kwargs={"id": payment_method.id}))

        customer.refresh_from_db()
        assert customer.selected_payment_method == default_method

    def test_requires_authentication(self, client, payment_method):
        """Test that view requires authentication."""
        response = client.post(reverse("lfs_manage_delete_payment_method", kwargs={"id": payment_method.id}))

        assert response.status_code in [302, 403]

    def test_requires_manage_shop_permission(self, client, regular_user, payment_method):
        """Test that view requires manage_shop permission."""
        client.force_login(regular_user)

        response = client.post(reverse("lfs_manage_delete_payment_method", kwargs={"id": payment_method.id}))

        assert response.status_code == 403


class TestPaymentMethodPriceCriteriaViewIntegration:
    """Integration tests for PaymentMethodPriceCriteriaView."""

    def test_get_renders_price_criteria_page(self, client, admin_user, payment_method_price):
        """Test GET renders price criteria page."""
        client.force_login(admin_user)

        response = client.get(
            reverse("lfs_manage_payment_price_criteria", kwargs={"price_id": payment_method_price.id})
        )

        assert response.status_code == 200
        assert response.context["payment_price"] == payment_method_price
        assert "criteria" in response.context

    def test_get_with_htmx_returns_modal_template(self, client, admin_user, payment_method_price):
        """Test GET with HTMX returns modal template."""
        client.force_login(admin_user)

        response = client.get(
            reverse("lfs_manage_payment_price_criteria", kwargs={"price_id": payment_method_price.id}),
            HTTP_HX_REQUEST="true",
        )

        assert response.status_code == 200
        # Should return modal template fragment
        assert response.context["payment_price"] == payment_method_price

    def test_requires_authentication(self, client, payment_method_price):
        """Test that view requires authentication."""
        response = client.get(
            reverse("lfs_manage_payment_price_criteria", kwargs={"price_id": payment_method_price.id})
        )

        assert response.status_code in [302, 403]

    def test_requires_manage_shop_permission(self, client, regular_user, payment_method_price):
        """Test that view requires manage_shop permission."""
        client.force_login(regular_user)

        response = client.get(
            reverse("lfs_manage_payment_price_criteria", kwargs={"price_id": payment_method_price.id})
        )

        assert response.status_code == 403

    def test_get_with_nonexistent_price_returns_404(self, client, admin_user):
        """Test GET with nonexistent price returns 404."""
        client.force_login(admin_user)

        response = client.get(reverse("lfs_manage_payment_price_criteria", kwargs={"price_id": 999}))

        assert response.status_code == 404


class TestPaymentMethodPriceCriteriaSaveViewIntegration:
    """Integration tests for PaymentMethodPriceCriteriaSaveView."""

    @patch.object(PaymentMethodPrice, "save_criteria")
    def test_post_saves_criteria_and_redirects(self, mock_save_criteria, client, admin_user, payment_method_price):
        """Test POST saves criteria and redirects."""
        client.force_login(admin_user)

        response = client.post(
            reverse("lfs_manage_save_payment_price_criteria", kwargs={"price_id": payment_method_price.id}),
            data={"criteria_data": "test"},
        )

        mock_save_criteria.assert_called_once()
        assert response.status_code == 302

    @patch.object(PaymentMethodPrice, "save_criteria")
    def test_post_shows_success_message(self, mock_save_criteria, client, admin_user, payment_method_price):
        """Test POST shows success message."""
        client.force_login(admin_user)

        response = client.post(
            reverse("lfs_manage_save_payment_price_criteria", kwargs={"price_id": payment_method_price.id}),
            data={"criteria_data": "test"},
            follow=True,
        )

        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert "Criteria have been saved" in str(messages[0])

    @patch.object(PaymentMethodPrice, "save_criteria")
    def test_post_with_htmx_returns_htmx_redirect(self, mock_save_criteria, client, admin_user, payment_method_price):
        """Test POST with HTMX returns HTMX redirect."""
        client.force_login(admin_user)

        response = client.post(
            reverse("lfs_manage_save_payment_price_criteria", kwargs={"price_id": payment_method_price.id}),
            data={"criteria_data": "test"},
            HTTP_HX_REQUEST="true",
        )

        assert response.status_code == 200
        assert "HX-Redirect" in response
        expected_url = reverse(
            "lfs_manage_payment_method_prices", kwargs={"id": payment_method_price.payment_method.id}
        )
        assert expected_url in response["HX-Redirect"]

    def test_requires_authentication(self, client, payment_method_price):
        """Test that view requires authentication."""
        response = client.post(
            reverse("lfs_manage_save_payment_price_criteria", kwargs={"price_id": payment_method_price.id})
        )

        assert response.status_code in [302, 403]

    def test_requires_manage_shop_permission(self, client, regular_user, payment_method_price):
        """Test that view requires manage_shop permission."""
        client.force_login(regular_user)

        response = client.post(
            reverse("lfs_manage_save_payment_price_criteria", kwargs={"price_id": payment_method_price.id})
        )

        assert response.status_code == 403

    def test_post_with_nonexistent_price_returns_404(self, client, admin_user):
        """Test POST with nonexistent price returns 404."""
        client.force_login(admin_user)

        response = client.post(reverse("lfs_manage_save_payment_price_criteria", kwargs={"price_id": 999}))

        assert response.status_code == 404


class TestPaymentMethodViewsSearchFunctionality:
    """Integration tests for search functionality across payment method views."""

    def test_payment_method_data_view_preserves_search_in_tabs(self, client, admin_user, multiple_payment_methods):
        """Test that data view preserves search query in tab URLs."""
        client.force_login(admin_user)
        payment_method = multiple_payment_methods[0]

        response = client.get(reverse("lfs_manage_payment_method", kwargs={"id": payment_method.id}) + "?q=Method 1")

        assert response.status_code == 200
        assert response.context["search_query"] == "Method 1"

        # Check that tab URLs include search parameter
        tabs = response.context["tabs"]
        for tab_name, tab_url in tabs:
            assert "q=Method+1" in tab_url

    def test_payment_method_criteria_view_preserves_search_in_tabs(self, client, admin_user, multiple_payment_methods):
        """Test that criteria view preserves search query in tab URLs."""
        client.force_login(admin_user)
        payment_method = multiple_payment_methods[0]

        response = client.get(
            reverse("lfs_manage_payment_method_criteria", kwargs={"id": payment_method.id}) + "?q=Method 1"
        )

        assert response.status_code == 200
        assert response.context["search_query"] == "Method 1"

    def test_payment_method_prices_view_preserves_search_in_tabs(self, client, admin_user, multiple_payment_methods):
        """Test that prices view preserves search query in tab URLs."""
        client.force_login(admin_user)
        payment_method = multiple_payment_methods[0]

        response = client.get(
            reverse("lfs_manage_payment_method_prices", kwargs={"id": payment_method.id}) + "?q=Method 1"
        )

        assert response.status_code == 200
        assert response.context["search_query"] == "Method 1"

    def test_search_functionality_filters_payment_methods_list(self, client, admin_user, multiple_payment_methods):
        """Test that search functionality filters payment methods in sidebar."""
        client.force_login(admin_user)
        payment_method = multiple_payment_methods[1]  # "Payment Method 2"

        response = client.get(reverse("lfs_manage_payment_method", kwargs={"id": payment_method.id}) + "?q=Method 2")

        assert response.status_code == 200
        payment_methods = response.context["payment_methods"]
        payment_method_names = list(payment_methods.values_list("name", flat=True))

        assert payment_method_names == ["Payment Method 2"]
