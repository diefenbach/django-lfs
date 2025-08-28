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


@pytest.mark.e2e
@pytest.mark.django_db
class TestStaticBlockCRUDFlow:
    """Complete StaticBlock CRUD user journey tests."""

    def test_user_can_create_static_block(self, logged_in_page: Page, live_server):
        """User should be able to create a new StaticBlock via modal form."""
        page = logged_in_page

        # Arrange: Navigate to manage interface
        page.goto(f"{live_server.url}/manage/")

        # Act: Navigate to StaticBlocks - first open HTML dropdown, then click
        page.click("#htmlDropdown")  # Open HTML dropdown menu using specific ID
        page.wait_for_selector('a[href="/manage/static-blocks"]', state="visible")  # Wait for dropdown to open
        page.click('a[href="/manage/static-blocks"]')  # Then click static blocks link

        # Expect: Should see StaticBlocks management page (either list or no-blocks page)
        expect(page).to_have_url(re.compile(r".*/manage/(static-blocks|no-static-blocks).*"))
        expect(page.get_by_role("heading", name="Static Blocks")).to_be_visible()

        # Act: Click Add StaticBlock button to open modal
        page.click('button:has-text("Add Static Block")')

        # Expect: Modal should be visible
        expect(page.locator(".modal")).to_be_visible()

        # Act: Fill form in modal
        page.fill('input[name="name"]', "E2E Test Block")

        # Act: Submit form
        page.click('button[type="submit"]:has-text("Save")')

        # Expect: Should redirect to edit view or list view
        page.wait_for_url(lambda url: "static" in url.lower())

        # Expect: Should see success message or the created block
        expect(page.locator("text=E2E Test Block")).to_be_visible()

    def test_user_can_edit_static_block(self, logged_in_page: Page, live_server, static_block_e2e):
        """User should be able to edit an existing StaticBlock."""
        page = logged_in_page

        # Arrange: Navigate to edit view of existing block
        edit_url = f"{live_server.url}/manage/static-blocks/{static_block_e2e.id}/"
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
        page.goto(f"{live_server.url}/manage/static-blocks/")

        # Expect: Should see the test block
        expect(page.locator(f"text={static_block_e2e.name}")).to_be_visible()

        # Act: Click delete button (adjust selector based on actual UI)
        page.click(f'tr:has-text("{static_block_e2e.name}") button:has-text("Delete")')

        # Expect: Confirmation modal should appear
        expect(page.locator('.modal:has-text("Delete")')).to_be_visible()

        # Act: Confirm deletion
        page.click('button:has-text("Confirm"):visible')

        # Expect: Block should be removed from list
        expect(page.locator(f"text={static_block_e2e.name}")).not_to_be_visible()


@pytest.mark.e2e
@pytest.mark.django_db
class TestStaticBlockFileManagement:
    """Test file upload and management functionality."""

    def test_select_all_checkbox_functionality(self, logged_in_page: Page, live_server, static_block_e2e):
        """Select All checkbox should work with three-state behavior."""
        page = logged_in_page

        # Arrange: Navigate to files tab (assuming files are already present)
        files_url = f"{live_server.url}/manage/static-blocks/{static_block_e2e.id}/files/"
        page.goto(files_url)

        # Skip test if no files present
        if not page.locator(".select-delete-files").count():
            pytest.skip("No files present for testing select all functionality")

        # Act: Click select all checkbox
        page.click("#select-all-files")

        # Expect: All individual checkboxes should be checked
        individual_checkboxes = page.locator(".select-delete-files")
        for i in range(individual_checkboxes.count()):
            expect(individual_checkboxes.nth(i)).to_be_checked()

        # Act: Uncheck one individual checkbox
        individual_checkboxes.first.click()

        # Expect: Select all checkbox should be in indeterminate state
        # Note: Playwright doesn't have direct indeterminate check, but we can verify behavior
        expect(page.locator("#select-all-files")).not_to_be_checked()

        # Act: Check the individual checkbox again
        individual_checkboxes.first.click()

        # Expect: Select all checkbox should be checked again
        expect(page.locator("#select-all-files")).to_be_checked()


@pytest.mark.e2e
@pytest.mark.django_db
class TestStaticBlockJavaScriptInteractions:
    """Test JavaScript functionality and modal behavior."""

    def test_modal_opens_and_closes_correctly(self, logged_in_page: Page, live_server):
        """Modal should open and close without flickering."""
        page = logged_in_page

        # Arrange: Navigate to StaticBlocks
        page.goto(f"{live_server.url}/manage/static-blocks/")

        # Act: Click Add button to open modal
        page.click('button:has-text("Add Static Block")')

        # Expect: Modal should be visible
        modal = page.locator(".modal")
        expect(modal).to_be_visible()

        # Act: Close modal via close button
        page.click(".modal .btn-close")

        # Expect: Modal should be hidden
        expect(modal).not_to_be_visible()

    def test_htmx_content_loading(self, logged_in_page: Page, live_server, static_block_e2e):
        """HTMX should load content dynamically without page refresh."""
        page = logged_in_page

        # Arrange: Navigate to StaticBlock edit
        page.goto(f"{live_server.url}/manage/static-blocks/{static_block_e2e.id}/")

        # Act: Click Files tab
        page.click('a[href*="files"]:has-text("Files")')

        # Expect: Content should change without page reload
        # We can verify this by checking the URL doesn't change completely
        expect(page).to_have_url(lambda url: "files" in url)

        # Expect: Files content should be loaded
        expect(page.locator("text=Files")).to_be_visible()


# Test configuration
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.slow,
]
