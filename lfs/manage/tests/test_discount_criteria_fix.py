import pytest
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware

from lfs.discounts.models import Discount
from lfs.discounts.settings import DISCOUNT_TYPE_ABSOLUTE


class TestDiscountCriteria(TestCase):
    """Test cases for discount criteria functionality."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", password="testpass123")

        # Create a test discount
        self.discount = Discount.objects.create(name="Test Discount", value=10.0, type=DISCOUNT_TYPE_ABSOLUTE)

    def test_save_criteria_with_invalid_type_key(self):
        """Test that save_criteria handles invalid type keys gracefully."""
        # Create a request with invalid type key (no dash)
        request = self.factory.post(
            "/test/",
            {"type": "invalid_key_without_dash", "csrfmiddlewaretoken": "test"},  # This should cause IndexError
        )

        # Add session and messages middleware
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        messages_middleware = MessageMiddleware(lambda req: None)
        messages_middleware.process_request(request)

        # This should not raise an IndexError
        try:
            self.discount.save_criteria(request)
        except IndexError:
            pytest.fail("save_criteria raised IndexError when it should handle it gracefully")

    def test_save_criteria_with_empty_post(self):
        """Test that save_criteria handles empty POST data."""
        request = self.factory.post("/test/", {})

        # Add session and messages middleware
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        messages_middleware = MessageMiddleware(lambda req: None)
        messages_middleware.process_request(request)

        # This should not raise any exception
        try:
            self.discount.save_criteria(request)
        except Exception as e:
            pytest.fail(f"save_criteria raised {type(e).__name__}: {e}")

    def test_save_criteria_with_valid_type_key(self):
        """Test that save_criteria works with valid type keys."""
        request = self.factory.post(
            "/test/",
            {
                "type-123": "lfs.criteria.models.CartPriceCriterion",
                "operator-123": "0",
                "position-123": "10",
                "value-123": "100",
                "csrfmiddlewaretoken": "test",
            },
        )

        # Add session and messages middleware
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        messages_middleware = MessageMiddleware(lambda req: None)
        messages_middleware.process_request(request)

        # This should work without raising exceptions
        try:
            self.discount.save_criteria(request)
        except Exception as e:
            pytest.fail(f"save_criteria raised {type(e).__name__}: {e}")
