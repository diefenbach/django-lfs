"""
Pytest configuration and fixtures for criteria tests.
"""

import pytest
from unittest.mock import Mock
from django.test import RequestFactory
from django.contrib.auth import get_user_model

from lfs.criteria.models import CartPriceCriterion, CountryCriterion
from lfs.core.models import Country

User = get_user_model()


@pytest.fixture
def request_factory():
    """Django RequestFactory for creating test requests."""
    return RequestFactory()


@pytest.fixture
def manage_user(db):
    """User with manage_shop permission."""
    user = User.objects.create_user(username="testmanager", email="manager@test.com", password="testpass123")
    user.is_superuser = True
    user.is_staff = True
    user.save()
    return user


@pytest.fixture
def mock_request(request_factory, manage_user):
    """Mock request object for testing."""
    request = request_factory.get("/")
    request.user = manage_user
    request.session = {}
    return request


@pytest.fixture
def mock_cart_price_criterion():
    """Mock CartPriceCriterion for testing."""
    criterion = Mock(spec=CartPriceCriterion)
    criterion.pk = 1
    criterion.render.return_value = "<div>Mock Cart Price Criterion</div>"
    return criterion


@pytest.fixture
def mock_country_criterion():
    """Mock CountryCriterion for testing."""
    criterion = Mock(spec=CountryCriterion)
    criterion.pk = 2
    criterion.render.return_value = "<div>Mock Country Criterion</div>"
    return criterion


@pytest.fixture
def default_country(db):
    """Create a default country for testing."""
    return Country.objects.create(code="us", name="USA")


@pytest.fixture
def multiple_countries(db):
    """Multiple countries for testing."""
    countries = []
    for i, (code, name) in enumerate([("us", "USA"), ("de", "Germany"), ("fr", "France")]):
        country = Country.objects.create(code=code, name=name)
        countries.append(country)
    return countries


@pytest.fixture
def mock_lfs_criteria_setting():
    """Mock LFS_CRITERIA setting for testing."""
    return [
        ["lfs.criteria.models.CartPriceCriterion", "Cart Price"],
        ["lfs.criteria.models.CountryCriterion", "Country"],
        ["lfs.criteria.models.WeightCriterion", "Weight"],
    ]
