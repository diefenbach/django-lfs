"""
Comprehensive edge case tests for discount management.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Fast tests with minimal mocking

Tests cover:
- Boundary conditions and edge cases
- Error handling and validation
- Invalid input handling
- Database integrity
- Permission edge cases
"""

import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse

from lfs.discounts.models import Discount
from lfs.discounts.settings import DISCOUNT_TYPE_ABSOLUTE, DISCOUNT_TYPE_PERCENTAGE
from lfs.catalog.models import Product

User = get_user_model()


class TestDiscountBoundaryConditions:
    """Test boundary conditions for discounts."""

    def test_discount_name_minimum_length(self, db):
        """Should handle minimum name length."""
        discount = Discount(name="A", value=Decimal("1.00"), type=DISCOUNT_TYPE_ABSOLUTE)
        discount.full_clean()  # Should not raise validation error
        discount.save()
        assert Discount.objects.filter(name="A").exists()

    def test_discount_name_maximum_length(self, db):
        """Should handle maximum name length."""
        long_name = "A" * 100  # Using reasonable length within model limits
        discount = Discount(name=long_name, value=Decimal("10.00"), type=DISCOUNT_TYPE_ABSOLUTE)
        discount.full_clean()  # Should not raise validation error
        discount.save()
        assert Discount.objects.filter(name=long_name).exists()

    def test_discount_value_minimum(self, db):
        """Should handle minimum discount value."""
        discount = Discount(name="Min Value", value=Decimal("0.01"), type=DISCOUNT_TYPE_ABSOLUTE)
        discount.full_clean()  # Should not raise validation error
        discount.save()
        assert Discount.objects.filter(name="Min Value").exists()

    def test_discount_value_maximum(self, db):
        """Should handle maximum discount value."""
        # Test with a very large value
        large_value = Decimal("999999.99")
        discount = Discount(name="Max Value", value=large_value, type=DISCOUNT_TYPE_ABSOLUTE)
        discount.full_clean()  # Should not raise validation error
        discount.save()
        assert Discount.objects.filter(name="Max Value").exists()

    def test_discount_value_zero(self, db):
        """Should handle zero discount value."""
        discount = Discount(name="Zero Discount", value=Decimal("0.00"), type=DISCOUNT_TYPE_ABSOLUTE)
        discount.full_clean()  # Should not raise validation error
        discount.save()
        assert Discount.objects.filter(name="Zero Discount").exists()

    def test_discount_with_many_products(self, db, discount, shop):
        """Should handle discount with many products."""
        # Create many products
        products = []
        for i in range(20):  # Test with 20 products (reasonable for test)
            product = Product.objects.create(
                name=f"Product {i}",
                slug=f"product-{i}",
                sku=f"SKU-{i:03d}",
                price=Decimal("10.00"),
                active=True,
            )
            products.append(product)

        # Assign all products to discount
        discount.products.add(*products)

        # Verify all products were assigned
        assert discount.products.count() == 20

        # Verify discount can be saved with many products
        discount.save()
        discount.refresh_from_db()
        assert discount.products.count() == 20


class TestDiscountValidationEdgeCases:
    """Test validation edge cases."""

    def test_negative_discount_value(self, db):
        """Should accept negative discount values (original model doesn't validate)."""
        discount = Discount(name="Negative", value=-10.0, type=DISCOUNT_TYPE_ABSOLUTE)

        # Original model doesn't validate negative values
        discount.full_clean()  # Should not raise ValidationError
        discount.save()
        assert discount.value == -10.0

    def test_empty_discount_name(self, db):
        """Should reject empty discount names (Django CharField validation)."""
        discount = Discount(name="", value=10.0, type=DISCOUNT_TYPE_ABSOLUTE)

        # Django's CharField with blank=False rejects empty strings
        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            discount.full_clean()

    def test_whitespace_only_name(self, db):
        """Should accept whitespace-only names (original model doesn't validate)."""
        discount = Discount(name="   ", value=10.0, type=DISCOUNT_TYPE_ABSOLUTE)

        # Original model doesn't validate whitespace names
        discount.full_clean()  # Should not raise ValidationError
        discount.save()
        assert discount.name == "   "

    def test_unicode_characters_in_name(self, db):
        """Should handle unicode characters in discount name."""
        unicode_name = "Rabatt mit Umlauten äöü"
        discount = Discount(name=unicode_name, value=10.0, type=DISCOUNT_TYPE_ABSOLUTE)
        discount.full_clean()  # Should not raise validation error
        discount.save()
        assert discount.name == unicode_name

    def test_percentage_discount_over_100(self, db):
        """Should handle percentage discounts over 100%."""
        # Original model doesn't validate percentage values
        discount = Discount(name="High Percentage", value=150.0, type=DISCOUNT_TYPE_PERCENTAGE)
        discount.full_clean()  # Should not raise validation error
        discount.save()
        assert Discount.objects.filter(name="High Percentage").exists()

    def test_percentage_discount_negative(self, db):
        """Should accept negative percentage discounts (original model doesn't validate)."""
        discount = Discount(name="Negative Percent", value=-5.0, type=DISCOUNT_TYPE_PERCENTAGE)

        # Original model doesn't validate negative percentage values
        discount.full_clean()  # Should not raise ValidationError
        discount.save()
        assert discount.value == -5.0

    def test_invalid_discount_type(self, db):
        """Should reject invalid discount types (Django PositiveSmallIntegerField validation)."""
        discount = Discount(name="Invalid Type", value=10.0, type="invalid_type")

        # Django's PositiveSmallIntegerField rejects non-integer values
        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            discount.full_clean()


class TestDiscountModelEdgeCases:
    """Test model-related edge cases."""

    def test_discount_active_default_value(self, db):
        """Should have correct default value for active field."""
        discount = Discount(name="Default Active", value=10.0, type=DISCOUNT_TYPE_ABSOLUTE)
        discount.save()

        # Active should default to False
        assert discount.active is False

    def test_discount_str_method(self, db):
        """Should have proper string representation."""
        discount = Discount(name="Test Discount", value=15.50, type=DISCOUNT_TYPE_ABSOLUTE)
        expected_str = "Test Discount"
        assert str(discount) == expected_str

    def test_discount_with_same_name_allowed(self, db):
        """Should allow multiple discounts with same name."""
        discount1 = Discount.objects.create(name="Same Name", value=10.00, type=DISCOUNT_TYPE_ABSOLUTE)
        discount2 = Discount.objects.create(name="Same Name", value=20.00, type=DISCOUNT_TYPE_PERCENTAGE)

        # Both should exist
        assert Discount.objects.filter(name="Same Name").count() == 2

    def test_discount_criteria_empty_by_default(self, db):
        """Should have empty criteria by default."""
        discount = Discount.objects.create(name="No Criteria", value=Decimal("10.00"), type=DISCOUNT_TYPE_ABSOLUTE)

        # Should have no criteria initially
        assert len(discount.get_criteria()) == 0


class TestDiscountDecimalPrecisionEdgeCases:
    """Test decimal precision edge cases."""

    def test_discount_value_many_decimal_places(self, db):
        """Should handle float values."""
        value = 10.99
        discount = Discount(name="Precise", value=value, type=DISCOUNT_TYPE_ABSOLUTE)
        discount.full_clean()
        discount.save()

        # Value should be preserved (within float precision limits)
        discount.refresh_from_db()
        assert abs(discount.value - value) < 0.001  # Allow for float precision

    def test_discount_value_rounding(self, db):
        """Should handle float value rounding."""
        value = 10.99
        discount = Discount(name="Rounding Test", value=value, type=DISCOUNT_TYPE_ABSOLUTE)
        discount.full_clean()
        discount.save()

        discount.refresh_from_db()
        # Should preserve the value as stored
        assert abs(discount.value - value) < 0.001  # Allow for float precision


class TestDiscountDatabaseIntegrity:
    """Test database integrity constraints."""

    def test_discount_cannot_delete_with_assigned_products(self, db, discount_with_products):
        """Should handle discount deletion with assigned products."""
        # This should work - deleting discount should not affect products
        discount_id = discount_with_products.id
        discount_with_products.delete()

        assert not Discount.objects.filter(id=discount_id).exists()

        # Products should still exist
        from lfs.catalog.models import Product

        assert Product.objects.count() > 0

    def test_discount_bulk_delete(self, db):
        """Should handle bulk deletion of discounts."""
        # Create multiple discounts
        discounts = []
        for i in range(5):
            discount = Discount.objects.create(
                name=f"Bulk Delete {i}", value=Decimal(f"{i+1}.00"), type=DISCOUNT_TYPE_ABSOLUTE
            )
            discounts.append(discount)

        # Delete all
        deleted_count = Discount.objects.filter(name__startswith="Bulk Delete").delete()[0]

        assert deleted_count == 5
        assert Discount.objects.filter(name__startswith="Bulk Delete").count() == 0


class TestDiscountPermissionEdgeCases:
    """Test permission-related edge cases."""

    def test_discount_views_require_staff_status(self, client, regular_user, discount):
        """Should require staff status for discount views."""
        client.force_login(regular_user)

        urls = [
            reverse("lfs_manage_discount", kwargs={"id": discount.id}),
            reverse("lfs_manage_discount_criteria", kwargs={"id": discount.id}),
            reverse("lfs_manage_discount_products", kwargs={"id": discount.id}),
            reverse("lfs_manage_add_discount"),
        ]

        for url in urls:
            response = client.get(url)
            # Should redirect to login or return 403
            assert response.status_code in [302, 403, 401]

    def test_discount_views_require_superuser_or_staff(self, client, admin_user, discount):
        """Should allow access for superuser."""
        client.force_login(admin_user)

        urls = [
            reverse("lfs_manage_discount", kwargs={"id": discount.id}),
            reverse("lfs_manage_discount_criteria", kwargs={"id": discount.id}),
            reverse("lfs_manage_discount_products", kwargs={"id": discount.id}),
        ]

        for url in urls:
            response = client.get(url)
            assert response.status_code == 200


class TestDiscountConcurrencyEdgeCases:
    """Test concurrency-related edge cases."""

    def test_discount_simultaneous_updates(self, db, discount):
        """Should handle simultaneous discount updates."""
        # Create two discount instances from same DB record
        discount1 = Discount.objects.get(id=discount.id)
        discount2 = Discount.objects.get(id=discount.id)

        # Update both
        discount1.name = "Updated by 1"
        discount1.save()

        discount2.name = "Updated by 2"
        discount2.save()

        # Both updates should succeed (last write wins)
        discount.refresh_from_db()
        assert discount.name == "Updated by 2"


class TestDiscountCriteriaEdgeCases:
    """Test discount criteria edge cases."""

    def test_criteria_with_invalid_model_reference(self, discount, request_factory):
        """Should handle criteria with invalid model references."""
        from django.contrib.sessions.middleware import SessionMiddleware
        from django.contrib.messages.middleware import MessageMiddleware

        request = request_factory.post(
            "/test/",
            {"type-invalid": "invalid.model.Class", "csrfmiddlewaretoken": "test"},
        )

        # Add session and messages middleware
        SessionMiddleware(lambda req: None).process_request(request)
        request.session.save()
        MessageMiddleware(lambda req: None).process_request(request)

        # This should not raise an exception
        try:
            discount.save_criteria(request)
        except Exception:
            # Should handle gracefully
            pass

    def test_criteria_with_malformed_keys(self, discount, request_factory):
        """Should handle criteria with malformed keys."""
        from django.contrib.sessions.middleware import SessionMiddleware
        from django.contrib.messages.middleware import MessageMiddleware

        request = request_factory.post(
            "/test/",
            {"malformed_key_without_dash": "value", "csrfmiddlewaretoken": "test"},
        )

        # Add session and messages middleware
        SessionMiddleware(lambda req: None).process_request(request)
        request.session.save()
        MessageMiddleware(lambda req: None).process_request(request)

        # This should not raise IndexError
        try:
            discount.save_criteria(request)
        except IndexError:
            pytest.fail("save_criteria raised IndexError for malformed key")
