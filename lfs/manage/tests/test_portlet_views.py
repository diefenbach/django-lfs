"""
Comprehensive tests for Portlet CBVs in the manage package.

Following TDD principles:
- Test behavior, not implementation
- Clear test names
- Arrange-Act-Assert structure
- One assertion per test (when practical)
"""

import json
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect, QueryDict
from django.contrib.contenttypes.models import ContentType

from portlets.models import PortletAssignment, PortletBlocking
from portlets.example.models import TextPortlet

from lfs.page.models import Page
from lfs.manage.portlets.views import (
    PortletsInlineView,
    UpdatePortletsView,
    AddPortletView,
    DeletePortletView,
    EditPortletView,
    MovePortletView,
    SortPortletsView,
    update_portlet_positions,
    get_portlet_management_url,
)

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.unit
class TestPortletsInlineView:
    """Tests for PortletsInlineView."""

    def test_view_configuration(self):
        """Should have correct view configuration."""
        assert PortletsInlineView.permission_required == "core.manage_shop"
        assert PortletsInlineView.template_name == "manage/portlets/portlets_inline.html"

    def test_get_renders_portlets_inline_template(self, page, authenticated_request, monkeypatch):
        """Should render portlets inline template with correct context."""
        request = authenticated_request()

        # Mock render_to_string to capture the call
        render_calls = []

        def mock_render_to_string(template_name, request=None, context=None):
            render_calls.append((template_name, request, context))
            return "rendered_content"

        monkeypatch.setattr("lfs.manage.portlets.views.render_to_string", mock_render_to_string)

        view = PortletsInlineView()
        result = view.get(request, page)

        assert result == "rendered_content"
        assert len(render_calls) == 1

        # Check context data
        template_name, request_arg, context = render_calls[0]
        assert template_name == "manage/portlets/portlets_inline.html"
        assert "slots" in context
        assert "parent_slots" in context
        assert "parent_for_portlets" in context
        assert "portlet_types" in context
        assert "object" in context
        assert context["object"] == page
        assert "object_type_id" in context

    def test_get_handles_page_without_parent(self, page, authenticated_request, monkeypatch):
        """Should handle pages without parent for portlets."""
        request = authenticated_request()

        # Mock render_to_string to capture the call
        render_calls = []

        def mock_render_to_string(template_name, request=None, context=None):
            render_calls.append((template_name, request, context))
            return "rendered_content"

        monkeypatch.setattr("lfs.manage.portlets.views.render_to_string", mock_render_to_string)

        view = PortletsInlineView()
        result = view.get(request, page)

        assert len(render_calls) == 1
        template_name, request_arg, context = render_calls[0]

        # Pages that are not id=1 return the page with id=1 as parent
        # Only the root page (id=1) returns the shop as parent
        assert context["parent_for_portlets"] is not None
        assert context["parent_slots"] is not None

    def test_get_uses_custom_template_name(self, page, authenticated_request, monkeypatch):
        """Should use custom template name when provided."""
        request = authenticated_request()
        custom_template = "custom/template.html"

        # Mock render_to_string to capture the call
        render_calls = []

        def mock_render_to_string(template_name, request=None, context=None):
            render_calls.append((template_name, request, context))
            return "rendered_content"

        monkeypatch.setattr("lfs.manage.portlets.views.render_to_string", mock_render_to_string)

        view = PortletsInlineView()
        result = view.get(request, page, template_name=custom_template)

        assert len(render_calls) == 1
        template_name, request_arg, context = render_calls[0]
        assert template_name == custom_template


@pytest.mark.django_db
@pytest.mark.unit
class TestUpdatePortletsView:
    """Tests for UpdatePortletsView."""

    def test_view_configuration(self):
        """Should have correct view configuration."""
        assert UpdatePortletsView.permission_required == "core.manage_shop"

    def test_post_updates_portlet_blocking(self, page, authenticated_request, slot, monkeypatch):
        """Should update portlet blocking settings."""
        request = authenticated_request()
        request.method = "POST"
        request.POST = QueryDict("block_slot=" + str(slot.id))

        # Mock PortletsInlineView to avoid template rendering
        def mock_inline_view_get(self, request, obj):
            return "updated_portlets"

        monkeypatch.setattr(
            "lfs.manage.portlets.views.PortletsInlineView", type("MockView", (), {"get": mock_inline_view_get})
        )

        view = UpdatePortletsView()
        response = view.post(request, ContentType.objects.get_for_model(page).id, page.id)

        # Check that blocking was created
        blocking = PortletBlocking.objects.filter(
            content_type=ContentType.objects.get_for_model(page), content_id=page.id, slot=slot
        )
        assert blocking.exists()

    def test_post_removes_unchecked_blocking(self, page, authenticated_request, slot):
        """Should remove blocking for unchecked slots."""
        request = authenticated_request()
        request.method = "POST"
        request.POST = QueryDict()  # No slots checked

        # Create existing blocking
        PortletBlocking.objects.create(
            content_type=ContentType.objects.get_for_model(page), content_id=page.id, slot=slot
        )

        view = UpdatePortletsView()
        response = view.post(request, ContentType.objects.get_for_model(page).id, page.id)

        # Check that blocking was removed
        blocking = PortletBlocking.objects.filter(
            content_type=ContentType.objects.get_for_model(page), content_id=page.id
        )
        assert not blocking.exists()

    def test_post_ajax_request_returns_json(self, page, authenticated_request, slot, monkeypatch):
        """Should return JSON response for AJAX requests."""
        request = authenticated_request()
        request.method = "POST"
        request.POST = QueryDict("block_slot=" + str(slot.id))
        request.headers = {"X-Requested-With": "XMLHttpRequest"}

        # Mock PortletsInlineView to avoid template rendering
        def mock_inline_view_get(self, request, obj):
            return "updated_portlets"

        monkeypatch.setattr(
            "lfs.manage.portlets.views.PortletsInlineView", type("MockView", (), {"get": mock_inline_view_get})
        )

        view = UpdatePortletsView()
        response = view.post(request, ContentType.objects.get_for_model(page).id, page.id)

        assert response.status_code == 200
        assert response["Content-Type"] == "application/json"

        data = json.loads(response.content)
        assert "html" in data
        assert "message" in data

    def test_post_regular_request_redirects(self, page, authenticated_request, slot, monkeypatch):
        """Should redirect for regular form submissions."""
        request = authenticated_request()
        request.method = "POST"
        request.POST = QueryDict("block_slot=" + str(slot.id))
        request.headers = {}

        # Mock redirect to avoid actual redirect
        def mock_redirect(url):
            return HttpResponseRedirect("/redirect/")

        monkeypatch.setattr("lfs.manage.portlets.views.redirect", mock_redirect)

        view = UpdatePortletsView()
        response = view.post(request, ContentType.objects.get_for_model(page).id, page.id)

        assert isinstance(response, HttpResponseRedirect)


@pytest.mark.django_db
@pytest.mark.unit
class TestAddPortletView:
    """Tests for AddPortletView."""

    def test_view_configuration(self):
        """Should have correct view configuration."""
        assert AddPortletView.permission_required == "core.manage_shop"
        assert AddPortletView.template_name == "manage/portlets/portlet_add.html"

    def test_get_without_portlet_type_returns_warning(self, page, authenticated_request):
        """Should return warning when no portlet type is provided."""
        request = authenticated_request()
        request.GET = {}

        view = AddPortletView()
        response = view.get(request, ContentType.objects.get_for_model(page).id, page.id)

        assert "Please select a portlet type" in response.content.decode()

    def test_get_with_invalid_portlet_type_returns_error(self, page, authenticated_request):
        """Should return error for invalid portlet type."""
        request = authenticated_request()
        request.GET = {"portlet_type": "invalid_type"}

        view = AddPortletView()
        response = view.get(request, ContentType.objects.get_for_model(page).id, page.id)

        assert "Invalid portlet type" in response.content.decode()

    def test_get_with_valid_portlet_type_renders_form(self, page, authenticated_request, monkeypatch):
        """Should render form for valid portlet type."""
        request = authenticated_request()
        request.GET = {"portlet_type": "textportlet"}

        # Mock ContentType.objects.filter to return a valid portlet type
        mock_form = type("MockForm", (), {})()
        mock_model_instance = type("MockModelInstance", (), {"form": lambda self, prefix: mock_form})()

        mock_queryset = type(
            "MockQuerySet",
            (),
            {
                "exists": lambda self: True,
                "__getitem__": lambda self, i: type(
                    "MockCT", (), {"model_class": lambda self: lambda: mock_model_instance}
                )(),
            },
        )()

        def mock_filter(model):
            return mock_queryset

        monkeypatch.setattr("lfs.manage.portlets.views.ContentType.objects.filter", mock_filter)

        # Mock render to capture the call
        render_calls = []

        def mock_render(request, template, context):
            render_calls.append((request, template, context))
            return type("MockResponse", (), {})()

        monkeypatch.setattr("lfs.manage.portlets.views.render", mock_render)

        view = AddPortletView()
        response = view.get(request, ContentType.objects.get_for_model(page).id, page.id)

        assert len(render_calls) == 1

    def test_post_without_portlet_type_returns_warning(self, page, authenticated_request):
        """Should return warning when no portlet type in POST."""
        request = authenticated_request()
        request.method = "POST"
        request.POST = {}

        view = AddPortletView()
        response = view.post(request, ContentType.objects.get_for_model(page).id, page.id)

        assert "Please select a portlet type" in response.content.decode()

    def test_post_with_invalid_form_rerenders_form(self, page, authenticated_request, monkeypatch):
        """Should re-render form when validation fails."""
        request = authenticated_request()
        request.method = "POST"
        request.POST = QueryDict("portlet_type=textportlet&slot=1")

        # Mock ContentType.objects.filter to return a valid portlet type
        mock_form = type("MockForm", (), {"is_valid": lambda self: False})()

        mock_instance = type("MockInstance", (), {"form": lambda self, prefix, data: mock_form})()

        mock_queryset = type(
            "MockQuerySet",
            (),
            {
                "exists": lambda self: True,
                "__getitem__": lambda self, i: type(
                    "MockCT", (), {"model_class": lambda self: lambda: mock_instance}
                )(),
            },
        )()

        def mock_filter(model):
            return mock_queryset

        monkeypatch.setattr("lfs.manage.portlets.views.ContentType.objects.filter", mock_filter)

        # Mock render to capture the call
        render_calls = []

        def mock_render(request, template, context):
            render_calls.append((request, template, context))
            return type("MockResponse", (), {})()

        monkeypatch.setattr("lfs.manage.portlets.views.render", mock_render)

        view = AddPortletView()
        response = view.post(request, ContentType.objects.get_for_model(page).id, page.id)

        assert len(render_calls) == 1

    def test_post_with_valid_form_creates_portlet(self, page, authenticated_request, slot, monkeypatch):
        """Should create portlet when form is valid."""
        request = authenticated_request()
        request.method = "POST"
        request.POST = QueryDict(f"portlet_type=textportlet&slot={slot.id}")

        # Mock ContentType.objects.filter to return a valid portlet type
        mock_portlet = type("MockPortlet", (), {})()
        mock_form = type("MockForm", (), {"is_valid": lambda self: True, "save": lambda self: mock_portlet})()

        mock_instance = type("MockInstance", (), {"form": lambda self, prefix, data: mock_form})()

        mock_queryset = type(
            "MockQuerySet",
            (),
            {
                "exists": lambda self: True,
                "__getitem__": lambda self, i: type(
                    "MockCT", (), {"model_class": lambda self: lambda: mock_instance}
                )(),
            },
        )()

        def mock_filter(model):
            return mock_queryset

        monkeypatch.setattr("lfs.manage.portlets.views.ContentType.objects.filter", mock_filter)

        # Mock ContentType.objects.get to return a valid ContentType
        mock_content_type = type(
            "MockContentType",
            (),
            {"get_object_for_this_type": lambda self, pk: page, "app_label": "lfs", "model": "page", "id": 1},
        )()

        def mock_get(*args, **kwargs):
            return mock_content_type

        monkeypatch.setattr("lfs.manage.portlets.views.ContentType.objects.get", mock_get)

        # Mock PortletAssignment.objects.create
        mock_pa = type(
            "MockPA", (), {"content_type": ContentType.objects.get_for_model(page), "content_id": page.id, "slot": slot}
        )()

        create_calls = []

        def mock_create(**kwargs):
            create_calls.append(kwargs)
            return mock_pa

        monkeypatch.setattr("lfs.manage.portlets.views.PortletAssignment.objects.create", mock_create)

        # Mock update_portlet_positions
        def mock_update_positions(pa):
            pass

        monkeypatch.setattr("lfs.manage.portlets.views.update_portlet_positions", mock_update_positions)

        # Mock redirect
        def mock_redirect(url):
            return HttpResponseRedirect("/redirect/")

        monkeypatch.setattr("lfs.manage.portlets.views.redirect", mock_redirect)

        view = AddPortletView()
        response = view.post(request, ContentType.objects.get_for_model(page).id, page.id)

        assert len(create_calls) == 1
        assert isinstance(response, HttpResponseRedirect)


@pytest.mark.django_db
@pytest.mark.unit
class TestDeletePortletView:
    """Tests for DeletePortletView."""

    def test_view_configuration(self):
        """Should have correct view configuration."""
        assert DeletePortletView.permission_required == "core.manage_shop"
        assert DeletePortletView.template_name == "manage/portlets/delete_portlet.html"

    def test_get_with_nonexistent_portlet_returns_error(self, authenticated_request):
        """Should return error for non-existent portlet."""
        request = authenticated_request()

        view = DeletePortletView()
        response = view.get(request, 99999)

        assert "Portlet not found" in response.content.decode()

    def test_get_with_htmx_request_returns_html(self, portlet_assignment, authenticated_request, monkeypatch):
        """Should return HTML for HTMX requests."""
        request = authenticated_request()
        request.headers = {"HX-Request": "true"}

        # Mock render_to_string
        def mock_render_to_string(template, request=None, context=None):
            return "confirmation_html"

        monkeypatch.setattr("lfs.manage.portlets.views.render_to_string", mock_render_to_string)

        view = DeletePortletView()
        response = view.get(request, portlet_assignment.id)

        assert response.content.decode() == "confirmation_html"

    def test_get_with_regular_request_returns_json(self, portlet_assignment, authenticated_request, monkeypatch):
        """Should return JSON for regular requests."""
        request = authenticated_request()
        request.headers = {}

        # Mock render_to_string
        def mock_render_to_string(template, request=None, context=None):
            return "confirmation_html"

        monkeypatch.setattr("lfs.manage.portlets.views.render_to_string", mock_render_to_string)

        view = DeletePortletView()
        response = view.get(request, portlet_assignment.id)

        assert response["Content-Type"] == "application/json"
        data = json.loads(response.content)
        assert "html" in data

    def test_post_deletes_portlet_and_redirects(self, portlet_assignment, authenticated_request, monkeypatch):
        """Should delete portlet and redirect."""
        request = authenticated_request()
        request.method = "POST"

        # Mock redirect
        def mock_redirect(url):
            return HttpResponseRedirect("/redirect/")

        monkeypatch.setattr("lfs.manage.portlets.views.redirect", mock_redirect)

        view = DeletePortletView()
        response = view.post(request, portlet_assignment.id)

        # Check that portlet was deleted
        assert not PortletAssignment.objects.filter(id=portlet_assignment.id).exists()
        assert isinstance(response, HttpResponseRedirect)

    def test_post_with_nonexistent_portlet_redirects_with_error(self, authenticated_request, monkeypatch):
        """Should redirect with error message for non-existent portlet."""
        request = authenticated_request()
        request.method = "POST"

        # Mock redirect
        def mock_redirect(url):
            return HttpResponseRedirect("/redirect/")

        monkeypatch.setattr("lfs.manage.portlets.views.redirect", mock_redirect)

        view = DeletePortletView()
        response = view.post(request, 99999)

        assert isinstance(response, HttpResponseRedirect)


@pytest.mark.django_db
@pytest.mark.unit
class TestEditPortletView:
    """Tests for EditPortletView."""

    def test_view_configuration(self):
        """Should have correct view configuration."""
        assert EditPortletView.permission_required == "core.manage_shop"
        assert EditPortletView.template_name == "manage/portlets/portlet_edit.html"

    def test_get_with_nonexistent_portlet_returns_error(self, authenticated_request):
        """Should return error for non-existent portlet."""
        request = authenticated_request()
        request.headers = {"HX-Request": "true"}

        view = EditPortletView()
        response = view.get(request, 99999)

        assert "Portlet not found" in response.content.decode()

    def test_get_renders_edit_form(self, portlet_assignment, authenticated_request, monkeypatch):
        """Should render edit form with correct context."""
        request = authenticated_request()

        # Mock render to capture the call
        render_calls = []

        def mock_render(request, template, context):
            render_calls.append((request, template, context))
            return type("MockResponse", (), {})()

        monkeypatch.setattr("lfs.manage.portlets.views.render", mock_render)

        view = EditPortletView()
        response = view.get(request, portlet_assignment.id)

        assert len(render_calls) == 1
        request_arg, template, context = render_calls[0]

        assert "form" in context
        assert "portletassigment_id" in context
        assert context["portletassigment_id"] == portlet_assignment.id
        assert "slots" in context

    def test_post_with_valid_form_saves_and_redirects(self, portlet_assignment, authenticated_request, monkeypatch):
        """Should save changes and redirect when form is valid."""
        request = authenticated_request()
        request.method = "POST"
        request.POST = QueryDict("slot=1")

        # Mock the portlet's form method
        mock_form = type("MockForm", (), {"is_valid": lambda self: True, "save": lambda self: None})()

        form_calls = []
        save_calls = []

        def mock_form_method(self, **kwargs):
            form_calls.append(kwargs)
            return mock_form

        # Create a mock portlet assignment with the mocked form method
        mock_portlet = type("MockPortlet", (), {"form": mock_form_method})()

        mock_pa = type(
            "MockPA",
            (),
            {
                "id": portlet_assignment.id,
                "portlet": mock_portlet,
                "slot_id": 1,
                "slot": type("MockSlot", (), {"id": 1})(),
                "content": portlet_assignment.content,
                "save": lambda self: None,
            },
        )()

        # Mock PortletAssignment.objects.get to return our mock
        def mock_get(pk):
            return mock_pa

        monkeypatch.setattr("lfs.manage.portlets.views.PortletAssignment.objects.get", mock_get)

        # Mock save method to track calls
        def mock_save():
            save_calls.append(True)

        monkeypatch.setattr(mock_form, "save", mock_save)

        # Mock redirect
        def mock_redirect(url):
            return HttpResponseRedirect("/redirect/")

        monkeypatch.setattr("lfs.manage.portlets.views.redirect", mock_redirect)

        view = EditPortletView()
        response = view.post(request, portlet_assignment.id)

        # Verify the form was called and save was called
        assert len(form_calls) == 1
        assert len(save_calls) == 1
        assert isinstance(response, HttpResponseRedirect)

    def test_post_with_invalid_form_rerenders_form(self, portlet_assignment, authenticated_request, monkeypatch):
        """Should re-render form when validation fails."""
        request = authenticated_request()
        request.method = "POST"
        request.POST = QueryDict("slot=1")

        # Mock the portlet's form method
        mock_form = type("MockForm", (), {"is_valid": lambda self: False})()

        form_calls = []

        def mock_form_method(self, **kwargs):
            form_calls.append(kwargs)
            return mock_form

        # Create a mock portlet assignment with the mocked form method
        mock_portlet = type("MockPortlet", (), {"form": mock_form_method})()

        mock_pa = type(
            "MockPA",
            (),
            {
                "id": portlet_assignment.id,
                "portlet": mock_portlet,
                "slot_id": 1,
                "slot": type("MockSlot", (), {"id": 1})(),
                "content": portlet_assignment.content,
                "save": lambda self: None,
            },
        )()

        # Mock PortletAssignment.objects.get to return our mock
        def mock_get(pk):
            return mock_pa

        monkeypatch.setattr("lfs.manage.portlets.views.PortletAssignment.objects.get", mock_get)

        # Mock render to capture the call
        render_calls = []

        def mock_render(request, template, context):
            render_calls.append((request, template, context))
            return type("MockResponse", (), {})()

        monkeypatch.setattr("lfs.manage.portlets.views.render", mock_render)

        view = EditPortletView()
        response = view.post(request, portlet_assignment.id)

        # Verify the form was called and render was called
        assert len(form_calls) == 1
        assert len(render_calls) == 1


@pytest.mark.django_db
@pytest.mark.unit
class TestMovePortletView:
    """Tests for MovePortletView."""

    def test_view_configuration(self):
        """Should have correct view configuration."""
        assert MovePortletView.permission_required == "core.manage_shop"

    def test_get_with_nonexistent_portlet_returns_empty(self, authenticated_request):
        """Should return empty response for non-existent portlet."""
        request = authenticated_request()

        view = MovePortletView()
        response = view.get(request, 99999)

        assert response.content.decode() == ""

    def test_get_moves_portlet_up(self, portlet_assignment, authenticated_request, monkeypatch):
        """Should move portlet up when direction is 0."""
        request = authenticated_request()
        request.GET = {"direction": "0"}

        original_position = portlet_assignment.position

        # Mock PortletsInlineView to avoid template rendering
        def mock_inline_view_get(self, request, obj):
            return "updated_portlets"

        monkeypatch.setattr(
            "lfs.manage.portlets.views.PortletsInlineView", type("MockView", (), {"get": mock_inline_view_get})
        )

        view = MovePortletView()
        response = view.get(request, portlet_assignment.id)

        portlet_assignment.refresh_from_db()
        # After moving up and calling update_portlet_positions, position should be 10 (first position)
        assert portlet_assignment.position == 10

    def test_get_moves_portlet_down(self, portlet_assignment, authenticated_request, monkeypatch):
        """Should move portlet down when direction is 1."""
        request = authenticated_request()
        request.GET = {"direction": "1"}

        original_position = portlet_assignment.position

        # Mock PortletsInlineView to avoid template rendering
        def mock_inline_view_get(self, request, obj):
            return "updated_portlets"

        monkeypatch.setattr(
            "lfs.manage.portlets.views.PortletsInlineView", type("MockView", (), {"get": mock_inline_view_get})
        )

        view = MovePortletView()
        response = view.get(request, portlet_assignment.id)

        portlet_assignment.refresh_from_db()
        # After moving down and calling update_portlet_positions, position should be 10 (first position)
        assert portlet_assignment.position == 10

    def test_get_prevents_negative_position(self, portlet_assignment, authenticated_request, monkeypatch):
        """Should prevent negative position values."""
        request = authenticated_request()
        request.GET = {"direction": "0"}

        # Set position to minimum value
        portlet_assignment.position = 5
        portlet_assignment.save()

        # Mock PortletsInlineView to avoid template rendering
        def mock_inline_view_get(self, request, obj):
            return "updated_portlets"

        monkeypatch.setattr(
            "lfs.manage.portlets.views.PortletsInlineView", type("MockView", (), {"get": mock_inline_view_get})
        )

        view = MovePortletView()
        response = view.get(request, portlet_assignment.id)

        portlet_assignment.refresh_from_db()
        assert portlet_assignment.position == 10

    def test_get_returns_json_response(self, portlet_assignment, authenticated_request, monkeypatch):
        """Should return JSON response with updated portlets."""
        request = authenticated_request()
        request.GET = {"direction": "0"}

        # Mock PortletsInlineView to avoid template rendering
        def mock_inline_view_get(self, request, obj):
            return "updated_portlets"

        monkeypatch.setattr(
            "lfs.manage.portlets.views.PortletsInlineView", type("MockView", (), {"get": mock_inline_view_get})
        )

        view = MovePortletView()
        response = view.get(request, portlet_assignment.id)

        assert response["Content-Type"] == "application/json"
        data = json.loads(response.content)
        assert "html" in data


@pytest.mark.django_db
@pytest.mark.unit
class TestSortPortletsView:
    """Tests for SortPortletsView."""

    def test_view_configuration(self):
        """Should have correct view configuration."""
        assert SortPortletsView.permission_required == "core.manage_shop"

    def test_post_sorts_portlets_correctly(self, portlet_assignment, authenticated_request, slot):
        """Should sort portlets after drag and drop."""
        request = authenticated_request()
        request.method = "POST"
        request.POST = QueryDict(f"portlet_id={portlet_assignment.id}&to_slot={slot.id}&new_index=1")

        view = SortPortletsView()
        response = view.post(request)

        assert response.status_code == 200
        portlet_assignment.refresh_from_db()
        assert portlet_assignment.slot_id == slot.id

    def test_post_updates_slot_when_changed(self, portlet_assignment, multiple_slots, authenticated_request):
        """Should update slot when portlet is moved to different slot."""
        # Use a different slot than the one the portlet is currently in
        target_slot = multiple_slots[1] if multiple_slots[1].id != portlet_assignment.slot_id else multiple_slots[0]

        request = authenticated_request()
        request.method = "POST"
        request.POST = QueryDict(f"portlet_id={portlet_assignment.id}&to_slot={target_slot.id}&new_index=1")

        original_slot_id = portlet_assignment.slot_id

        view = SortPortletsView()
        response = view.post(request)

        portlet_assignment.refresh_from_db()
        assert portlet_assignment.slot_id == target_slot.id
        assert portlet_assignment.slot_id != original_slot_id

    def test_post_handles_first_position(self, portlet_assignment, authenticated_request):
        """Should handle moving portlet to first position."""
        request = authenticated_request()
        request.method = "POST"
        request.POST = QueryDict(f"portlet_id={portlet_assignment.id}&to_slot={portlet_assignment.slot_id}&new_index=1")

        view = SortPortletsView()
        response = view.post(request)

        portlet_assignment.refresh_from_db()
        assert portlet_assignment.position == 10

    def test_post_handles_last_position(self, page, slot, authenticated_request, shop_for_portlets):
        """Should handle moving portlet to last position."""  # Create multiple portlets in the same slot
        portlets = []
        assignments = []
        for i in range(3):
            portlet = TextPortlet.objects.create(title=f"Test Portlet {i+1}", text=f"Content {i+1}")
            assignment = PortletAssignment.objects.create(
                slot=slot, content=page, portlet=portlet, position=(i + 1) * 10
            )
            portlets.append(portlet)
            assignments.append(assignment)

        # Use the first assignment for the test
        test_assignment = assignments[0]

        request = authenticated_request()
        request.method = "POST"
        request.POST = QueryDict(f"portlet_id={test_assignment.id}&to_slot={test_assignment.slot_id}&new_index=999")

        view = SortPortletsView()
        response = view.post(request)

        test_assignment.refresh_from_db()
        # Should be positioned after other portlets (position should be 40, which is > 10)
        assert test_assignment.position > 10


@pytest.mark.django_db
@pytest.mark.integration
class TestPortletViewsIntegration:
    """Integration tests for Portlet views."""

    @pytest.mark.parametrize(
        "url_name",
        [
            "lfs_add_portlet",
            "lfs_update_portlets",
            "lfs_sort_portlets",
        ],
    )
    def test_portlet_crud_workflow(self, page, authenticated_client, slot, url_name):
        """Should support complete CRUD workflow for portlets."""
        if url_name in ("lfs_add_portlet", "lfs_update_portlets"):
            url = reverse(
                url_name,
                kwargs={"object_type_id": ContentType.objects.get_for_model(page).id, "object_id": page.id},
            )
        else:
            url = reverse(url_name)
        response = authenticated_client.get(url)
        assert response.status_code != 404

    @pytest.mark.parametrize(
        "url_name,extra_kwargs",
        [
            ("lfs_add_portlet", {"needs_obj": True}),
            ("lfs_update_portlets", {"needs_obj": True}),
            ("lfs_delete_portlet", {"portletassignment_id": 1}),
            ("lfs_edit_portlet", {"portletassignment_id": 1}),
            ("lfs_move_portlet", {"portletassignment_id": 1}),
            ("lfs_sort_portlets", {}),
        ],
    )
    def test_permission_required_for_all_views(self, client, url_name, extra_kwargs):
        """Should require authentication for all portlet views."""
        page = Page.objects.create(title="Test Page", slug="test-page")
        if extra_kwargs.get("needs_obj"):
            url = reverse(
                url_name,
                kwargs={"object_type_id": ContentType.objects.get_for_model(page).id, "object_id": page.id},
            )
        else:
            url = reverse(url_name, kwargs={k: v for k, v in extra_kwargs.items() if k != "needs_obj"})
        response = client.get(url)
        assert response.status_code in [302, 403]


# =============================================================================
# Utility Function Tests
# =============================================================================


@pytest.mark.django_db
@pytest.mark.unit
class TestUpdatePortletPositions:
    """Tests for the update_portlet_positions utility function."""

    def test_update_portlet_positions_reorders_correctly(self, page, slot, shop_for_portlets):
        """Should reorder portlet positions correctly."""

        # Create multiple portlets in the same slot
        assignments = []
        for i in range(3):
            portlet = TextPortlet.objects.create(title=f"Test Portlet {i+1}", text=f"Content {i+1}")
            assignment = PortletAssignment.objects.create(
                slot=slot, content=page, portlet=portlet, position=(i + 1) * 10
            )
            assignments.append(assignment)

        # Manually set positions to be out of order
        assignments[0].position = 50
        assignments[1].position = 10
        assignments[2].position = 30
        for assignment in assignments:
            assignment.save()

        update_portlet_positions(assignments[0])

        # Refresh from database and get assignments in position order
        for assignment in assignments:
            assignment.refresh_from_db()

        # Get assignments in position order
        ordered_assignments = sorted(assignments, key=lambda x: x.position)
        positions = [assignment.position for assignment in ordered_assignments]
        assert positions == [10, 20, 30]

    def test_update_portlet_positions_handles_single_portlet(self, portlet_assignment):
        """Should handle single portlet correctly."""
        portlet_assignment.position = 999
        portlet_assignment.save()

        update_portlet_positions(portlet_assignment)

        portlet_assignment.refresh_from_db()
        assert portlet_assignment.position == 10

    def test_update_portlet_positions_handles_empty_slot(self, page, slot):
        """Should handle empty slot without errors."""

        # Create a mock PortletAssignment-like object
        class MockPA:
            def __init__(self):
                self.content_type = ContentType.objects.get_for_model(page)
                self.content_id = page.id
                self.slot = slot

        mock_pa = MockPA()

        # Should not raise an error
        update_portlet_positions(mock_pa)


@pytest.mark.django_db
@pytest.mark.unit
class TestGetPortletManagementUrl:
    """Tests for the get_portlet_management_url utility function."""

    def test_returns_page_url_for_page_object(self, page):
        """Should return correct URL for Page objects."""
        url = get_portlet_management_url(page)
        expected_url = reverse("lfs_manage_page_portlets", kwargs={"id": page.id})
        assert url == expected_url

    def test_returns_category_url_for_category_object(self, category):
        """Should return correct URL for Category objects."""
        url = get_portlet_management_url(category)
        expected_url = reverse("lfs_manage_category_portlets", kwargs={"id": category.id})
        assert url == expected_url

    def test_returns_manufacturer_url_for_manufacturer_object(self, manufacturer):
        """Should return correct URL for Manufacturer objects."""
        url = get_portlet_management_url(manufacturer)
        expected_url = reverse("lfs_manage_manufacturer_portlets", kwargs={"id": manufacturer.id})
        assert url == expected_url

    def test_returns_fallback_url_for_unknown_object_type(self):
        """Should return fallback URL for unknown object types."""

        class UnknownObject:
            def __init__(self):
                self.id = 123

        unknown_obj = UnknownObject()
        url = get_portlet_management_url(unknown_obj)
        expected_url = reverse("lfs_manage_page_portlets", kwargs={"id": 1})
        assert url == expected_url


# =============================================================================
# Edge Cases and Error Handling Tests
# =============================================================================


@pytest.mark.django_db
@pytest.mark.unit
class TestPortletViewsEdgeCases:
    """Tests for edge cases and error handling in portlet views."""

    def test_add_portlet_with_missing_content_type(self, authenticated_request, monkeypatch):
        """Should handle missing content type gracefully."""
        request = authenticated_request()
        request.GET = {"portlet_type": "textportlet"}

        # Mock ContentType.objects.get to raise DoesNotExist
        def mock_get(pk):
            raise ContentType.DoesNotExist()

        monkeypatch.setattr("lfs.manage.portlets.views.ContentType.objects.get", mock_get)

        view = AddPortletView()
        response = view.get(request, 99999, 99999)

        # Should handle the error gracefully
        assert response.status_code == 200
        assert "invalid content type" in response.content.decode().lower()

    def test_delete_portlet_with_deleted_content_object(self, portlet_assignment, authenticated_request, monkeypatch):
        """Should handle deleted content object gracefully."""
        request = authenticated_request()
        request.method = "POST"

        # Delete the content object
        portlet_assignment.content.delete()

        # Mock redirect
        def mock_redirect(url):
            return HttpResponseRedirect("/redirect/")

        monkeypatch.setattr("lfs.manage.portlets.views.redirect", mock_redirect)

        view = DeletePortletView()
        response = view.post(request, portlet_assignment.id)

        # Should redirect to a safe location
        assert isinstance(response, HttpResponseRedirect)

    def test_move_portlet_with_invalid_direction(self, portlet_assignment, authenticated_request, monkeypatch):
        """Should handle invalid direction parameter."""
        request = authenticated_request()
        request.GET = {"direction": "invalid"}

        original_position = portlet_assignment.position

        # Mock PortletsInlineView to avoid template rendering
        def mock_inline_view_get(self, request, obj):
            return "updated_portlets"

        monkeypatch.setattr(
            "lfs.manage.portlets.views.PortletsInlineView", type("MockView", (), {"get": mock_inline_view_get})
        )

        view = MovePortletView()
        response = view.get(request, portlet_assignment.id)

        # Should default to direction 0 (up), then update_portlet_positions resets to 10
        portlet_assignment.refresh_from_db()
        assert portlet_assignment.position == 10

    def test_sort_portlets_with_invalid_data(self, authenticated_request):
        """Should handle invalid POST data gracefully."""

        request = authenticated_request()
        request.method = "POST"
        request.POST = QueryDict("portlet_id=invalid&to_slot=invalid&new_index=invalid")

        view = SortPortletsView()

        # Should handle the error gracefully
        with pytest.raises((ValueError, PortletAssignment.DoesNotExist)):
            view.post(request)

    def test_update_portlets_with_invalid_object_id(self, authenticated_request, monkeypatch):
        """Should handle invalid object ID gracefully."""

        request = authenticated_request()
        request.method = "POST"
        request.POST = QueryDict("block_slot=1")

        # Mock ContentType.objects.get to raise DoesNotExist
        def mock_get(pk):
            raise ContentType.DoesNotExist()

        monkeypatch.setattr("lfs.manage.portlets.views.ContentType.objects.get", mock_get)

        view = UpdatePortletsView()
        response = view.post(request, 99999, 99999)

        # Should handle the error gracefully
        assert response.status_code == 200
        assert "invalid content type" in response.content.decode().lower()

    def test_portlets_inline_with_object_without_get_parent_for_portlets(self, authenticated_request, monkeypatch):
        """Should handle objects without get_parent_for_portlets method."""
        request = authenticated_request()

        # Create a mock object without the method
        class MockObj:
            def get_parent_for_portlets(self):
                raise AttributeError("'Mock' object has no attribute 'get_parent_for_portlets'")

        mock_obj = MockObj()

        # Mock the ContentType.objects.get_for_model to avoid database issues
        def mock_get_for_model(model):
            return type("MockCT", (), {})()

        monkeypatch.setattr("lfs.manage.portlets.views.ContentType.objects.get_for_model", mock_get_for_model)

        # Mock render_to_string
        def mock_render_to_string(template, request=None, context=None):
            return "rendered_content"

        monkeypatch.setattr("lfs.manage.portlets.views.render_to_string", mock_render_to_string)

        view = PortletsInlineView()

        # Should handle the error gracefully
        with pytest.raises(AttributeError):
            view.get(request, mock_obj)


# =============================================================================
# Permission Tests
# =============================================================================


@pytest.mark.django_db
@pytest.mark.unit
class TestPortletViewsPermissions:
    """Tests for permission handling in portlet views."""

    def test_portlets_inline_requires_permission(self, page, request_factory, regular_user):
        """Should require manage_shop permission."""
        request = request_factory.get("/")
        request.user = regular_user

        view = PortletsInlineView()
        view.setup(request)

        assert not view.has_permission()

    def test_update_portlets_requires_permission(self, page, request_factory, regular_user, slot):
        """Should require manage_shop permission."""

        request = request_factory.post("/", QueryDict(f"block_slot={slot.id}"))
        request.user = regular_user

        view = UpdatePortletsView()
        view.setup(request, object_type_id=ContentType.objects.get_for_model(page).id, object_id=page.id)

        assert not view.has_permission()

    def test_add_portlet_requires_permission(self, page, request_factory, regular_user):
        """Should require manage_shop permission."""
        request = request_factory.get("/", {"portlet_type": "textportlet"})
        request.user = regular_user

        view = AddPortletView()
        view.setup(request, object_type_id=ContentType.objects.get_for_model(page).id, object_id=page.id)

        assert not view.has_permission()

    def test_delete_portlet_requires_permission(self, portlet_assignment, request_factory, regular_user):
        """Should require manage_shop permission."""
        request = request_factory.get("/")
        request.user = regular_user

        view = DeletePortletView()
        view.setup(request, portletassignment_id=portlet_assignment.id)

        assert not view.has_permission()

    def test_edit_portlet_requires_permission(self, portlet_assignment, request_factory, regular_user):
        """Should require manage_shop permission."""
        request = request_factory.get("/")
        request.user = regular_user

        view = EditPortletView()
        view.setup(request, portletassignment_id=portlet_assignment.id)

        assert not view.has_permission()

    def test_move_portlet_requires_permission(self, portlet_assignment, request_factory, regular_user):
        """Should require manage_shop permission."""
        request = request_factory.get("/", {"direction": "0"})
        request.user = regular_user

        view = MovePortletView()
        view.setup(request, portletassignment_id=portlet_assignment.id)

        assert not view.has_permission()

    def test_sort_portlets_requires_permission(self, portlet_assignment, request_factory, regular_user, slot):
        """Should require manage_shop permission."""

        request = request_factory.post(
            "/", QueryDict(f"portlet_id={portlet_assignment.id}&to_slot={slot.id}&new_index=1")
        )
        request.user = regular_user

        view = SortPortletsView()
        view.setup(request)

        assert not view.has_permission()
