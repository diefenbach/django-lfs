import pytest
from lfs.catalog.models import StaticBlock, File
from lfs.core.models import Shop


@pytest.fixture(scope="session", autouse=True)
def setup_shop_for_tests(django_db_setup, django_db_blocker):
    """Create a default shop for all tests that need it."""
    with django_db_blocker.unblock():
        # Create a default shop if none exists
        if not Shop.objects.exists():
            Shop.objects.create(
                name="Test Shop",
                shop_owner="Test Owner",
                from_email="test@example.com",
                notification_emails="test@example.com",
                description="Test shop description",
            )


@pytest.fixture
def test_shop(db):
    """Create a test shop for individual tests."""
    return Shop.objects.create(
        name="Test Shop",
        shop_owner="Test Owner",
        from_email="test@example.com",
        notification_emails="test@example.com",
        description="Test shop description",
    )


@pytest.fixture
def sample_static_block(db):
    """Create a sample static block for testing."""
    return StaticBlock.objects.create(
        name="Test Static Block",
        html="<p>This is test HTML content</p>",
    )


@pytest.fixture
def sample_static_blocks(db):
    """Create multiple sample static blocks for testing."""
    blocks = []
    for i in range(3):
        block = StaticBlock.objects.create(
            name=f"Test Static Block {i+1}",
            html=f"<p>This is test HTML content {i+1}</p>",
        )
        blocks.append(block)
    return blocks


@pytest.fixture
def sample_file(sample_static_block):
    """Create a sample file for testing."""
    return File.objects.create(
        content=sample_static_block,
        title="test_file.txt",
        file="test_file.txt",
    )


@pytest.fixture
def sample_files(sample_static_block):
    """Create multiple sample files for testing."""
    files = []
    for i in range(3):
        file_obj = File.objects.create(
            content=sample_static_block,
            title=f"test_file_{i+1}.txt",
            file=f"test_file_{i+1}.txt",
            position=(i + 1) * 10,
        )
        files.append(file_obj)
    return files
