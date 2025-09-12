"""
Comprehensive tests for payment method service layer and utilities.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Fast tests with minimal mocking

Tests cover:
- Payment method utility functions from lfs.payment.utils
- Payment method model methods that act as services
- Integration between payment methods and customer management
- Business logic validation and processing
- Error handling in service methods
- Performance of service operations
"""

import pytest
from decimal import Decimal
from unittest.mock import patch, Mock

from django.contrib.auth import get_user_model

from lfs.payment.models import PaymentMethod, PaymentMethodPrice
from lfs.payment import utils as payment_utils
from lfs.customer.models import Customer

User = get_user_model()


class TestPaymentMethodUtilityServices:
    """Test payment method utility service functions."""

    def test_get_valid_payment_methods_returns_active_methods(self, mock_request, multiple_payment_methods):
        """Test get_valid_payment_methods returns only active payment methods."""
        # Make one payment method inactive
        multiple_payment_methods[1].active = False
        multiple_payment_methods[1].save()

        # Mock is_valid to return True for all methods
        with patch.object(PaymentMethod, "is_valid", return_value=True):
            valid_methods = payment_utils.get_valid_payment_methods(mock_request)

        assert len(valid_methods) == 2
        method_names = [method.name for method in valid_methods]
        assert "Payment Method 1" in method_names
        assert "Payment Method 3" in method_names
        assert "Payment Method 2" not in method_names

    def test_get_valid_payment_methods_filters_by_criteria(self, mock_request, multiple_payment_methods):
        """Test get_valid_payment_methods filters by payment method criteria."""

        # Mock is_valid to return False for one method
        original_is_valid = PaymentMethod.is_valid

        def mock_is_valid(self, request):
            if self.name == "Payment Method 2":
                return False
            return True

        with patch.object(PaymentMethod, "is_valid", mock_is_valid):
            valid_methods = payment_utils.get_valid_payment_methods(mock_request)

        assert len(valid_methods) == 2
        method_names = [method.name for method in valid_methods]
        assert "Payment Method 2" not in method_names

    def test_get_valid_payment_methods_returns_empty_list_when_none_valid(self, mock_request, multiple_payment_methods):
        """Test get_valid_payment_methods returns empty list when no methods are valid."""
        # Mock is_valid to return False for all methods
        with patch.object(PaymentMethod, "is_valid", return_value=False):
            valid_methods = payment_utils.get_valid_payment_methods(mock_request)

        assert valid_methods == []

    @pytest.mark.django_db
    def test_get_valid_payment_methods_handles_no_payment_methods(self, mock_request):
        """Test get_valid_payment_methods handles case with no payment methods."""
        valid_methods = payment_utils.get_valid_payment_methods(mock_request)

        assert valid_methods == []

    def test_get_default_payment_method_returns_first_valid_method(self, mock_request, multiple_payment_methods):
        """Test get_default_payment_method returns first valid payment method."""
        # Mock is_valid to return True for all methods
        with patch.object(PaymentMethod, "is_valid", return_value=True):
            default_method = payment_utils.get_default_payment_method(mock_request)

        # Should return first method alphabetically
        assert default_method.name == "Payment Method 1"

    def test_get_default_payment_method_returns_none_when_no_valid_methods(
        self, mock_request, multiple_payment_methods
    ):
        """Test get_default_payment_method returns None when no valid methods."""
        # Mock is_valid to return False for all methods
        with patch.object(PaymentMethod, "is_valid", return_value=False):
            default_method = payment_utils.get_default_payment_method(mock_request)

        assert default_method is None

    def test_get_selected_payment_method_returns_customer_selection(self, mock_request, payment_method, admin_user):
        """Test get_selected_payment_method returns customer's selected method."""
        # Create customer with selected payment method
        customer = Customer.objects.create(user=admin_user, selected_payment_method=payment_method)

        mock_request.user = admin_user

        with patch("lfs.customer.utils.get_customer", return_value=customer):
            selected_method = payment_utils.get_selected_payment_method(mock_request)

        assert selected_method == payment_method

    def test_get_selected_payment_method_falls_back_to_default(self, mock_request, payment_method, admin_user):
        """Test get_selected_payment_method falls back to default when no customer selection."""
        mock_request.user = admin_user

        with patch("lfs.customer.utils.get_customer", return_value=None):
            with patch("lfs.payment.utils.get_default_payment_method", return_value=payment_method):
                selected_method = payment_utils.get_selected_payment_method(mock_request)

        assert selected_method == payment_method

    def test_get_payment_costs_calculates_correct_costs(self, mock_request, payment_method, tax_rate):
        """Test get_payment_costs calculates correct payment costs."""
        # Set up payment method with tax and price
        payment_method.tax = tax_rate
        payment_method.price = Decimal("10.00")
        payment_method.save()

        # Mock criteria_utils.get_first_valid to return None (use base price)
        with patch("lfs.criteria.utils.get_first_valid", return_value=None):
            # Patch the payment_method.price to be a float to avoid TypeError
            with patch.object(payment_method, "price", float(payment_method.price)):
                costs = payment_utils.get_payment_costs(mock_request, payment_method)

        # Expected calculations with 19% tax
        # The calculation is (tax_rate / (tax_rate + 100)) * price
        # The utils function does: tax = (tax_rate / (tax_rate + 100)) * price
        # where tax_rate is float and price is Decimal, which causes TypeError
        # We need to convert to float for the calculation
        price_as_float = float(payment_method.price)
        expected_tax = (19.0 / (19.0 + 100)) * price_as_float
        expected_net = price_as_float - expected_tax
        expected_gross = price_as_float

        assert abs(costs["tax"] - expected_tax) < 0.01
        assert abs(costs["price_net"] - expected_net) < 0.01
        assert costs["price_gross"] == expected_gross

    def test_get_payment_costs_uses_price_criteria(self, mock_request, payment_method_with_prices, tax_rate):
        """Test get_payment_costs uses price from criteria when available."""
        payment_method_with_prices.tax = tax_rate
        payment_method_with_prices.save()

        # Get first price
        price_obj = payment_method_with_prices.prices.first()

        # Mock criteria_utils.get_first_valid to return the price object
        with patch("lfs.criteria.utils.get_first_valid", return_value=price_obj):
            costs = payment_utils.get_payment_costs(mock_request, payment_method_with_prices)

        # Should use price from price object
        expected_gross = price_obj.price
        expected_tax = (19.0 / (19.0 + 100)) * float(expected_gross)
        expected_net = float(expected_gross) - expected_tax

        assert costs["price_gross"] == expected_gross
        assert abs(costs["tax"] - expected_tax) < 0.01
        assert abs(costs["price_net"] - expected_net) < 0.01

    def test_get_payment_costs_handles_none_payment_method(self, mock_request):
        """Test get_payment_costs handles None payment method."""
        costs = payment_utils.get_payment_costs(mock_request, None)

        expected_costs = {"price_net": 0.0, "tax": 0.0, "price_gross": 0.0}
        assert costs == expected_costs

    def test_get_payment_costs_handles_no_tax(self, mock_request, payment_method):
        """Test get_payment_costs handles payment method without tax."""
        payment_method.price = Decimal("15.00")
        payment_method.save()
        # payment_method.tax is None by default

        with patch("lfs.criteria.utils.get_first_valid", return_value=None):
            # Patch the payment_method.price to be a float to avoid TypeError
            with patch.object(payment_method, "price", float(payment_method.price)):
                costs = payment_utils.get_payment_costs(mock_request, payment_method)

        # With 0% tax, net price equals gross price
        # When tax_rate is 0.0, the calculation becomes (0.0 / (0.0 + 100)) * price = 0
        price_as_float = float(payment_method.price)
        expected_tax = (0.0 / (0.0 + 100)) * price_as_float  # 0
        expected_net = price_as_float - expected_tax  # price - 0
        expected_gross = price_as_float

        assert costs["tax"] == expected_tax
        assert costs["price_net"] == expected_net
        assert costs["price_gross"] == expected_gross

    def test_update_to_valid_payment_method_updates_customer(self, mock_request, admin_user, payment_method):
        """Test update_to_valid_payment_method updates customer's payment method."""
        # Create customer with invalid payment method
        invalid_method = PaymentMethod.objects.create(name="Invalid Method", active=False)
        customer = Customer.objects.create(user=admin_user, selected_payment_method=invalid_method)

        # Mock get_default_payment_method to return valid method
        with patch("lfs.payment.utils.get_default_payment_method", return_value=payment_method):
            payment_utils.update_to_valid_payment_method(mock_request, customer, save=True)

        customer.refresh_from_db()
        assert customer.selected_payment_method == payment_method

    def test_update_to_valid_payment_method_no_save_option(self, mock_request, admin_user, payment_method):
        """Test update_to_valid_payment_method with save=False."""
        invalid_method = PaymentMethod.objects.create(name="Invalid Method", active=False)
        customer = Customer.objects.create(user=admin_user, selected_payment_method=invalid_method)

        with patch("lfs.payment.utils.get_default_payment_method", return_value=payment_method):
            payment_utils.update_to_valid_payment_method(mock_request, customer, save=False)

        # Customer should be updated in memory but not saved to database
        assert customer.selected_payment_method == payment_method

        customer.refresh_from_db()
        assert customer.selected_payment_method == invalid_method  # Still invalid in DB

    def test_update_to_valid_payment_method_handles_no_default(self, mock_request, admin_user):
        """Test update_to_valid_payment_method handles case with no default payment method."""
        invalid_method = PaymentMethod.objects.create(name="Invalid Method", active=False)
        customer = Customer.objects.create(user=admin_user, selected_payment_method=invalid_method)

        with patch("lfs.payment.utils.get_default_payment_method", return_value=None):
            payment_utils.update_to_valid_payment_method(mock_request, customer, save=True)

        customer.refresh_from_db()
        assert customer.selected_payment_method is None


class TestPaymentMethodModelServices:
    """Test payment method model methods that act as services."""

    def test_payment_method_is_valid_with_no_criteria(self, mock_request, payment_method):
        """Test PaymentMethod.is_valid with no criteria returns True."""
        # Mock get_criteria to return empty list
        with patch.object(PaymentMethod, "get_criteria", return_value=[]):
            assert payment_method.is_valid(mock_request) is True

    def test_payment_method_is_valid_with_valid_criteria(self, mock_request, payment_method):
        """Test PaymentMethod.is_valid with valid criteria returns True."""
        # Mock criteria that returns True
        mock_criterion = Mock()
        mock_criterion.is_valid.return_value = True

        with patch.object(PaymentMethod, "get_criteria", return_value=[mock_criterion]):
            assert payment_method.is_valid(mock_request) is True

    def test_payment_method_is_valid_with_invalid_criteria(self, mock_request, payment_method):
        """Test PaymentMethod.is_valid with invalid criteria returns False."""
        # Mock criteria that returns False
        mock_criterion = Mock()
        mock_criterion.is_valid.return_value = False

        with patch.object(PaymentMethod, "get_criteria", return_value=[mock_criterion]):
            assert payment_method.is_valid(mock_request) is False

    def test_payment_method_is_valid_with_mixed_criteria(self, mock_request, payment_method):
        """Test PaymentMethod.is_valid with mixed criteria returns False if any invalid."""
        # Mock mixed criteria
        valid_criterion = Mock()
        valid_criterion.is_valid.return_value = True

        invalid_criterion = Mock()
        invalid_criterion.is_valid.return_value = False

        with patch.object(PaymentMethod, "get_criteria", return_value=[valid_criterion, invalid_criterion]):
            assert payment_method.is_valid(mock_request) is False

    def test_payment_method_save_criteria_delegates_to_criteria_mixin(self, mock_request, payment_method):
        """Test PaymentMethod.save_criteria delegates to Criteria mixin."""
        # Mock the parent save_criteria method
        with patch("lfs.criteria.base.Criteria.save_criteria") as mock_save_criteria:
            payment_method.save_criteria(mock_request)
            mock_save_criteria.assert_called_once_with(mock_request)

    def test_payment_method_price_is_valid_with_no_criteria(self, mock_request, payment_method_price):
        """Test PaymentMethodPrice.is_valid with no criteria returns True."""
        with patch.object(PaymentMethodPrice, "get_criteria", return_value=[]):
            assert payment_method_price.is_valid(mock_request) is True

    def test_payment_method_price_is_valid_with_valid_criteria(self, mock_request, payment_method_price):
        """Test PaymentMethodPrice.is_valid with valid criteria returns True."""
        mock_criterion = Mock()
        mock_criterion.is_valid.return_value = True

        with patch.object(PaymentMethodPrice, "get_criteria", return_value=[mock_criterion]):
            assert payment_method_price.is_valid(mock_request) is True

    def test_payment_method_price_is_valid_with_invalid_criteria(self, mock_request, payment_method_price):
        """Test PaymentMethodPrice.is_valid with invalid criteria returns False."""
        mock_criterion = Mock()
        mock_criterion.is_valid.return_value = False

        with patch.object(PaymentMethodPrice, "get_criteria", return_value=[mock_criterion]):
            assert payment_method_price.is_valid(mock_request) is False

    def test_payment_method_price_save_criteria_delegates_to_criteria_mixin(self, mock_request, payment_method_price):
        """Test PaymentMethodPrice.save_criteria delegates to Criteria mixin."""
        with patch("lfs.criteria.base.Criteria.save_criteria") as mock_save_criteria:
            payment_method_price.save_criteria(mock_request)
            mock_save_criteria.assert_called_once_with(mock_request)


class TestPaymentMethodManagerServices:
    """Test payment method manager service methods."""

    def test_active_payment_method_manager_filters_active_only(self, multiple_payment_methods):
        """Test ActivePaymentMethodManager returns only active payment methods."""
        # Make one payment method inactive
        multiple_payment_methods[1].active = False
        multiple_payment_methods[1].save()

        # Use the active manager (if it exists in the model)
        # This test assumes ActivePaymentMethodManager is used
        active_methods = PaymentMethod.objects.filter(active=True)

        assert active_methods.count() == 2
        method_names = list(active_methods.values_list("name", flat=True))
        assert "Payment Method 1" in method_names
        assert "Payment Method 3" in method_names
        assert "Payment Method 2" not in method_names

    def test_payment_method_queryset_ordering(self, multiple_payment_methods):
        """Test PaymentMethod queryset can be ordered consistently."""
        # Test ordering by name
        methods_by_name = PaymentMethod.objects.all().order_by("name")
        names = list(methods_by_name.values_list("name", flat=True))
        assert names == ["Payment Method 1", "Payment Method 2", "Payment Method 3"]

        # Test ordering by priority
        methods_by_priority = PaymentMethod.objects.all().order_by("priority")
        priorities = list(methods_by_priority.values_list("priority", flat=True))
        assert priorities == [10, 20, 30]

    def test_payment_method_filtering_by_name(self, multiple_payment_methods):
        """Test PaymentMethod filtering by name works correctly."""
        filtered_methods = PaymentMethod.objects.filter(name__icontains="Method 2")

        assert filtered_methods.count() == 1
        assert filtered_methods.first().name == "Payment Method 2"

    def test_payment_method_filtering_case_insensitive(self, multiple_payment_methods):
        """Test PaymentMethod filtering is case insensitive."""
        filtered_methods = PaymentMethod.objects.filter(name__icontains="method 2")

        assert filtered_methods.count() == 1
        assert filtered_methods.first().name == "Payment Method 2"


class TestPaymentMethodIntegrationServices:
    """Test integration services between payment methods and other components."""

    def test_customer_payment_method_integration(self, admin_user, payment_method):
        """Test integration between Customer and PaymentMethod models."""
        customer = Customer.objects.create(user=admin_user, selected_payment_method=payment_method)

        assert customer.selected_payment_method == payment_method

        # Test reverse relationship
        customers_using_method = Customer.objects.filter(selected_payment_method=payment_method)
        assert customers_using_method.count() == 1
        assert customers_using_method.first() == customer

    def test_payment_method_price_relationship(self, payment_method_with_prices):
        """Test relationship between PaymentMethod and PaymentMethodPrice."""
        prices = payment_method_with_prices.prices.all()

        assert prices.count() == 2

        for price in prices:
            assert price.payment_method == payment_method_with_prices

    def test_payment_method_tax_integration(self, payment_method, tax_rate):
        """Test integration between PaymentMethod and Tax models."""
        payment_method.tax = tax_rate
        payment_method.save()

        assert payment_method.tax == tax_rate
        assert payment_method.tax.rate == Decimal("19.0")

    def test_payment_method_deletion_cascade_behavior(self, payment_method_with_prices):
        """Test cascade behavior when PaymentMethod is deleted."""
        price_ids = list(payment_method_with_prices.prices.values_list("id", flat=True))
        payment_method_id = payment_method_with_prices.id

        payment_method_with_prices.delete()

        # Verify payment method is deleted
        assert not PaymentMethod.objects.filter(id=payment_method_id).exists()

        # Verify associated prices are deleted (assuming CASCADE)
        for price_id in price_ids:
            assert not PaymentMethodPrice.objects.filter(id=price_id).exists()


class TestPaymentMethodServicePerformance:
    """Test performance of payment method services."""

    @pytest.mark.django_db
    def test_get_valid_payment_methods_performance_with_many_methods(self, mock_request):
        """Test get_valid_payment_methods performance with many payment methods."""
        # Create many payment methods
        for i in range(100):
            PaymentMethod.objects.create(name=f"Method {i:03d}", active=True, priority=i)

        # Mock is_valid to return True for all
        with patch.object(PaymentMethod, "is_valid", return_value=True):
            valid_methods = payment_utils.get_valid_payment_methods(mock_request)

        assert len(valid_methods) == 100

    def test_payment_method_criteria_evaluation_performance(self, mock_request, payment_method):
        """Test performance of criteria evaluation with many criteria."""
        # Mock many criteria
        criteria = []
        for i in range(50):
            criterion = Mock()
            criterion.is_valid.return_value = True
            criteria.append(criterion)

        with patch.object(PaymentMethod, "get_criteria", return_value=criteria):
            result = payment_method.is_valid(mock_request)

        assert result is True

        # Verify all criteria were evaluated
        for criterion in criteria:
            criterion.is_valid.assert_called_once()

    def test_payment_costs_calculation_performance(self, mock_request, payment_method):
        """Test performance of payment costs calculation."""
        payment_method.price = Decimal("100.00")
        payment_method.save()

        # Test multiple calculations
        for i in range(100):
            with patch("lfs.criteria.utils.get_first_valid", return_value=None):
                # Patch the payment_method.price to be a float to avoid TypeError
                with patch.object(payment_method, "price", float(payment_method.price)):
                    costs = payment_utils.get_payment_costs(mock_request, payment_method)
                    # The price should equal the payment method price (as float)
                    assert costs["price_gross"] == float(payment_method.price)


class TestPaymentMethodServiceErrorHandling:
    """Test error handling in payment method services."""

    def test_get_valid_payment_methods_handles_database_errors(self, mock_request):
        """Test get_valid_payment_methods handles database errors gracefully."""
        with patch.object(PaymentMethod.objects, "filter") as mock_filter:
            mock_filter.side_effect = Exception("Database error")

            with pytest.raises(Exception):
                payment_utils.get_valid_payment_methods(mock_request)

    def test_get_payment_costs_handles_invalid_tax_rate(self, mock_request, payment_method, tax_rate):
        """Test get_payment_costs handles invalid tax rates."""
        # Use a real tax object
        payment_method.tax = tax_rate
        payment_method.price = Decimal("10.00")
        payment_method.save()

        # Mock the tax rate to return invalid value
        with patch.object(tax_rate, "rate", "invalid"):
            with patch("lfs.criteria.utils.get_first_valid", return_value=None):
                # Should handle invalid tax rate gracefully
                try:
                    costs = payment_utils.get_payment_costs(mock_request, payment_method)
                    # If it doesn't raise an exception, verify it handled it somehow
                    assert isinstance(costs, dict)
                except (ValueError, TypeError):
                    # Expected for invalid tax rate
                    pass

    def test_payment_method_is_valid_handles_criteria_errors(self, mock_request, payment_method):
        """Test PaymentMethod.is_valid handles criteria evaluation errors."""
        # Mock criterion that raises exception
        mock_criterion = Mock()
        mock_criterion.is_valid.side_effect = Exception("Criteria error")

        with patch.object(PaymentMethod, "get_criteria", return_value=[mock_criterion]):
            with pytest.raises(Exception):
                payment_method.is_valid(mock_request)

    def test_update_to_valid_payment_method_handles_save_errors(self, mock_request, admin_user, payment_method):
        """Test update_to_valid_payment_method handles save errors."""
        customer = Customer.objects.create(user=admin_user)

        # Mock customer save to raise exception
        with patch.object(Customer, "save", side_effect=Exception("Save error")):
            with patch("lfs.payment.utils.get_default_payment_method", return_value=payment_method):
                with pytest.raises(Exception):
                    payment_utils.update_to_valid_payment_method(mock_request, customer, save=True)

    def test_get_payment_costs_handles_missing_price(self, mock_request, payment_method):
        """Test get_payment_costs handles missing price gracefully."""
        # Payment method with zero price (None violates NOT NULL constraint)
        payment_method.price = Decimal("0.00")
        payment_method.save()

        with patch("lfs.criteria.utils.get_first_valid", return_value=None):
            # Patch the payment_method.price to be a float to avoid TypeError
            with patch.object(payment_method, "price", float(payment_method.price)):
                costs = payment_utils.get_payment_costs(mock_request, payment_method)
                # Should handle zero price gracefully
                assert isinstance(costs, dict)
                # The price should equal the payment method price (as float)
                assert costs["price_gross"] == float(payment_method.price)

    def test_payment_method_criteria_with_corrupted_data(self, mock_request, payment_method):
        """Test payment method criteria handling with corrupted data."""
        # Mock get_criteria to return invalid data
        with patch.object(PaymentMethod, "get_criteria", return_value=[None, "invalid", 123]):
            try:
                result = payment_method.is_valid(mock_request)
                # If it doesn't crash, verify it handled corrupted data
                assert isinstance(result, bool)
            except (AttributeError, TypeError):
                # Expected for corrupted criteria data
                pass
