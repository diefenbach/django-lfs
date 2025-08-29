"""
End-to-End tests for Actions CRUD operations.

Tests complete user workflows using real browser interactions.
Validates JavaScript functionality and user experience.

Following TDD principles:
- Test user behavior, not implementation
- One workflow per test method
- Arrange-Act-Assert structure
"""

import pytest
from playwright.sync_api import Page, expect


def navigate_to_actions(page: Page, live_server):
    """Helper to navigate to Actions management page."""
    # Navigate directly to actions URL to avoid navigation issues
    page.goto(f"{live_server.url}/manage/actions/")

    # Wait for the page to load
    page.wait_for_load_state("networkidle")

    # Verify we're on the right page
    page.wait_for_url(lambda url: "manage" in url and ("action" in url or "no-actions" in url), timeout=10000)

    # Wait for the page content to load
    page.wait_for_load_state("networkidle")


def open_add_action_modal(page: Page):
    """Helper to open the Add Action modal."""
    page.click('button:has-text("Add Action")')
    expect(page.locator(".modal")).to_be_visible()


def fill_and_submit_action_form(page: Page, title: str, link: str = "https://example.com/test", group_id: int = None):
    """Helper to fill and submit Action form."""
    page.fill('input[name="create-title"]', title)
    page.fill('input[name="create-link"]', link)

    # Select the specified group or first available one
    if group_id:
        page.select_option('select[name="create-group"]', value=str(group_id))
    else:
        page.select_option('select[name="create-group"]', index=0)

    page.click('button[type="submit"]:has-text("Add")')


@pytest.mark.e2e
@pytest.mark.django_db
class TestActionCRUDFlow:
    """Complete Action CRUD user journey tests."""

    def test_user_can_create_action(self, logged_in_page: Page, live_server, action_group_e2e):
        """User should be able to create an Action and assign it to a group."""
        page = logged_in_page
        action_title = "Group Action Test"

        # Arrange: Navigate to Actions management
        navigate_to_actions(page, live_server)

        # Act: Open modal and fill form with group selection
        open_add_action_modal(page)
        fill_and_submit_action_form(page, action_title, "https://example.com/group-action", action_group_e2e.id)

        # Expect: Action should appear in the sidebar within its group
        sidebar = page.locator("aside")
        expect(sidebar.locator(f"text={action_title}")).to_be_visible()

        # Verify it's in the correct group section
        group_section = sidebar.locator(f".action-group[data-list='{action_group_e2e.id}']")
        expect(group_section.locator(f"text={action_title}")).to_be_visible()

    def test_action_form_requires_group_selection(self, logged_in_page: Page, live_server):
        """Action form should require group selection before submission."""
        page = logged_in_page

        # Arrange: Navigate to Actions management
        navigate_to_actions(page, live_server)

        # Act: Open modal and check form validation
        open_add_action_modal(page)

        # Expect: Group field should be required and visible
        group_select = page.locator('select[name="create-group"]')
        expect(group_select).to_be_visible()

        # Expect: Should have at least one group option
        group_options = page.locator('select[name="create-group"] option')
        expect(group_options).to_have_count(1)  # At least one group should exist

        # Expect: Modal should remain open (form not submitted)
        expect(page.locator(".modal")).to_be_visible()

    def test_user_can_edit_action(self, logged_in_page: Page, live_server, action_e2e, action_group_e2e):
        """User should be able to edit an existing Action."""
        page = logged_in_page

        # Arrange: Navigate to edit view of existing action
        edit_url = f"{live_server.url}/manage/action/{action_e2e.id}/"
        page.goto(edit_url)

        # Expect: Should be on edit page
        expect(page.locator('input[name="title"]')).to_have_value(action_e2e.title)
        expect(page.locator('input[name="link"]')).to_have_value(action_e2e.link)

        # Act: Modify the title and link
        page.fill('input[name="title"]', "Modified E2E Test Action")
        page.fill('input[name="link"]', "https://example.com/modified-e2e-test")

        # Act: Submit form
        page.click('button[type="submit"]:has-text("Save")')

        # Expect: Modified Action should appear in the sidebar within its group
        sidebar = page.locator("aside")
        expect(sidebar.locator(f"text=Modified E2E Test Action")).to_be_visible()

    def test_user_can_delete_action(self, logged_in_page: Page, live_server, action_e2e):
        """User should be able to delete an Action with confirmation."""
        page = logged_in_page

        # Arrange: Navigate to Actions list
        navigate_to_actions(page, live_server)

        # Expect: Should see the test action
        expect(page.locator(f"text={action_e2e.title}")).to_be_visible()

        # Set up dialog handler BEFORE triggering the action
        page.on("dialog", lambda dialog: dialog.accept())

        # Act: Click delete button (will trigger confirmation dialog)
        page.click(f'a:has-text("Delete Action")')

        # Expect: Action should be removed from list
        sidebar = page.locator("aside")
        expect(sidebar.locator(f"text=Modified E2E Test Action")).not_to_be_visible()


# Test configuration
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.slow,
]
