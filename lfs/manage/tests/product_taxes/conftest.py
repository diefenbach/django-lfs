"""
Test fixtures for product_taxes module tests.

Following pytest best practices:
- Fixtures over setup/teardown
- Clear fixture names describing what they provide
- Minimal mocking - prefer real objects
- Fast, isolated fixtures
"""

import pytest
from django.contrib.auth import get_user_model

from lfs.tax.models import Tax

User = get_user_model()


# Common fixtures are now imported from the main conftest.py


@pytest.fixture
def tax():
    """Create a single tax for testing."""
    return Tax.objects.create(rate=19.0, description="VAT 19%")


@pytest.fixture
def multiple_taxes():
    """Create multiple taxes for testing."""
    taxes = []

    # Create first tax
    tax1 = Tax.objects.create(rate=19.0, description="VAT 19%")
    taxes.append(tax1)

    # Create second tax
    tax2 = Tax.objects.create(rate=7.0, description="VAT 7%")
    taxes.append(tax2)

    # Create third tax
    tax3 = Tax.objects.create(rate=0.0, description="No Tax")
    taxes.append(tax3)

    return taxes


# Common fixtures (MockSession, mock_session, mock_request, htmx_request)
# are now imported from the main conftest.py
