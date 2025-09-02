"""
Unit tests for order management views.
"""

from django.urls import reverse
from unittest.mock import patch

from lfs.order.models import Order
import lfs.order.settings


class TestOrderListView:
    """Test OrderListView functionality."""

    def test_order_list_view_get(self, authenticated_client, multiple_orders):
        """Test GET request to order list view."""
        url = reverse("lfs_orders")
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert "orders_with_data" in response.context
        assert "states" in response.context
        assert "page" in response.context

    def test_order_list_view_with_filters(self, authenticated_client, multiple_orders):
        """Test order list view with filters applied."""
        # First apply filters using the ApplyOrderFiltersView
        filter_url = reverse("lfs_set_order_filter")
        filter_data = {
            "name": "Customer1",
            "state": "1",
        }
        authenticated_client.post(filter_url, filter_data)

        # Now check that the order list view shows the filters
        url = reverse("lfs_orders")
        response = authenticated_client.get(url)

        assert response.status_code == 200
        # The filters should be in the context
        assert response.context["name"] == "Customer1"
        assert response.context["state_id"] == "1"

    def test_order_list_view_pagination(self, authenticated_client, multiple_orders):
        """Test order list view pagination."""
        url = reverse("lfs_orders")
        response = authenticated_client.get(url, {"page": 1})

        assert response.status_code == 200
        assert "page" in response.context
        assert hasattr(response.context["page"], "paginator")

    def test_order_list_view_permission_required(self, client, multiple_orders):
        """Test that order list view requires proper permissions."""
        url = reverse("lfs_orders")
        response = client.get(url)

        # Should redirect to login or return 403
        assert response.status_code in [302, 403]


class TestOrderDataView:
    """Test OrderDataView functionality."""

    def test_order_data_view_get(self, authenticated_client, order_with_items):
        """Test GET request to order data view."""
        url = reverse("lfs_manage_order", kwargs={"order_id": order_with_items.id})
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert "current_order" in response.context
        assert "order_items" in response.context
        assert "order_total" in response.context
        assert response.context["current_order"] == order_with_items

    def test_order_data_view_with_nonexistent_order(self, authenticated_client):
        """Test order data view with non-existent order."""
        url = reverse("lfs_manage_order", kwargs={"order_id": 99999})
        response = authenticated_client.get(url)

        assert response.status_code == 404

    def test_order_data_view_permission_required(self, client, order):
        """Test that order data view requires proper permissions."""
        url = reverse("lfs_manage_order", kwargs={"order_id": order.id})
        response = client.get(url)

        # Should redirect to login or return 403
        assert response.status_code in [302, 403]

    def test_order_data_view_context_data(self, authenticated_client, order_with_items):
        """Test that order data view provides correct context data."""
        url = reverse("lfs_manage_order", kwargs={"order_id": order_with_items.id})
        response = authenticated_client.get(url)

        context = response.context
        assert "order_total" in context
        assert "order_products" in context
        assert "customer_name" in context
        assert "order_items" in context
        assert "active_tab" in context
        assert context["active_tab"] == "data"


class TestApplyOrderFiltersView:
    """Test ApplyOrderFiltersView functionality."""

    def test_apply_order_filters_post(self, authenticated_client, order):
        """Test POST request to apply order filters."""
        url = reverse("lfs_set_order_filter")
        data = {
            "name": "John",
            "state": "1",
            "start": "2024-01-01",
            "end": "2024-12-31",
            "order-id": str(order.id),
        }

        response = authenticated_client.post(url, data)

        assert response.status_code == 302
        assert response.url == reverse("lfs_manage_order", kwargs={"order_id": order.id})

    def test_apply_order_filters_redirects_to_orders_list(self, authenticated_client):
        """Test that applying filters without order-id redirects to orders list."""
        url = reverse("lfs_set_order_filter")
        data = {
            "name": "John",
            "state": "1",
        }

        response = authenticated_client.post(url, data)

        assert response.status_code == 302
        assert response.url == reverse("lfs_orders")

    def test_apply_order_filters_saves_to_session(self, authenticated_client, order):
        """Test that filters are saved to session."""
        url = reverse("lfs_set_order_filter")
        data = {
            "name": "John",
            "state": "1",
            "order-id": str(order.id),
        }

        response = authenticated_client.post(url, data)

        # Check that filters are saved in session
        session_filters = authenticated_client.session.get("order-filters", {})
        assert session_filters["name"] == "John"
        assert session_filters["state"] == "1"

    def test_apply_order_filters_clears_empty_values(self, authenticated_client, order):
        """Test that empty filter values are removed from session."""
        # First set some filters
        authenticated_client.session["order-filters"] = {
            "name": "John",
            "state": "1",
            "start": "2024-01-01",
        }
        authenticated_client.session.save()

        url = reverse("lfs_set_order_filter")
        data = {
            "name": "",  # Empty name should clear it
            "state": "1",
            "order-id": str(order.id),
        }

        response = authenticated_client.post(url, data)

        # Check that empty name is removed
        session_filters = authenticated_client.session.get("order-filters", {})
        assert "name" not in session_filters
        assert session_filters["state"] == "1"


class TestResetOrderFiltersView:
    """Test ResetOrderFiltersView functionality."""

    def test_reset_order_filters(self, authenticated_client, order):
        """Test resetting order filters."""
        # Set some filters first
        authenticated_client.session["order-filters"] = {
            "name": "John",
            "state": "1",
        }
        authenticated_client.session.save()

        url = reverse("lfs_reset_order_filters")
        response = authenticated_client.get(url, {"order_id": order.id})

        assert response.status_code == 302
        assert response.url == reverse("lfs_manage_order", kwargs={"order_id": order.id})

        # Check that filters are cleared
        assert "order-filters" not in authenticated_client.session

    def test_reset_order_filters_redirects_to_orders_list(self, authenticated_client):
        """Test that resetting filters without order_id redirects to orders list."""
        url = reverse("lfs_reset_order_filters")
        response = authenticated_client.get(url)

        assert response.status_code == 302
        assert response.url == reverse("lfs_orders")


class TestApplyPredefinedOrderFilterView:
    """Test ApplyPredefinedOrderFilterView functionality."""

    def test_apply_today_filter(self, authenticated_client, order):
        """Test applying today filter."""
        url = reverse("lfs_apply_predefined_order_filter", kwargs={"filter_type": "today"})
        response = authenticated_client.get(url)

        assert response.status_code == 302
        assert response.url == reverse("lfs_orders")

        # Check that start date is set
        session_filters = authenticated_client.session.get("order-filters", {})
        assert "start" in session_filters

    def test_apply_week_filter(self, authenticated_client, order):
        """Test applying week filter."""
        url = reverse("lfs_apply_predefined_order_filter", kwargs={"filter_type": "week"})
        response = authenticated_client.get(url)

        assert response.status_code == 302
        assert response.url == reverse("lfs_orders")

    def test_apply_month_filter(self, authenticated_client, order):
        """Test applying month filter."""
        url = reverse("lfs_apply_predefined_order_filter", kwargs={"filter_type": "month"})
        response = authenticated_client.get(url)

        assert response.status_code == 302
        assert response.url == reverse("lfs_orders")

    def test_apply_invalid_filter(self, authenticated_client, order):
        """Test applying invalid filter type."""
        url = reverse("lfs_apply_predefined_order_filter", kwargs={"filter_type": "invalid"})
        response = authenticated_client.get(url)

        assert response.status_code == 302
        assert response.url == reverse("lfs_orders")


class TestOrderDeleteView:
    """Test OrderDeleteView functionality."""

    def test_order_delete_view_get(self, authenticated_client, order):
        """Test GET request to order delete view."""
        url = reverse("lfs_delete_order", kwargs={"order_id": order.id})
        response = authenticated_client.get(url)

        # DirectDeleteMixin deletes immediately on GET, so we expect a redirect
        assert response.status_code == 302
        assert response.url == reverse("lfs_orders")

    def test_order_delete_view_post(self, authenticated_client, order):
        """Test POST request to delete order."""
        url = reverse("lfs_delete_order", kwargs={"order_id": order.id})
        response = authenticated_client.post(url)

        assert response.status_code == 302
        assert response.url == reverse("lfs_orders")

        # Check that order is deleted
        assert not Order.objects.filter(id=order.id).exists()

    def test_order_delete_view_permission_required(self, client, order):
        """Test that order delete view requires proper permissions."""
        url = reverse("lfs_delete_order", kwargs={"order_id": order.id})
        response = client.post(url)

        # Should redirect to login or return 403
        assert response.status_code in [302, 403]


class TestChangeOrderState:
    """Test change_order_state function."""

    def test_change_order_state_success(self, authenticated_client, order):
        """Test successful order state change."""
        url = reverse("lfs_change_order_state")
        data = {
            "order-id": str(order.id),
            "new-state": "2",  # Change to different state
        }

        response = authenticated_client.post(url, data)

        assert response.status_code == 302
        assert response.url == reverse("lfs_manage_order", kwargs={"order_id": order.id})

        # Check that order state is updated
        order.refresh_from_db()
        assert order.state == 2

    def test_change_order_state_invalid_state(self, authenticated_client, order):
        """Test order state change with invalid state."""
        url = reverse("lfs_change_order_state")
        data = {
            "order-id": str(order.id),
            "new-state": "invalid",
        }

        response = authenticated_client.post(url, data)

        assert response.status_code == 302
        # Order state should remain unchanged
        order.refresh_from_db()
        assert order.state == 1  # Original state

    def test_change_order_state_nonexistent_order(self, authenticated_client):
        """Test order state change with non-existent order."""
        url = reverse("lfs_change_order_state")
        data = {
            "order-id": "99999",
            "new-state": "2",
        }

        response = authenticated_client.post(url, data)

        assert response.status_code == 404

    def test_change_order_state_updates_timestamp(self, authenticated_client, order):
        """Test that order state change updates state_modified timestamp."""
        original_timestamp = order.state_modified

        url = reverse("lfs_change_order_state")
        data = {
            "order-id": str(order.id),
            "new-state": "2",
        }

        response = authenticated_client.post(url, data)

        order.refresh_from_db()
        assert order.state_modified != original_timestamp

    def test_change_order_state_permission_required(self, client, order):
        """Test that order state change requires proper permissions."""
        url = reverse("lfs_change_order_state")
        data = {
            "order-id": str(order.id),
            "new-state": "2",
        }

        response = client.post(url, data)

        # Should redirect to login or return 403
        assert response.status_code in [302, 403]

    @patch("lfs.core.signals.order_sent.send")
    @patch("lfs.core.signals.order_paid.send")
    @patch("lfs.core.signals.order_state_changed.send")
    def test_change_order_state_triggers_signals(
        self, mock_state_changed, mock_paid, mock_sent, authenticated_client, order
    ):
        """Test that order state change triggers appropriate signals."""
        url = reverse("lfs_change_order_state")
        data = {
            "order-id": str(order.id),
            "new-state": str(lfs.order.settings.SENT),
        }

        response = authenticated_client.post(url, data)

        # Check that signals are called
        mock_sent.assert_called_once()
        mock_state_changed.assert_called_once()


class TestSendOrder:
    """Test send_order function."""

    @patch("lfs.mail.utils.send_order_received_mail")
    def test_send_order_success(self, mock_send_mail, authenticated_client, order):
        """Test successful order sending."""
        url = reverse("lfs_send_order", kwargs={"order_id": order.id})
        response = authenticated_client.get(url)

        assert response.status_code == 302
        assert response.url == reverse("lfs_manage_order", kwargs={"order_id": order.id})

        # Check that mail function is called
        mock_send_mail.assert_called_once()

    def test_send_order_nonexistent_order(self, authenticated_client):
        """Test sending non-existent order."""
        url = reverse("lfs_send_order", kwargs={"order_id": 99999})
        response = authenticated_client.get(url)

        assert response.status_code == 404

    def test_send_order_permission_required(self, client, order):
        """Test that send order requires proper permissions."""
        url = reverse("lfs_send_order", kwargs={"order_id": order.id})
        response = client.get(url)

        # Should redirect to login or return 403
        assert response.status_code in [302, 403]


class TestLegacyViews:
    """Test legacy function-based views."""

    def test_manage_orders_with_orders(self, authenticated_client, order):
        """Test manage_orders redirects to first order when orders exist."""
        url = reverse("lfs_manage_orders")
        response = authenticated_client.get(url)

        assert response.status_code == 302
        assert response.url == reverse("lfs_manage_order", kwargs={"order_id": order.id})

    def test_manage_orders_without_orders(self, authenticated_client):
        """Test manage_orders redirects to orders list when no orders exist."""
        url = reverse("lfs_manage_orders")
        response = authenticated_client.get(url)

        assert response.status_code == 302
        assert response.url == reverse("lfs_orders")

    def test_orders_view_delegates_to_class_view(self, authenticated_client, multiple_orders):
        """Test that orders_view delegates to OrderListView."""
        url = reverse("lfs_orders")
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert "orders_with_data" in response.context

    def test_order_view_delegates_to_class_view(self, authenticated_client, order):
        """Test that order_view delegates to OrderDataView."""
        url = reverse("lfs_manage_order", kwargs={"order_id": order.id})
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert "current_order" in response.context
        assert response.context["current_order"] == order


class TestOrderFiltering:
    """Test order filtering functionality."""

    def test_filter_by_customer_name(self, authenticated_client, multiple_orders):
        """Test filtering orders by customer name."""
        # Apply filter
        url = reverse("lfs_set_order_filter")
        data = {
            "name": "Customer1",
        }
        authenticated_client.post(url, data)

        # Check filtered results
        url = reverse("lfs_orders")
        response = authenticated_client.get(url)

        assert response.status_code == 200
        # Should have filtered results (implementation depends on OrderFilterService)

    def test_filter_by_state(self, authenticated_client, multiple_orders):
        """Test filtering orders by state."""
        # Apply filter
        url = reverse("lfs_set_order_filter")
        data = {
            "state": "1",
        }
        authenticated_client.post(url, data)

        # Check filtered results
        url = reverse("lfs_orders")
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert response.context["state_id"] == "1"

    def test_filter_by_date_range(self, authenticated_client, multiple_orders):
        """Test filtering orders by date range."""
        # Apply filter
        url = reverse("lfs_set_order_filter")
        data = {
            "start": "2024-01-01",
            "end": "2024-12-31",
        }
        authenticated_client.post(url, data)

        # Check filtered results
        url = reverse("lfs_orders")
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert response.context["start"] == "2024-01-01"
        assert response.context["end"] == "2024-12-31"

    def test_combined_filters(self, authenticated_client, multiple_orders):
        """Test combining multiple filters."""
        # Apply combined filters
        url = reverse("lfs_set_order_filter")
        data = {
            "name": "Customer1",
            "state": "1",
            "start": "2024-01-01",
        }
        authenticated_client.post(url, data)

        # Check filtered results
        url = reverse("lfs_orders")
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert response.context["name"] == "Customer1"
        assert response.context["state_id"] == "1"
        assert response.context["start"] == "2024-01-01"
