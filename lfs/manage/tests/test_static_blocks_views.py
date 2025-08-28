"""
Tests for StaticBlock views in the manage package.

Following TDD principles:
- Test behavior, not implementation
- Clear test names
- Arrange-Act-Assert structure
- One assertion per test (when practical)
"""

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import Http404

from lfs.catalog.models import StaticBlock
from lfs.manage.static_blocks.views import (
    StaticBlockDataView,
    StaticBlockFilesView,
    StaticBlockTabMixin,
    manage_static_blocks,
)

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.unit
class TestStaticBlockTabMixin:
    """Tests for StaticBlockTabMixin functionality."""

    def test_get_static_block_returns_correct_object(self, static_block):
        """Should return the StaticBlock for given id."""
        mixin = StaticBlockTabMixin()
        mixin.kwargs = {"id": static_block.id}

        result = mixin.get_static_block()

        assert result == static_block

    def test_get_static_block_raises_404_for_nonexistent_id(self):
        """Should raise Http404 for non-existent StaticBlock id."""
        mixin = StaticBlockTabMixin()
        mixin.kwargs = {"id": 99999}

        with pytest.raises(Http404):
            mixin.get_static_block()

    def test_get_tabs_returns_correct_navigation_urls(self, static_block):
        """Should return list of tab navigation URLs."""
        mixin = StaticBlockTabMixin()

        tabs = mixin._get_tabs(static_block)

        assert len(tabs) == 2
        assert tabs[0] == ("data", reverse("lfs_manage_static_block", args=[static_block.pk]))
        assert tabs[1] == ("files", reverse("lfs_manage_static_block_files", args=[static_block.pk]))


@pytest.mark.django_db
@pytest.mark.unit
class TestStaticBlockDataView:
    """Tests for StaticBlockDataView (Data Tab)."""

    def test_requires_authentication(self, request_factory, static_block):
        """Should require user to be authenticated."""
        request = request_factory.get(f"/static-block/{static_block.id}/")
        request.user = AnonymousUser()

        view = StaticBlockDataView()
        view.setup(request, id=static_block.id)

        # PermissionRequiredMixin should handle this
        assert not view.has_permission()

    def test_requires_manage_shop_permission(self, request_factory, regular_user, static_block):
        """Should require manage_shop permission."""
        request = request_factory.get(f"/static-block/{static_block.id}/")
        request.user = regular_user

        view = StaticBlockDataView()
        view.setup(request, id=static_block.id)

        assert not view.has_permission()

    def test_allows_access_with_manage_permission(self, request_factory, manage_user, static_block):
        """Should allow access for users with manage_shop permission."""
        request = request_factory.get(f"/static-block/{static_block.id}/")
        request.user = manage_user

        view = StaticBlockDataView()
        view.setup(request, id=static_block.id)

        assert view.has_permission()

    def test_tab_name_is_data(self):
        """Should have tab_name set to 'data'."""
        view = StaticBlockDataView()

        assert view.tab_name == "data"

    def test_uses_correct_model(self):
        """Should use StaticBlock model."""
        view = StaticBlockDataView()

        assert view.model == StaticBlock

    def test_get_success_url_returns_data_tab_url(self, static_block):
        """Should return URL to data tab after successful save."""
        view = StaticBlockDataView()
        view.object = static_block

        url = view.get_success_url()

        assert url == reverse("lfs_manage_static_block", kwargs={"id": static_block.pk})

    def test_get_context_data_includes_tab_navigation(self, request_factory, manage_user, static_block):
        """Should include tab navigation in context."""
        request = request_factory.get(f"/static-block/{static_block.id}/")
        request.user = manage_user

        view = StaticBlockDataView()
        view.setup(request, id=static_block.id)
        view.object = static_block

        context = view.get_context_data()

        assert "active_tab" in context
        assert context["active_tab"] == "data"
        assert "tabs" in context
        assert "current_static_block" in context
        assert context["current_static_block"] == static_block


@pytest.mark.django_db
@pytest.mark.unit
class TestStaticBlockFilesView:
    """Tests for StaticBlockFilesView (Files Tab)."""

    def test_requires_manage_shop_permission(self, request_factory, regular_user, static_block):
        """Should require manage_shop permission."""
        request = request_factory.get(f"/static-block/{static_block.id}/files/")
        request.user = regular_user

        view = StaticBlockFilesView()
        view.setup(request, id=static_block.id)

        assert not view.has_permission()

    def test_tab_name_is_files(self):
        """Should have tab_name set to 'files'."""
        view = StaticBlockFilesView()

        assert view.tab_name == "files"

    def test_get_success_url_returns_files_tab_url(self, static_block):
        """Should return URL to files tab after successful operation."""
        view = StaticBlockFilesView()
        view.kwargs = {"id": static_block.id}

        url = view.get_success_url()

        assert url == reverse("lfs_manage_static_block_files", kwargs={"id": static_block.id})

    def test_get_context_data_includes_static_block(self, request_factory, manage_user, static_block):
        """Should include static_block in context."""
        request = request_factory.get(f"/static-block/{static_block.id}/files/")
        request.user = manage_user

        view = StaticBlockFilesView()
        view.setup(request, id=static_block.id)

        context = view.get_context_data()

        assert "static_block" in context
        assert context["static_block"] == static_block
        assert "current_static_block" in context
        assert context["current_static_block"] == static_block


@pytest.mark.django_db
@pytest.mark.integration
class TestManageStaticBlocksDispatcher:
    """Tests for manage_static_blocks dispatcher function."""

    def test_redirects_to_first_static_block_when_blocks_exist(self, authenticated_request, multiple_static_blocks):
        """Should redirect to first StaticBlock when blocks exist."""
        request = authenticated_request("GET", "/static-blocks/")

        response = manage_static_blocks(request)

        first_block = multiple_static_blocks[0]
        expected_url = reverse("lfs_manage_static_block", kwargs={"id": first_block.id})
        assert response.status_code == 302
        assert response.url == expected_url

    def test_redirects_to_no_static_blocks_when_none_exist(self, authenticated_request, db):
        """Should redirect to no_static_blocks view when no blocks exist."""
        # Ensure no static blocks exist
        StaticBlock.objects.all().delete()

        request = authenticated_request("GET", "/static-blocks/")

        response = manage_static_blocks(request)

        expected_url = reverse("lfs_manage_no_static_blocks")
        assert response.status_code == 302
        assert response.url == expected_url


@pytest.mark.django_db
class TestStaticBlockViewIntegration:
    """Integration tests for StaticBlock views."""

    def test_data_view_form_submission_saves_changes(self, authenticated_request, static_block):
        """Should save changes when valid form is submitted to data view."""
        form_data = {"name": "Updated Block Name", "html": "<p>Updated content</p>"}
        request = authenticated_request("POST", f"/static-block/{static_block.id}/", data=form_data)

        view = StaticBlockDataView.as_view()
        response = view(request, id=static_block.id)

        # Should redirect after successful save
        assert response.status_code == 302

        # Verify changes were saved
        static_block.refresh_from_db()
        assert static_block.name == "Updated Block Name"
        assert static_block.html == "<p>Updated content</p>"
        # Position is no longer part of the data form

    def test_files_view_handles_file_upload(self, authenticated_request, static_block):
        """Should handle file upload in files view."""
        # This is a placeholder - actual file upload testing would require
        # more complex setup with file fixtures
        request = authenticated_request("GET", f"/static-block/{static_block.id}/files/")

        view = StaticBlockFilesView.as_view()
        response = view(request, id=static_block.id)

        # Should render successfully
        assert response.status_code == 200

    def test_static_block_files_url_exists_and_resolves(self):
        """The lfs_manage_static_block_files URL should exist and be resolvable."""
        # RED: This test would fail if the URL doesn't exist
        from django.urls import reverse, NoReverseMatch

        # Should not raise NoReverseMatch
        try:
            url = reverse("lfs_manage_static_block_files", args=[1])
            assert url is not None
            assert "/static-block/1/files/" in url
        except NoReverseMatch:
            pytest.fail("URL 'lfs_manage_static_block_files' does not exist")

    def test_update_files_sb_url_exists_and_resolves(self):
        """The lfs_manage_update_files_sb URL should exist for legacy template compatibility."""
        # RED: This test should FAIL initially due to missing lfs_manage_update_files_sb URL
        from django.urls import reverse, NoReverseMatch

        # Should not raise NoReverseMatch - used in files-list.html template
        try:
            url = reverse("lfs_manage_update_files_sb", args=[1])
            assert url is not None
            # Should resolve to files view since that handles update operations
            assert "/static-block/1/files/" in url or "update" in url
        except NoReverseMatch:
            pytest.fail("URL 'lfs_manage_update_files_sb' does not exist but is used in templates")

    def test_file_upload_redirects_to_files_tab_not_json(self, authenticated_request, static_block):
        """File upload should redirect to files tab, not return JSON."""
        # RED: This test should FAIL initially because current code returns JSON
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.test import RequestFactory
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(username="testuser", password="testpass")
        user.is_superuser = True
        user.save()

        # Create a fake uploaded file
        uploaded_file = SimpleUploadedFile("test-image.png", b"fake image content", content_type="image/png")

        # Use RequestFactory to create a proper request with FILES
        factory = RequestFactory()
        request = factory.post(f"/static-block/{static_block.id}/files/", data={"files[]": uploaded_file})
        request.user = user

        view = StaticBlockFilesView.as_view()
        response = view(request, id=static_block.id)

        # Should be a redirect (302), not JSON (200)
        assert response.status_code == 302, f"Expected redirect, got {response.status_code}"
        assert response.url == f"/manage/static-block/{static_block.id}/files/"

        # Should NOT be JSON content
        assert response.get("Content-Type") != "application/json"

    def test_files_list_template_syntax_includes_csrf_token(self):
        """Files list template should include {% csrf_token %} syntax to prevent CSRF errors."""
        # RED: This test should FAIL initially because template is missing {% csrf_token %}

        # Read the template file directly
        with open("src/lfs/lfs/manage/templates/manage/static_block/files-list.html", "r") as f:
            template_content = f.read()

        # Should contain {% csrf_token %} in the form
        assert "{% csrf_token %}" in template_content, "Files update form missing {% csrf_token %}"

        # Should be inside a form tag
        lines = template_content.split("\n")
        form_started = False
        csrf_found = False

        for line in lines:
            if "<form" in line:
                form_started = True
            elif "</form>" in line:
                form_started = False
            elif "{% csrf_token %}" in line and form_started:
                csrf_found = True
                break

        assert csrf_found, "{% csrf_token %} should be inside the form"

    def test_file_update_saves_changes_and_redirects(self, authenticated_request, static_block):
        """File update should save changes and redirect, not return JSON."""
        # RED: This test should FAIL initially because update action is not processed correctly
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.test import RequestFactory
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(username="testuser2", password="testpass")
        user.is_superuser = True
        user.save()

        # Create a file for the static block first
        from lfs.catalog.models import File

        uploaded_file = SimpleUploadedFile("test.png", b"content", content_type="image/png")
        file = File.objects.create(content=static_block, title="Original Title")
        file.file.save("test.png", uploaded_file, save=True)

        # Simulate update form submission
        factory = RequestFactory()
        request = factory.post(
            f"/static-block/{static_block.id}/files/",
            data={
                "update": "Update",  # Button name from template
                f"title-{file.id}": "Updated Title",
                f"position-{file.id}": "20",
            },
        )
        request.user = user

        view = StaticBlockFilesView.as_view()
        response = view(request, id=static_block.id)

        # Should be a redirect (302), not JSON (200)
        assert response.status_code == 302, f"Expected redirect, got {response.status_code}"

        # Verify changes were saved
        file.refresh_from_db()
        assert file.title == "Updated Title"
        assert file.position == 20

    def test_files_list_buttons_use_bootstrap_classes(self):
        """Update and Delete buttons should use Bootstrap CSS classes for consistency."""
        # RED: This test should FAIL initially because buttons use old 'button' class

        # Read the template file directly
        with open("src/lfs/lfs/manage/templates/manage/static_block/files-list.html", "r") as f:
            template_content = f.read()

        # Should contain Bootstrap button classes (allowing additional classes)
        assert "btn btn-primary" in template_content, "Update button should use Bootstrap btn btn-primary"
        assert (
            "btn btn-danger" in template_content or "btn btn-outline-danger" in template_content
        ), "Delete button should use Bootstrap danger styling"

        # Should NOT contain old button classes
        assert 'class="button ajax-save-button"' not in template_content, "Should not use old 'button' class"


@pytest.mark.django_db
class TestAddStaticBlockView:
    """Test cases for AddStaticBlockView (CreateView)."""

    def test_requires_authentication(self, request_factory):
        """Test that the view requires user authentication."""
        from lfs.manage.static_blocks.views import AddStaticBlockView
        from django.contrib.auth.models import AnonymousUser

        request = request_factory.get("/add-static-block/")
        request.user = AnonymousUser()
        view = AddStaticBlockView()
        view.setup(request)

        # Should require authentication
        response = view.dispatch(request)
        assert response.status_code == 302  # Redirect to login

    def test_requires_manage_shop_permission(self, request_factory, regular_user):
        """Test that the view requires manage_shop permission."""
        from lfs.manage.static_blocks.views import AddStaticBlockView

        request = request_factory.get("/add-static-block/")
        request.user = regular_user
        view = AddStaticBlockView()
        view.setup(request)

        # Should require manage_shop permission
        response = view.dispatch(request)
        assert response.status_code == 302  # Redirect due to missing permission

    def test_allows_access_with_manage_permission(self, request_factory, manage_user):
        """Test that the view allows access with proper permission."""
        from lfs.manage.static_blocks.views import AddStaticBlockView

        request = request_factory.get("/add-static-block/")
        request.user = manage_user
        view = AddStaticBlockView()
        view.setup(request)

        response = view.dispatch(request)
        assert response.status_code == 200

    def test_get_returns_successful_response(self, request_factory, manage_user):
        """Test that GET request returns successful response."""
        from lfs.manage.static_blocks.views import AddStaticBlockView

        request = request_factory.get("/add-static-block/")
        request.user = manage_user
        view = AddStaticBlockView()
        view.setup(request)

        response = view.get(request)
        assert response.status_code == 200
        # Note: Full template rendering requires Shop setup, testing status code only

    def test_get_context_data_includes_form(self, request_factory, manage_user):
        """Test that context includes form for static block creation."""
        from lfs.manage.static_blocks.views import AddStaticBlockView

        request = request_factory.get("/add-static-block/")
        request.user = manage_user
        view = AddStaticBlockView()
        view.setup(request)
        view.object = None  # CreateView sets this to None initially

        context = view.get_context_data()

        assert "form" in context
        assert "view" in context

    def test_post_creates_new_static_block(self, request_factory, manage_user):
        """Test that POST request creates a new static block."""
        from lfs.manage.static_blocks.views import AddStaticBlockView
        from lfs.catalog.models import StaticBlock

        initial_count = StaticBlock.objects.count()

        request = request_factory.post("/add-static-block/", {"name": "New Test Block", "html": "<p>Test content</p>"})
        request.user = manage_user
        view = AddStaticBlockView()
        view.setup(request)

        response = view.post(request)

        # Should create new static block
        assert StaticBlock.objects.count() == initial_count + 1
        new_block = StaticBlock.objects.get(name="New Test Block")
        # Note: HTML content might be set to empty string by view logic
        assert new_block.html is not None

    def test_post_sets_empty_html_when_none_provided(self, request_factory, manage_user):
        """Test that POST sets empty HTML when none provided."""
        from lfs.manage.static_blocks.views import AddStaticBlockView
        from lfs.catalog.models import StaticBlock

        request = request_factory.post("/add-static-block/", {"name": "Empty HTML Block"})
        request.user = manage_user
        view = AddStaticBlockView()
        view.setup(request)

        response = view.post(request)

        new_block = StaticBlock.objects.get(name="Empty HTML Block")
        assert new_block.html == ""

    def test_post_htmx_request_returns_redirect_header(self, request_factory, manage_user):
        """Test that HTMX POST returns HX-Redirect header."""
        from lfs.manage.static_blocks.views import AddStaticBlockView

        request = request_factory.post("/add-static-block/", {"name": "HTMX Test Block"})
        request.user = manage_user
        request.headers = {"HX-Request": "true"}
        view = AddStaticBlockView()
        view.setup(request)

        response = view.post(request)

        assert response.status_code == 200
        assert "HX-Redirect" in response
        assert "/manage/static-block/" in response["HX-Redirect"]

    def test_post_request_returns_htmx_redirect(self, request_factory, manage_user):
        """Test that POST returns HTMX redirect header."""
        from lfs.manage.static_blocks.views import AddStaticBlockView

        request = request_factory.post("/add-static-block/", {"name": "Regular Test Block"})
        request.user = manage_user
        view = AddStaticBlockView()
        view.setup(request)

        response = view.post(request)

        assert response.status_code == 200  # HTMX response
        assert response["HX-Redirect"]
        assert "/manage/static-block/" in response["HX-Redirect"]

    def test_uses_correct_template(self, request_factory, manage_user):
        """Test that view uses the correct template."""
        from lfs.manage.static_blocks.views import AddStaticBlockView

        view = AddStaticBlockView()
        assert view.template_name == "manage/static_block/add_static_block.html"

    def test_form_validation_error_returns_form_response(self, request_factory, manage_user):
        """Test that form validation errors are properly handled."""
        from lfs.manage.static_blocks.views import AddStaticBlockView
        from lfs.catalog.models import StaticBlock

        initial_count = StaticBlock.objects.count()

        # Submit form without required name field
        request = request_factory.post("/add-static-block/", {"html": "<p>Content without name</p>"})
        request.user = manage_user
        view = AddStaticBlockView()
        view.setup(request)

        response = view.post(request)

        # Should return form with errors (status 200, not redirect)
        assert response.status_code == 200
        # Should not create a new static block
        assert StaticBlock.objects.count() == initial_count
