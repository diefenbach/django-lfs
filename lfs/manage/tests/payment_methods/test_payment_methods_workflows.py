"""
Comprehensive end-to-end workflow tests for payment method management.

Following TDD principles:
- Test complete user workflows from start to finish
- Test realistic user scenarios and use cases
- Test integration between different views and components
- Clear test names describing the workflow being tested
- Arrange-Act-Assert structure
- Test both happy paths and error scenarios

Workflows covered:
- Complete payment method creation and configuration workflow
- Payment method editing and updating workflow
- Payment method deletion workflow with customer updates
- Price management workflow (add, edit, delete prices)
- Criteria configuration workflow
- Search and navigation workflow
- Bulk operations workflow
- Error recovery workflow
"""

import pytest
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
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


class TestPaymentMethodCreationWorkflow:
    """Test complete payment method creation workflow."""

    def test_complete_payment_method_creation_workflow(self, client, admin_user):
        """Test complete workflow from creation to full configuration."""
        client.force_login(admin_user)

        # Step 1: Navigate to payment methods (should redirect to no methods page)
        response = client.get(reverse("lfs_manage_payment_methods"))
        assert response.status_code == 302
        assert response.url == reverse("lfs_manage_no_payment_methods")

        # Step 2: Visit no payment methods page
        response = client.get(reverse("lfs_manage_no_payment_methods"))
        assert response.status_code == 200

        # Step 3: Create new payment method
        response = client.post(reverse("lfs_manage_add_payment_method"), data={"name": "Credit Card"})
        assert response.status_code == 302

        payment_method = PaymentMethod.objects.get(name="Credit Card")
        assert response.url == reverse("lfs_manage_payment_method", kwargs={"id": payment_method.id})

        # Step 4: Configure payment method data
        response = client.post(
            reverse("lfs_manage_payment_method", kwargs={"id": payment_method.id}),
            data={
                "name": "Credit Card Payment",
                "description": "Accept credit card payments",
                "active": True,
                "price": "5.00",
                "type": 0,
            },
        )
        assert response.status_code == 302

        payment_method.refresh_from_db()
        assert payment_method.name == "Credit Card Payment"
        assert payment_method.description == "Accept credit card payments"
        assert payment_method.active is True

        # Step 5: Add prices
        response = client.post(
            reverse("lfs_manage_payment_method_prices", kwargs={"id": payment_method.id}),
            data={"add_price": "true", "price": "2.50"},
        )
        assert response.status_code == 302
        assert payment_method.prices.filter(price=Decimal("2.50")).exists()

        # Step 6: Add another price
        response = client.post(
            reverse("lfs_manage_payment_method_prices", kwargs={"id": payment_method.id}),
            data={"add_price": "true", "price": "5.00"},
        )
        assert response.status_code == 302
        assert payment_method.prices.filter(price=Decimal("5.00")).exists()

        # Step 7: Configure criteria (mock save_criteria)
        with patch.object(PaymentMethod, "save_criteria") as mock_save_criteria:
            response = client.post(
                reverse("lfs_manage_payment_method_criteria", kwargs={"id": payment_method.id}),
                data={"criteria_data": "test"},
            )
            assert response.status_code == 302
            mock_save_criteria.assert_called_once()

        # Step 8: Verify final state
        response = client.get(reverse("lfs_manage_payment_method", kwargs={"id": payment_method.id}))
        assert response.status_code == 200
        assert response.context["payment_method"] == payment_method
        assert response.context["active_tab"] == "data"

        # Verify prices tab
        response = client.get(reverse("lfs_manage_payment_method_prices", kwargs={"id": payment_method.id}))
        assert response.status_code == 200
        assert response.context["prices"].count() == 2

    def test_payment_method_creation_with_validation_errors_workflow(self, client, admin_user):
        """Test creation workflow with validation errors and recovery."""
        client.force_login(admin_user)

        # Step 1: Try to create payment method with empty name
        response = client.post(reverse("lfs_manage_add_payment_method"), data={"name": ""})
        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["form"].errors

        # Step 2: Correct the error and create successfully
        response = client.post(reverse("lfs_manage_add_payment_method"), data={"name": "Valid Payment Method"})
        assert response.status_code == 302

        payment_method = PaymentMethod.objects.get(name="Valid Payment Method")

        # Step 3: Try to update with invalid data
        response = client.post(
            reverse("lfs_manage_payment_method", kwargs={"id": payment_method.id}),
            data={
                "name": "",  # Empty name should cause validation error
                "description": "Valid description",
                "active": True,
                "price": "5.00",
                "type": 0,
            },
        )
        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["form"].errors

        # Step 4: Correct the error and update successfully
        response = client.post(
            reverse("lfs_manage_payment_method", kwargs={"id": payment_method.id}),
            data={
                "name": "Corrected Payment Method",
                "description": "Valid description",
                "active": True,
                "price": "5.00",
                "type": 0,
            },
        )
        assert response.status_code == 302

        payment_method.refresh_from_db()
        assert payment_method.name == "Corrected Payment Method"

    def test_payment_method_creation_cancellation_workflow(self, client, admin_user):
        """Test workflow when user cancels creation process."""
        client.force_login(admin_user)

        # Step 1: Start creation but don't submit
        response = client.get(reverse("lfs_manage_add_payment_method"))
        assert response.status_code == 200

        # Step 2: Navigate away without creating (simulate cancel)
        response = client.get(reverse("lfs_manage_no_payment_methods"))
        assert response.status_code == 200

        # Step 3: Verify no payment method was created
        assert PaymentMethod.objects.count() == 0

        # Step 4: Create payment method properly
        response = client.post(reverse("lfs_manage_add_payment_method"), data={"name": "Actual Payment Method"})
        assert response.status_code == 302
        assert PaymentMethod.objects.count() == 1


class TestPaymentMethodEditingWorkflow:
    """Test complete payment method editing workflow."""

    def test_complete_payment_method_editing_workflow(self, client, admin_user, payment_method_with_prices):
        """Test complete editing workflow across all tabs."""
        client.force_login(admin_user)

        # Step 1: Navigate to payment method
        response = client.get(reverse("lfs_manage_payment_methods"))
        assert response.status_code == 302
        assert response.url == reverse("lfs_manage_payment_method", kwargs={"id": payment_method_with_prices.id})

        # Step 2: Edit data tab
        response = client.post(
            reverse("lfs_manage_payment_method", kwargs={"id": payment_method_with_prices.id}),
            data={
                "name": "Updated Payment Method",
                "description": "Updated description",
                "active": False,
                "price": "5.00",
                "type": 0,
            },
        )
        assert response.status_code == 302

        payment_method_with_prices.refresh_from_db()
        assert payment_method_with_prices.name == "Updated Payment Method"
        assert payment_method_with_prices.active is False

        # Step 3: Navigate to prices tab
        response = client.get(reverse("lfs_manage_payment_method_prices", kwargs={"id": payment_method_with_prices.id}))
        assert response.status_code == 200
        assert response.context["active_tab"] == "prices"

        # Step 4: Update existing prices
        prices = payment_method_with_prices.prices.all()
        price1, price2 = prices[0], prices[1]

        response = client.post(
            reverse("lfs_manage_payment_method_prices", kwargs={"id": payment_method_with_prices.id}),
            data={
                "action": "update",
                f"price-{price1.id}": "15.00",
                f"priority-{price1.id}": "5",
                f"price-{price2.id}": "25.00",
                f"priority-{price2.id}": "10",
            },
        )
        assert response.status_code == 302

        price1.refresh_from_db()
        price2.refresh_from_db()
        assert price1.price == Decimal("15.00")
        assert price2.price == Decimal("25.00")

        # Step 5: Delete one price
        response = client.post(
            reverse("lfs_manage_payment_method_prices", kwargs={"id": payment_method_with_prices.id}),
            data={"action": "delete", f"delete-{price2.id}": "true"},
        )
        assert response.status_code == 302
        assert not PaymentMethodPrice.objects.filter(id=price2.id).exists()

        # Step 6: Add new price
        response = client.post(
            reverse("lfs_manage_payment_method_prices", kwargs={"id": payment_method_with_prices.id}),
            data={"add_price": "true", "price": "7.50"},
        )
        assert response.status_code == 302
        assert payment_method_with_prices.prices.filter(price=Decimal("7.50")).exists()

        # Step 7: Navigate to criteria tab
        response = client.get(
            reverse("lfs_manage_payment_method_criteria", kwargs={"id": payment_method_with_prices.id})
        )
        assert response.status_code == 200
        assert response.context["active_tab"] == "criteria"

        # Step 8: Update criteria
        with patch.object(PaymentMethod, "save_criteria") as mock_save_criteria:
            response = client.post(
                reverse("lfs_manage_payment_method_criteria", kwargs={"id": payment_method_with_prices.id}),
                data={"criteria_data": "updated_criteria"},
            )
            assert response.status_code == 302
            mock_save_criteria.assert_called_once()

        # Step 9: Verify final state
        assert payment_method_with_prices.prices.count() == 2  # One deleted, one added
        remaining_prices = list(payment_method_with_prices.prices.values_list("price", flat=True))
        assert Decimal("15.00") in remaining_prices
        assert Decimal("7.50") in remaining_prices

    def test_payment_method_editing_with_search_workflow(self, client, admin_user, multiple_payment_methods):
        """Test editing workflow with search functionality."""
        client.force_login(admin_user)

        target_method = multiple_payment_methods[1]  # "Payment Method 2"

        # Step 1: Navigate with search
        response = client.get(reverse("lfs_manage_payment_methods") + "?q=Method 2")
        assert response.status_code == 302

        # Step 2: Should redirect to first matching method
        response = client.get(reverse("lfs_manage_payment_method", kwargs={"id": target_method.id}) + "?q=Method 2")
        assert response.status_code == 200
        assert response.context["search_query"] == "Method 2"

        # Step 3: Verify search is preserved in tab URLs
        tabs = response.context["tabs"]
        for tab_name, tab_url in tabs:
            assert "q=Method+2" in tab_url

        # Step 4: Navigate to prices tab with search preserved
        response = client.get(
            reverse("lfs_manage_payment_method_prices", kwargs={"id": target_method.id}) + "?q=Method 2"
        )
        assert response.status_code == 200
        assert response.context["search_query"] == "Method 2"

        # Step 5: Edit while maintaining search context
        response = client.post(
            reverse("lfs_manage_payment_method", kwargs={"id": target_method.id}) + "?q=Method 2",
            data={
                "name": "Updated Method 2",
                "description": "Updated description",
                "active": True,
                "price": "5.00",
                "type": 0,
            },
        )
        assert response.status_code == 302

        target_method.refresh_from_db()
        assert target_method.name == "Updated Method 2"

    @pytest.mark.slow
    def test_concurrent_editing_workflow(self, client, admin_user, payment_method):
        """Test workflow when multiple users edit the same payment method."""
        client.force_login(admin_user)

        # Create second admin user
        admin_user2 = User.objects.create_user(
            username="admin2", email="admin2@example.com", password="testpass123", is_staff=True, is_superuser=True
        )
        client2 = Client()
        client2.force_login(admin_user2)

        # Step 1: Both users load the same payment method
        response1 = client.get(reverse("lfs_manage_payment_method", kwargs={"id": payment_method.id}))
        response2 = client2.get(reverse("lfs_manage_payment_method", kwargs={"id": payment_method.id}))

        assert response1.status_code == 200
        assert response2.status_code == 200

        # Step 2: First user updates the payment method
        response1 = client.post(
            reverse("lfs_manage_payment_method", kwargs={"id": payment_method.id}),
            data={
                "name": "Updated by User 1",
                "description": "Description by User 1",
                "active": True,
                "price": "5.00",
                "type": 0,
            },
        )
        assert response1.status_code == 302

        # Step 3: Second user updates the payment method (should overwrite)
        response2 = client2.post(
            reverse("lfs_manage_payment_method", kwargs={"id": payment_method.id}),
            data={
                "name": "Updated by User 2",
                "description": "Description by User 2",
                "active": False,
                "price": "5.00",
                "type": 0,
            },
        )
        assert response2.status_code == 302

        # Step 4: Verify last write wins
        payment_method.refresh_from_db()
        assert payment_method.name == "Updated by User 2"
        assert payment_method.description == "Description by User 2"
        assert payment_method.active is False


class TestPaymentMethodDeletionWorkflow:
    """Test complete payment method deletion workflow."""

    @pytest.mark.slow
    @patch("lfs.manage.payment_methods.views.payment_utils.get_default_payment_method")
    def test_complete_payment_method_deletion_workflow(self, mock_get_default, client, admin_user, payment_method):
        """Test complete deletion workflow with customer updates."""
        client.force_login(admin_user)

        # Step 1: Create customers using this payment method
        customers = []
        for i in range(3):
            user = User.objects.create_user(
                username=f"customer{i}", email=f"customer{i}@example.com", password="testpass123"
            )
            customer = Customer.objects.create(user=user, selected_payment_method=payment_method)
            customers.append(customer)

        # Step 2: Create default payment method
        default_method = PaymentMethod.objects.create(name="Default Method", active=True, priority=1, price=0.0, type=0)
        mock_get_default.return_value = default_method

        # Step 3: Navigate to delete confirmation
        response = client.get(reverse("lfs_manage_delete_payment_method_confirm", kwargs={"id": payment_method.id}))
        assert response.status_code == 200
        assert response.context["payment_method"] == payment_method

        # Step 4: Perform deletion
        payment_method_id = payment_method.id
        response = client.get(reverse("lfs_manage_delete_payment_method", kwargs={"id": payment_method_id}))
        assert response.status_code == 302
        assert response.url == reverse("lfs_manage_payment_methods")

        # Step 5: Verify payment method is deleted
        assert not PaymentMethod.objects.filter(id=payment_method_id).exists()

        # Step 6: Verify customers are updated
        for customer in customers:
            customer.refresh_from_db()
            assert customer.selected_payment_method == default_method

        # Step 7: Verify redirect to no payment methods page (since only default remains)
        response = client.get(reverse("lfs_manage_payment_methods"))
        assert response.status_code == 302
        expected_url = reverse("lfs_manage_payment_method", kwargs={"id": default_method.id})
        assert response.url == expected_url

    @pytest.mark.slow
    def test_payment_method_deletion_cancellation_workflow(self, client, admin_user, payment_method):
        """Test deletion workflow when user cancels."""
        client.force_login(admin_user)

        # Step 1: Navigate to delete confirmation
        response = client.get(reverse("lfs_manage_delete_payment_method_confirm", kwargs={"id": payment_method.id}))
        assert response.status_code == 200

        # Step 2: Cancel by navigating away instead of posting
        response = client.get(reverse("lfs_manage_payment_method", kwargs={"id": payment_method.id}))
        assert response.status_code == 200

        # Step 3: Verify payment method still exists
        assert PaymentMethod.objects.filter(id=payment_method.id).exists()

        # Step 4: Verify payment method is still functional
        response = client.post(
            reverse("lfs_manage_payment_method", kwargs={"id": payment_method.id}),
            data={
                "name": "Still Exists",
                "description": "Not deleted",
                "active": True,
                "price": "5.00",
                "type": 0,
            },
        )
        assert response.status_code == 302

        payment_method.refresh_from_db()
        assert payment_method.name == "Still Exists"

    def test_last_payment_method_deletion_workflow(self, client, admin_user, payment_method):
        """Test deletion workflow for the last remaining payment method."""
        client.force_login(admin_user)

        # Step 1: Verify this is the only payment method
        assert PaymentMethod.objects.count() == 1

        # Step 2: Create default method for customer updates
        default_method = PaymentMethod.objects.create(name="Default Method", active=True, priority=1)

        with patch("lfs.payment.utils.get_default_payment_method", return_value=default_method):
            # Step 3: Delete the original payment method
            response = client.post(reverse("lfs_manage_delete_payment_method", kwargs={"id": payment_method.id}))
            assert response.status_code == 302

        # Step 4: Should redirect to payment methods list
        response = client.get(reverse("lfs_manage_payment_methods"))
        assert response.status_code == 302

        # Step 5: Should redirect to the remaining default method
        expected_url = reverse("lfs_manage_payment_method", kwargs={"id": default_method.id})
        assert response.url == expected_url


class TestPriceManagementWorkflow:
    """Test complete price management workflow."""

    def test_complete_price_management_workflow(self, client, admin_user, payment_method):
        """Test complete price management from creation to deletion."""
        client.force_login(admin_user)

        # Step 1: Navigate to prices tab
        response = client.get(reverse("lfs_manage_payment_method_prices", kwargs={"id": payment_method.id}))
        assert response.status_code == 200
        assert response.context["prices"].count() == 0

        # Step 2: Add first price
        response = client.post(
            reverse("lfs_manage_payment_method_prices", kwargs={"id": payment_method.id}),
            data={"add_price": "true", "price": "5.00"},
        )
        assert response.status_code == 302

        # Step 3: Add second price
        response = client.post(
            reverse("lfs_manage_payment_method_prices", kwargs={"id": payment_method.id}),
            data={"add_price": "true", "price": "10.00"},
        )
        assert response.status_code == 302

        # Step 4: Add third price
        response = client.post(
            reverse("lfs_manage_payment_method_prices", kwargs={"id": payment_method.id}),
            data={"add_price": "true", "price": "15.00"},
        )
        assert response.status_code == 302

        # Step 5: Verify all prices exist
        response = client.get(reverse("lfs_manage_payment_method_prices", kwargs={"id": payment_method.id}))
        assert response.status_code == 200
        assert response.context["prices"].count() == 3

        prices = list(response.context["prices"])
        price_values = [price.price for price in prices]
        assert Decimal("5.00") in price_values
        assert Decimal("10.00") in price_values
        assert Decimal("15.00") in price_values

        # Step 6: Update prices
        response = client.post(
            reverse("lfs_manage_payment_method_prices", kwargs={"id": payment_method.id}),
            data={
                "action": "update",
                f"price-{prices[0].id}": "7.50",
                f"priority-{prices[0].id}": "5",
                f"price-{prices[1].id}": "12.50",
                f"priority-{prices[1].id}": "10",
                f"price-{prices[2].id}": "17.50",
                f"priority-{prices[2].id}": "15",
            },
        )
        assert response.status_code == 302

        # Step 7: Verify updates
        for price in prices:
            price.refresh_from_db()

        updated_values = [price.price for price in prices]
        assert Decimal("7.50") in updated_values
        assert Decimal("12.50") in updated_values
        assert Decimal("17.50") in updated_values

        # Step 8: Delete middle price
        response = client.post(
            reverse("lfs_manage_payment_method_prices", kwargs={"id": payment_method.id}),
            data={"action": "delete", f"delete-{prices[1].id}": "true"},
        )
        assert response.status_code == 302

        # Step 9: Verify deletion
        assert not PaymentMethodPrice.objects.filter(id=prices[1].id).exists()
        assert payment_method.prices.count() == 2

        # Step 10: Configure criteria for remaining prices
        remaining_prices = list(payment_method.prices.all())

        for price in remaining_prices:
            with patch.object(PaymentMethodPrice, "save_criteria") as mock_save_criteria:
                response = client.post(
                    reverse("lfs_manage_save_payment_price_criteria", kwargs={"price_id": price.id}),
                    data={"criteria_data": f"criteria_for_price_{price.id}"},
                )
                assert response.status_code == 302
                mock_save_criteria.assert_called_once()

    def test_bulk_price_operations_workflow(self, client, admin_user, payment_method):
        """Test bulk operations on multiple prices."""
        client.force_login(admin_user)

        # Step 1: Create multiple prices
        prices = []
        for i in range(5):
            response = client.post(
                reverse("lfs_manage_payment_method_prices", kwargs={"id": payment_method.id}),
                data={"add_price": "true", "price": f"{(i+1)*5}.00"},
            )
            assert response.status_code == 302

        # Step 2: Get all prices
        prices = list(payment_method.prices.all())
        assert len(prices) == 5

        # Step 3: Update all prices at once
        update_data = {"action": "update"}
        for i, price in enumerate(prices):
            update_data[f"price-{price.id}"] = f"{(i+1)*10}.00"
            update_data[f"priority-{price.id}"] = str((i + 1) * 10)

        response = client.post(
            reverse("lfs_manage_payment_method_prices", kwargs={"id": payment_method.id}), data=update_data
        )
        assert response.status_code == 302

        # Step 4: Verify all updates
        for price in prices:
            price.refresh_from_db()

        updated_values = [price.price for price in prices]
        expected_values = [Decimal(f"{(i+1)*10}.00") for i in range(5)]
        for expected in expected_values:
            assert expected in updated_values

        # Step 5: Delete multiple prices at once
        delete_data = {"action": "delete"}
        # Delete first, third, and fifth prices
        for i in [0, 2, 4]:
            delete_data[f"delete-{prices[i].id}"] = "true"

        response = client.post(
            reverse("lfs_manage_payment_method_prices", kwargs={"id": payment_method.id}), data=delete_data
        )
        assert response.status_code == 302

        # Step 6: Verify deletions
        assert payment_method.prices.count() == 2
        remaining_ids = list(payment_method.prices.values_list("id", flat=True))
        assert prices[1].id in remaining_ids
        assert prices[3].id in remaining_ids

    def test_price_criteria_workflow(self, client, admin_user, payment_method_price):
        """Test complete price criteria configuration workflow."""
        client.force_login(admin_user)

        # Step 1: Navigate to price criteria
        response = client.get(
            reverse("lfs_manage_payment_price_criteria", kwargs={"price_id": payment_method_price.id})
        )
        assert response.status_code == 200
        assert response.context["payment_price"] == payment_method_price

        # Step 2: Test HTMX modal request
        response = client.get(
            reverse("lfs_manage_payment_price_criteria", kwargs={"price_id": payment_method_price.id}),
            HTTP_HX_REQUEST="true",
        )
        assert response.status_code == 200

        # Step 3: Save criteria
        with patch.object(PaymentMethodPrice, "save_criteria") as mock_save_criteria:
            response = client.post(
                reverse("lfs_manage_save_payment_price_criteria", kwargs={"price_id": payment_method_price.id}),
                data={"criteria_data": "test_criteria"},
            )
            assert response.status_code == 302
            mock_save_criteria.assert_called_once()

        # Step 4: Save criteria via HTMX
        with patch.object(PaymentMethodPrice, "save_criteria") as mock_save_criteria:
            response = client.post(
                reverse("lfs_manage_save_payment_price_criteria", kwargs={"price_id": payment_method_price.id}),
                data={"criteria_data": "htmx_criteria"},
                HTTP_HX_REQUEST="true",
            )
            assert response.status_code == 200
            assert "HX-Redirect" in response
            mock_save_criteria.assert_called_once()

        # Step 5: Navigate back to prices tab
        response = client.get(
            reverse("lfs_manage_payment_method_prices", kwargs={"id": payment_method_price.payment_method.id})
        )
        assert response.status_code == 200
        assert payment_method_price in response.context["prices"]


class TestSearchAndNavigationWorkflow:
    """Test complete search and navigation workflow."""

    def test_complete_search_workflow(self, client, admin_user, multiple_payment_methods):
        """Test complete search and navigation workflow."""
        client.force_login(admin_user)

        # Step 1: Navigate to payment methods (should redirect to first method)
        response = client.get(reverse("lfs_manage_payment_methods"))
        assert response.status_code == 302
        first_method = multiple_payment_methods[0]
        expected_url = reverse("lfs_manage_payment_method", kwargs={"id": first_method.id})
        assert response.url == expected_url

        # Step 2: Search for specific payment method
        target_method = multiple_payment_methods[1]  # "Payment Method 2"
        response = client.get(reverse("lfs_manage_payment_method", kwargs={"id": target_method.id}) + "?q=Method 2")
        assert response.status_code == 200
        assert response.context["search_query"] == "Method 2"

        # Step 3: Verify search filters sidebar
        filtered_methods = response.context["payment_methods"]
        method_names = list(filtered_methods.values_list("name", flat=True))
        assert method_names == ["Payment Method 2"]

        # Step 4: Navigate between tabs while preserving search
        tabs = response.context["tabs"]
        criteria_tab_url = None
        prices_tab_url = None

        for tab_name, tab_url in tabs:
            if tab_name == "criteria":
                criteria_tab_url = tab_url
            elif tab_name == "prices":
                prices_tab_url = tab_url

        # Step 5: Navigate to criteria tab with search
        response = client.get(criteria_tab_url)
        assert response.status_code == 200
        assert response.context["search_query"] == "Method 2"
        assert response.context["active_tab"] == "criteria"

        # Step 6: Navigate to prices tab with search
        response = client.get(prices_tab_url)
        assert response.status_code == 200
        assert response.context["search_query"] == "Method 2"
        assert response.context["active_tab"] == "prices"

        # Step 7: Clear search by navigating without query
        response = client.get(reverse("lfs_manage_payment_method", kwargs={"id": target_method.id}))
        assert response.status_code == 200
        assert response.context["search_query"] == ""

        # Step 8: Verify all methods are shown again
        all_methods = response.context["payment_methods"]
        assert all_methods.count() == 3

    def test_search_with_no_results_workflow(self, client, admin_user, multiple_payment_methods):
        """Test search workflow when no results are found."""
        client.force_login(admin_user)

        # Step 1: Search for non-existent payment method
        first_method = multiple_payment_methods[0]
        response = client.get(reverse("lfs_manage_payment_method", kwargs={"id": first_method.id}) + "?q=NonExistent")
        assert response.status_code == 200
        assert response.context["search_query"] == "NonExistent"

        # Step 2: Verify no methods in sidebar
        filtered_methods = response.context["payment_methods"]
        assert filtered_methods.count() == 0

        # Step 3: Current method should still be displayed
        assert response.context["payment_method"] == first_method

        # Step 4: Navigate to different method and search again
        second_method = multiple_payment_methods[1]
        response = client.get(reverse("lfs_manage_payment_method", kwargs={"id": second_method.id}) + "?q=NonExistent")
        assert response.status_code == 200
        assert response.context["payment_method"] == second_method
        assert response.context["payment_methods"].count() == 0

    def test_navigation_workflow_across_all_views(self, client, admin_user, payment_method_with_prices):
        """Test navigation workflow across all payment method views."""
        client.force_login(admin_user)

        # Step 1: Start at main payment methods view
        response = client.get(reverse("lfs_manage_payment_methods"))
        assert response.status_code == 302

        # Step 2: Navigate to data tab
        response = client.get(reverse("lfs_manage_payment_method", kwargs={"id": payment_method_with_prices.id}))
        assert response.status_code == 200
        assert response.context["active_tab"] == "data"

        # Step 3: Navigate to criteria tab
        response = client.get(
            reverse("lfs_manage_payment_method_criteria", kwargs={"id": payment_method_with_prices.id})
        )
        assert response.status_code == 200
        assert response.context["active_tab"] == "criteria"

        # Step 4: Navigate to prices tab
        response = client.get(reverse("lfs_manage_payment_method_prices", kwargs={"id": payment_method_with_prices.id}))
        assert response.status_code == 200
        assert response.context["active_tab"] == "prices"

        # Step 5: Navigate to price criteria
        price = payment_method_with_prices.prices.first()
        response = client.get(reverse("lfs_manage_payment_price_criteria", kwargs={"price_id": price.id}))
        assert response.status_code == 200
        assert response.context["payment_price"] == price

        # Step 6: Navigate to delete confirmation
        response = client.get(
            reverse("lfs_manage_delete_payment_method_confirm", kwargs={"id": payment_method_with_prices.id})
        )
        assert response.status_code == 200
        assert response.context["payment_method"] == payment_method_with_prices

        # Step 7: Navigate back without deleting
        response = client.get(reverse("lfs_manage_payment_method", kwargs={"id": payment_method_with_prices.id}))
        assert response.status_code == 200

        # Step 8: Navigate to add new payment method
        response = client.get(reverse("lfs_manage_add_payment_method"))
        assert response.status_code == 200

        # Step 9: Navigate back to existing method
        response = client.get(reverse("lfs_manage_payment_method", kwargs={"id": payment_method_with_prices.id}))
        assert response.status_code == 200


class TestErrorRecoveryWorkflow:
    """Test error recovery workflows."""

    def test_form_validation_error_recovery_workflow(self, client, admin_user, payment_method):
        """Test recovery from form validation errors."""
        client.force_login(admin_user)

        # Step 1: Submit invalid form data
        response = client.post(
            reverse("lfs_manage_payment_method", kwargs={"id": payment_method.id}),
            data={
                "name": "",  # Invalid: empty name
                "description": "Valid description",
                "active": True,
                "price": "5.00",
                "type": 0,
            },
        )
        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["form"].errors

        # Step 2: Verify form shows previous values (except invalid ones)
        form = response.context["form"]
        assert form.data["description"] == "Valid description"
        assert form.data["active"] == "True"

        # Step 3: Correct the error and resubmit
        response = client.post(
            reverse("lfs_manage_payment_method", kwargs={"id": payment_method.id}),
            data={
                "name": "Corrected Name",
                "description": "Valid description",
                "active": True,
                "price": "5.00",
                "type": 0,
            },
        )
        assert response.status_code == 302

        # Step 4: Verify successful update
        payment_method.refresh_from_db()
        assert payment_method.name == "Corrected Name"
        assert payment_method.description == "Valid description"

    def test_network_interruption_recovery_workflow(self, client, admin_user, payment_method):
        """Test recovery workflow after simulated network interruption."""
        client.force_login(admin_user)

        # Step 1: Start editing payment method
        response = client.get(reverse("lfs_manage_payment_method", kwargs={"id": payment_method.id}))
        assert response.status_code == 200

        # Step 2: Simulate network interruption by making changes and then reloading
        # (In real scenario, user would lose unsaved changes)

        # Step 3: Reload page to simulate recovery
        response = client.get(reverse("lfs_manage_payment_method", kwargs={"id": payment_method.id}))
        assert response.status_code == 200

        # Step 4: Verify form shows current database values
        form = response.context["form"]
        assert form.initial["name"] == payment_method.name
        assert form.initial["description"] == payment_method.description

        # Step 5: Complete the editing process
        response = client.post(
            reverse("lfs_manage_payment_method", kwargs={"id": payment_method.id}),
            data={
                "name": "Recovered Edit",
                "description": "After recovery",
                "active": True,
                "price": "5.00",
                "type": 0,
            },
        )
        assert response.status_code == 302

        payment_method.refresh_from_db()
        assert payment_method.name == "Recovered Edit"

    def test_permission_error_recovery_workflow(self, client, regular_user, admin_user, payment_method):
        """Test recovery workflow after permission errors."""
        # Step 1: Try to access with regular user (should fail)
        client.force_login(regular_user)
        response = client.get(reverse("lfs_manage_payment_method", kwargs={"id": payment_method.id}))
        assert response.status_code == 403

        # Step 2: Login with proper permissions
        client.force_login(admin_user)

        # Step 3: Access should now work
        response = client.get(reverse("lfs_manage_payment_method", kwargs={"id": payment_method.id}))
        assert response.status_code == 200

        # Step 4: Complete normal workflow
        response = client.post(
            reverse("lfs_manage_payment_method", kwargs={"id": payment_method.id}),
            data={
                "name": "After Permission Fix",
                "description": "Now authorized",
                "active": True,
                "price": "5.00",
                "type": 0,
            },
        )
        assert response.status_code == 302

        payment_method.refresh_from_db()
        assert payment_method.name == "After Permission Fix"
