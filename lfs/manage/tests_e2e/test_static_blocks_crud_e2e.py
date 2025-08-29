"""
End-to-End tests for StaticBlock CRUD operations.

Tests complete user workflows using real browser interactions.
Validates JavaScript functionality and user experience.

Following TDD principles:
- Test user behavior, not implementation
- One workflow per test method
- Arrange-Act-Assert structure
"""

import pytest
import re
from playwright.sync_api import Page, expect


def navigate_to_static_blocks(page: Page, live_server):
    """Helper to navigate to StaticBlocks management page."""
    page.goto(f"{live_server.url}/manage/")
    page.click("#htmlDropdown")  # Open HTML dropdown menu
    page.wait_for_selector('a[href="/manage/static-blocks"]', state="visible")
    page.click('a[href="/manage/static-blocks"]')

    # Verify we're on the right page
    expect(page).to_have_url(re.compile(r".*/manage/(static-block|no-static-block).*"))
    expect(page.get_by_role("heading", name="Static Blocks")).to_be_visible()


def open_add_static_block_modal(page: Page):
    """Helper to open the Add StaticBlock modal."""
    page.click('button:has-text("Add Static Block")')
    expect(page.locator(".modal")).to_be_visible()


def fill_and_submit_static_block_form(page: Page, name: str):
    """Helper to fill and submit StaticBlock form."""
    page.fill('input[name="name"]', name)
    page.click('button[type="submit"]:has-text("Save")')


@pytest.mark.e2e
@pytest.mark.django_db
class TestStaticBlockCRUDFlow:
    """Complete StaticBlock CRUD user journey tests."""

    @pytest.mark.parametrize(
        "test_name,expected_url_pattern",
        [
            ("E2E Test Block", "static"),
            ("Simple Test Name", "static"),
        ],
    )
    def test_user_can_create_static_block(self, logged_in_page: Page, live_server, test_name, expected_url_pattern):
        """User should be able to create a new StaticBlock via modal form."""
        page = logged_in_page

        # Arrange: Navigate to StaticBlocks management
        navigate_to_static_blocks(page, live_server)

        # Act: Open modal and fill form
        open_add_static_block_modal(page)
        fill_and_submit_static_block_form(page, test_name)

        # Expect: Should redirect to edit view or list view
        page.wait_for_url(lambda url: expected_url_pattern in url.lower())

        # Expect: Should see success message or the created block
        expect(page.locator(f"text={test_name}")).to_be_visible()

    def test_user_can_edit_static_block(self, logged_in_page: Page, live_server, static_block_e2e):
        """User should be able to edit an existing StaticBlock."""

        page = logged_in_page

        # Arrange: Navigate to edit view of existing block
        edit_url = f"{live_server.url}/manage/static-block/{static_block_e2e.id}/"
        page.goto(edit_url)

        # Expect: Should be on edit page
        expect(page.locator('input[name="name"]')).to_have_value(static_block_e2e.name)

        # Act: Modify the name
        page.fill('input[name="name"]', "Modified E2E Test Block")

        # Act: Submit form
        page.click('button[type="submit"]:has-text("Save")')

        # Expect: Should see updated content
        expect(page.locator("text=Modified E2E Test Block")).to_be_visible()

    def test_user_can_delete_static_block(self, logged_in_page: Page, live_server, static_block_e2e):
        """User should be able to delete a StaticBlock with confirmation."""
        page = logged_in_page

        # Arrange: Navigate to StaticBlocks list
        navigate_to_static_blocks(page, live_server)

        # Expect: Should see the test block
        expect(page.locator(f"text={static_block_e2e.name}")).to_be_visible()

        # Set up dialog handler BEFORE triggering the action
        page.on("dialog", lambda dialog: dialog.accept())

        # Act: Click delete button (will trigger confirmation dialog)
        page.click(f'a:has-text("Delete Static Block")')

        # Expect: Block should be removed from list
        expect(page.locator(f"text={static_block_e2e.name}")).not_to_be_visible()


# File management tests moved to: test_static_blocks_file_management_e2e.py
# UI interaction tests moved to: test_static_blocks_ui_e2e.py


# Test configuration
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.slow,
]
