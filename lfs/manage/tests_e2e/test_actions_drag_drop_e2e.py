"""
End-to-End tests for Actions Drag & Drop functionality.

Tests drag and drop interactions for reordering actions within groups
and moving actions between different groups.

Following TDD principles:
- Test user behavior, not implementation
- One workflow per test method
- Arrange-Act-Assert structure
"""

import pytest
from playwright.sync_api import Page, expect


def navigate_to_actions(page: Page, live_server):
    """Helper to navigate to Actions management page."""
    page.goto(f"{live_server.url}/manage/actions/")
    page.wait_for_load_state("networkidle")
    page.wait_for_url(lambda url: "manage" in url and ("action" in url or "no-actions" in url), timeout=10000)
    page.wait_for_load_state("networkidle")


def perform_drag_and_drop(page: Page, source_selector: str, target_selector: str):
    """Helper to perform drag and drop operation."""
    # Get source and target elements
    source = page.locator(source_selector)
    target = page.locator(target_selector)

    # Ensure source element is visible
    expect(source).to_be_visible()

    # For target, be more flexible - it might be hidden or have different visibility rules
    try:
        expect(target).to_be_visible()
    except:
        # If target is not visible, try to find it differently or document behavior
        print(f"Target element not visible: {target_selector}")
        # Still attempt the drag operation to document behavior

    # Perform drag and drop
    try:
        source.drag_to(target)
        print(f"Drag and drop attempted from {source_selector} to {target_selector}")
    except Exception as e:
        print(f"Drag and drop failed: {e}")

    # Wait for any HTMX or JavaScript to process the change
    page.wait_for_timeout(1000)


def get_action_position_in_group(page: Page, action_title: str, group_id: int) -> int:
    """Helper to get the position of an action within its group."""
    group_actions = page.locator(f'.action-group[data-list="{group_id}"] .action-item')

    for i in range(group_actions.count()):
        action = group_actions.nth(i)
        if action_title in action.text_content():
            return i

    return -1  # Not found


@pytest.mark.e2e
@pytest.mark.django_db
class TestActionDragAndDrop:
    """Complete Action drag and drop user journey tests."""

    def test_user_can_reorder_actions_within_group(
        self, logged_in_page: Page, live_server, multiple_actions_same_group_e2e
    ):
        """User should be able to reorder actions within the same group using drag and drop."""
        page = logged_in_page

        # Arrange: Navigate to Actions management
        navigate_to_actions(page, live_server)

        # Get the actions from the fixture (all in the same group)
        actions = multiple_actions_same_group_e2e

        if len(actions) < 2:
            pytest.skip("Need at least 2 actions for reordering test")

        # Expect: Actions should be visible in the sidebar
        sidebar = page.locator("aside")
        first_action = actions[0]
        second_action = actions[1]

        # Use simpler selectors to find actions
        first_action_element = sidebar.locator(f"text={first_action.title}")
        second_action_element = sidebar.locator(f"text={second_action.title}")

        expect(first_action_element).to_be_visible()
        expect(second_action_element).to_be_visible()

        # Get initial positions BEFORE drag and drop
        group_id = first_action.group.id
        group_actions = sidebar.locator(f'.action-group[data-list="{group_id}"] .action-item, .action-item')

        # Find initial positions of our actions
        initial_first_position = -1
        initial_second_position = -1

        for i in range(group_actions.count()):
            action_element = group_actions.nth(i)
            action_text = action_element.text_content()

            if first_action.title in action_text:
                initial_first_position = i
            elif second_action.title in action_text:
                initial_second_position = i

        # Act: Attempt drag and drop between the two actions
        try:
            # Try to find draggable elements (could be .action-item or similar)
            first_draggable = sidebar.locator(f".action-item:has-text('{first_action.title}')").first
            second_draggable = sidebar.locator(f".action-item:has-text('{second_action.title}')").first

            # If .action-item doesn't work, fall back to any element containing the text
            if first_draggable.count() == 0:
                first_draggable = sidebar.locator(f":has-text('{first_action.title}')").first
                second_draggable = sidebar.locator(f":has-text('{second_action.title}')").first

            # Perform drag and drop
            first_draggable.drag_to(second_draggable)
            page.wait_for_timeout(2000)
        except Exception as e:
            print(f"Drag and drop failed: {e}")

        # Get positions AFTER drag and drop
        group_actions = sidebar.locator(f'.action-group[data-list="{group_id}"] .action-item, .action-item')

        # Find final positions of our actions
        final_first_position = -1
        final_second_position = -1

        for i in range(group_actions.count()):
            action_element = group_actions.nth(i)
            action_text = action_element.text_content()

            if first_action.title in action_text:
                final_first_position = i
            elif second_action.title in action_text:
                final_second_position = i

        print(f"AFTER drag & drop - First: {final_first_position}, Second: {final_second_position}")

        # Expect: Actions should still be visible
        expect(sidebar.locator(f"text={first_action.title}")).to_be_visible()
        expect(sidebar.locator(f"text={second_action.title}")).to_be_visible()

        # Assert: Test the reordering with actual assertions
        assert initial_first_position != -1, f"Could not find initial position of '{first_action.title}'"
        assert initial_second_position != -1, f"Could not find initial position of '{second_action.title}'"
        assert final_first_position != -1, f"Could not find final position of '{first_action.title}'"
        assert final_second_position != -1, f"Could not find final position of '{second_action.title}'"

        # Assert: Positions should have changed after drag and drop
        positions_changed = (
            initial_first_position != final_first_position or initial_second_position != final_second_position
        )

        assert positions_changed, (
            f"Drag and drop failed: Positions remained the same. "
            f"Before: First={initial_first_position}, Second={initial_second_position}. "
            f"After: First={final_first_position}, Second={final_second_position}"
        )

        # Assert: First action should now be after second action (moved down)
        assert final_first_position > final_second_position, (
            f"Expected first action to be below second action after drag and drop. "
            f"Final positions: First={final_first_position}, Second={final_second_position}"
        )

    def test_user_can_move_action_in_a_empty_group(
        self, logged_in_page: Page, live_server, multiple_action_groups_e2e, action_with_group_e2e
    ):
        """User should be able to move an action from one group to another using drag and drop."""
        page = logged_in_page

        # Arrange: Navigate to Actions management
        navigate_to_actions(page, live_server)

        # Get the action and groups from fixtures
        action = action_with_group_e2e
        source_group = action.group
        target_group = None

        # Find a different group to move to
        for group in multiple_action_groups_e2e:
            if group.id != source_group.id:
                target_group = group
                break

        if not target_group:
            pytest.skip("Need at least 2 groups for moving test")

        # Expect: Action should be visible in the sidebar
        sidebar = page.locator("aside")
        expect(sidebar.locator(f"text={action.title}")).to_be_visible()

        # Expect: Both groups should be visible (use exact match to avoid conflicts)
        expect(sidebar.get_by_text(source_group.name, exact=True)).to_be_visible()
        expect(sidebar.get_by_text(target_group.name, exact=True)).to_be_visible()

        # Act: Drag the action to the empty target group
        action_element = sidebar.locator(f".action-item[data-id='{action.id}']").first

        # Get the target group section
        target_group_section = sidebar.locator(f".action-group[data-list='{target_group.id}']").first

        # Drag the action to the target group section
        action_element.drag_to(target_group_section)
        page.wait_for_timeout(2000)

        # Assert: Check if action moved to the empty target group
        target_group_section = sidebar.locator(f".action-group[data-list='{target_group.id}']")
        action_in_target_group = target_group_section.locator(f".action-item[data-id='{action.id}']")

        # Check if the action is now in the target group
        expect(action_in_target_group).to_be_visible()

        source_group_section = sidebar.locator(f".action-group[data-list='{source_group.id}']")
        action_not_in_source_group = source_group_section.locator(f".action-item[data-id='{action.id}']")

        # Check if the action is not in the source group anymore
        expect(action_not_in_source_group).not_to_be_visible()

    def test_user_can_move_action_between_populated_groups(
        self, logged_in_page: Page, live_server, multiple_actions_e2e
    ):
        """User should be able to move an action from one populated group to another populated group."""
        page = logged_in_page

        # Arrange: Navigate to Actions management
        navigate_to_actions(page, live_server)

        # Get actions from different groups (multiple_actions_e2e has actions in different groups)
        actions = multiple_actions_e2e

        if len(actions) < 2:
            pytest.skip("Need at least 2 actions in different groups")

        # Get first action and its group (source)
        source_action = actions[0]
        source_group = source_action.group

        # Get second action and its group (target)
        target_action = actions[1]
        target_group = target_action.group

        if source_group.id == target_group.id:
            pytest.skip("Need actions in different groups")

        # Expect: Both actions should be visible in their respective groups
        sidebar = page.locator("aside")
        expect(sidebar.locator(f"text={source_action.title}")).to_be_visible()
        expect(sidebar.locator(f"text={target_action.title}")).to_be_visible()

        # Expect: Both groups should be visible
        expect(sidebar.get_by_text(source_group.name, exact=True)).to_be_visible()
        expect(sidebar.get_by_text(target_group.name, exact=True)).to_be_visible()

        # Act: Drag the source action to the target group (which already has the target action)
        source_action_element = sidebar.locator(f".action-item[data-id='{source_action.id}']").first
        target_group_section = sidebar.locator(f".action-group[data-list='{target_group.id}']").first

        # Drag source action to target group
        source_action_element.drag_to(target_group_section)
        page.wait_for_timeout(2000)

        # Assert: Check if source action moved to the target group
        target_group_section = sidebar.locator(f".action-group[data-list='{target_group.id}']")
        source_action_in_target_group = target_group_section.locator(f".action-item[data-id='{source_action.id}']")

        # Source action should now be in target group
        expect(source_action_in_target_group).to_be_visible()

        # Target action should still be in target group
        target_action_in_target_group = target_group_section.locator(f".action-item[data-id='{target_action.id}']")
        expect(target_action_in_target_group).to_be_visible()

        # Source action should no longer be in source group
        source_group_section = sidebar.locator(f".action-group[data-list='{source_group.id}']")
        source_action_not_in_source_group = source_group_section.locator(f".action-item[data-id='{source_action.id}']")
        expect(source_action_not_in_source_group).not_to_be_visible()


# Test configuration
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.slow,
]
