"""
Playwright configuration and fixtures for LFS manage E2E tests.

Following TDD principles:
- Independent test execution
- Reliable test data setup
- Proper cleanup
"""

import os
import pytest

# Configure Django settings before importing Django modules
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings.testing")
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

import django

django.setup()

from django.contrib.auth import get_user_model
from playwright.sync_api import Browser, BrowserContext, Page

from lfs.catalog.models import StaticBlock


User = get_user_model()


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for all tests."""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
    }


@pytest.fixture
def context(browser: Browser):
    """Create a new browser context for each test."""
    context = browser.new_context()
    yield context
    context.close()


@pytest.fixture
def page(context: BrowserContext):
    """Create a new page for each test."""
    page = context.new_page()
    yield page
    page.close()


@pytest.fixture
def manage_user_e2e(db):
    """User with manage_shop permission for E2E tests."""
    user = User.objects.create_user(username="e2e_manager", email="e2e@test.com", password="testpass123")

    # Create superuser to bypass permission check for testing
    user.is_superuser = True
    user.is_staff = True
    user.save()
    return user


@pytest.fixture
def shop_e2e(db):
    """Shop instance with robust initialization handling."""
    from lfs.core.models import Shop

    shop = Shop.objects.create(name="Test Shop")

    return shop


@pytest.fixture
def static_block_e2e(db, shop_e2e):
    """StaticBlock for E2E testing."""
    return StaticBlock.objects.create(name="E2E Test Block", html="<p>Test content for E2E testing</p>")


@pytest.fixture
def static_block_with_files_e2e(db, shop_e2e):
    """StaticBlock with dummy files for E2E testing."""
    from lfs.catalog.models import StaticBlock, File
    from django.core.files.base import ContentFile
    from django.contrib.contenttypes.models import ContentType

    # Create StaticBlock
    static_block = StaticBlock.objects.create(
        name="E2E Block with Files", html="<p>Block with test files</p>", display_files=True
    )

    # Create ContentType for StaticBlock
    content_type = ContentType.objects.get_for_model(StaticBlock)

    # Create dummy files
    for i in range(1, 4):  # 3 dummy files
        # Create a simple text file content
        file_content = ContentFile(
            f"This is test file {i} content.\nCreated for E2E testing.", name=f"test_file_{i}.txt"
        )

        File.objects.create(
            title=f"Test File {i}",
            slug=f"test-file-{i}",
            description=f"Description for test file {i}",
            file=file_content,
            content_type=content_type,
            content_id=static_block.id,
            position=i,
        )

    return static_block


def accept_cookie_banner(page: Page):
    """Helper function to close chat widget and accept cookie banner if present."""
    try:
        page.click(".mateo-close", timeout=500)
    except:
        pass  # No chat widget found

    try:
        page.click("#lcc-accept-all", timeout=500)
    except:
        pass  # No cookie banner found


def login_user(page: Page, username: str, password: str):
    """Helper function to log in a user."""
    page.fill('input[name="username"]', username)
    page.fill('input[name="password"]', password)

    # Try different submit button selectors (HIG theme uses Bootstrap)
    try:
        page.click('button.btn.btn-primary:has-text("Login")')
    except:
        try:
            page.click('button[type="submit"]:has-text("Login")')
        except:
            try:
                page.click('button:has-text("Login")')
            except:
                page.click('input[type="submit"]')


@pytest.fixture
def authenticated_page(page: Page, live_server, manage_user_e2e, shop_e2e):
    """Page with authenticated manage user session."""
    # Navigate to manage interface
    page.goto(f"{live_server.url}/manage/")

    # Handle cookie banner quickly
    accept_cookie_banner(page)

    # Login if redirected to login page
    if "login" in page.url:
        login_user(page, manage_user_e2e.username, "testpass123")
        page.wait_for_url(lambda url: "manage" in url, timeout=2000)

    return page


# Alias for backward compatibility
@pytest.fixture
def logged_in_page(authenticated_page):
    """Alias for authenticated_page for backward compatibility."""
    return authenticated_page


def pytest_configure(config):
    """Configure pytest for E2E tests."""
    # Allow Django async operations during tests
    os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


# Playwright pytest plugin configuration
@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Configure browser launch arguments."""
    return {
        **browser_type_launch_args,
        "headless": False,  # Set to False for visual debugging
        "slow_mo": 0,  # Milliseconds to slow down operations
        "args": ["--start-maximized", "--no-sandbox", "--disable-dev-shm-usage"],  # Start browser maximized
    }


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Enable database access for all E2E tests.

    E2E tests need database access since they interact with live_server
    which requires real database operations.
    """
    pass


# Custom pytest markers for E2E tests
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "e2e: mark test as end-to-end integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
