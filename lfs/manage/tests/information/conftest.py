import pytest
from lfs.core.models import Shop


@pytest.fixture(autouse=True)
def setup_shop(db):
    """Create a default shop for all information tests."""
    # Create a default shop if none exists
    if not Shop.objects.exists():
        Shop.objects.create(
            name="Test Shop",
            shop_owner="Test Owner",
            from_email="test@example.com",
        )


@pytest.fixture
def test_shop(db):
    """Create a test shop for individual tests."""
    return Shop.objects.create(
        name="Test Shop",
        shop_owner="Test Owner",
        from_email="test@example.com",
    )
