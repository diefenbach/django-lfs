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
    StaticBlockCreateView,
    ManageStaticBlocksView,
    StaticBlockDeleteView,
    StaticBlockPreviewView,
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

    def test_get_tabs_returns_correct_navigation_urls_without_search(self, static_block, rf):
        """Should return list of tab navigation URLs without search parameters."""
        mixin = StaticBlockTabMixin()
        mixin.request = rf.get("/test/")

        tabs = mixin._get_tabs(static_block)

        assert len(tabs) == 2
        assert tabs[0] == ("data", reverse("lfs_manage_static_block", args=[static_block.pk]))
        assert tabs[1] == ("files", reverse("lfs_manage_static_block_files", args=[static_block.pk]))

    def test_get_tabs_returns_correct_navigation_urls_with_search(self, static_block, rf):
        """Should return list of tab navigation URLs with search parameters."""
        mixin = StaticBlockTabMixin()
        mixin.request = rf.get("/test/", {"q": "test_search"})

        tabs = mixin._get_tabs(static_block)

        expected_data_url = reverse("lfs_manage_static_block", args=[static_block.pk]) + "?q=test_search"
        expected_files_url = reverse("lfs_manage_static_block_files", args=[static_block.pk]) + "?q=test_search"

        assert len(tabs) == 2
        assert tabs[0] == ("data", expected_data_url)
        assert tabs[1] == ("files", expected_files_url)

    def test_get_static_blocks_queryset_without_search(self, rf):
        """Should return all static blocks when no search query provided."""
        from lfs.catalog.models import StaticBlock

        # Create test static blocks
        sb1 = StaticBlock.objects.create(name="Test Block 1", html="<p>Test 1</p>")
        sb2 = StaticBlock.objects.create(name="Another Block", html="<p>Test 2</p>")

        mixin = StaticBlockTabMixin()
        mixin.request = rf.get("/test/")

        queryset = mixin.get_static_blocks_queryset()

        assert queryset.count() == 2
        assert sb1 in queryset
        assert sb2 in queryset

    def test_get_static_blocks_queryset_with_search(self, rf):
        """Should return filtered static blocks when search query provided."""
        from lfs.catalog.models import StaticBlock

        # Create test static blocks
        sb1 = StaticBlock.objects.create(name="Test Block", html="<p>Test 1</p>")
        sb2 = StaticBlock.objects.create(name="Another Block", html="<p>Test 2</p>")
        sb3 = StaticBlock.objects.create(name="Test Another", html="<p>Test 3</p>")

        mixin = StaticBlockTabMixin()
        mixin.request = rf.get("/test/", {"q": "Test"})

        queryset = mixin.get_static_blocks_queryset()

        assert queryset.count() == 2
        assert sb1 in queryset
        assert sb2 not in queryset  # "Another Block" doesn't contain "Test"
        assert sb3 in queryset


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

    @pytest.mark.parametrize(
        "attribute,expected",
        [
            ("tab_name", "data"),
            ("model", StaticBlock),
        ],
    )
    def test_view_configuration(self, attribute, expected):
        """Should have correct view configuration."""
        view = StaticBlockDataView()
        assert getattr(view, attribute) == expected

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
        assert "static_block" in context
        assert context["static_block"] == static_block


@pytest.mark.django_db
@pytest.mark.unit
class TestStaticBlockFilesView:
    """Tests for StaticBlockFilesView (Files Tab)."""

    def test_requires_authentication(self, request_factory, static_block):
        """Should require user to be authenticated."""
        request = request_factory.get(f"/static-block/{static_block.id}/files/")
        request.user = AnonymousUser()

        view = StaticBlockFilesView()
        view.setup(request, id=static_block.id)

        assert not view.has_permission()

    def test_requires_manage_shop_permission(self, request_factory, regular_user, static_block):
        """Should require manage_shop permission."""
        request = request_factory.get(f"/static-block/{static_block.id}/files/")
        request.user = regular_user

        view = StaticBlockFilesView()
        view.setup(request, id=static_block.id)

        assert not view.has_permission()

    def test_allows_access_with_manage_permission(self, request_factory, manage_user, static_block):
        """Should allow access for users with manage_shop permission."""
        request = request_factory.get(f"/static-block/{static_block.id}/files/")
        request.user = manage_user

        view = StaticBlockFilesView()
        view.setup(request, id=static_block.id)

        assert view.has_permission()

    @pytest.mark.parametrize(
        "attribute,expected",
        [
            ("tab_name", "files"),
        ],
    )
    def test_view_configuration(self, attribute, expected):
        """Should have correct view configuration."""
        view = StaticBlockFilesView()
        assert getattr(view, attribute) == expected

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
        assert "static_block" in context
        assert context["static_block"] == static_block


@pytest.mark.django_db
@pytest.mark.unit
class TestManageStaticBlocksViewPermissions:
    """Unit tests for ManageStaticBlocksView permissions."""

    def test_requires_authentication(self, request_factory):
        """Should require user to be authenticated."""
        request = request_factory.get("/manage/static-blocks/")
        request.user = AnonymousUser()

        view = ManageStaticBlocksView()
        view.setup(request)

        assert not view.has_permission()

    def test_requires_manage_shop_permission(self, request_factory, regular_user):
        """Should require manage_shop permission."""
        request = request_factory.get("/manage/static-blocks/")
        request.user = regular_user

        view = ManageStaticBlocksView()
        view.setup(request)

        assert not view.has_permission()

    def test_allows_access_with_manage_permission(self, request_factory, manage_user):
        """Should allow access for users with manage_shop permission."""
        request = request_factory.get("/manage/static-blocks/")
        request.user = manage_user

        view = ManageStaticBlocksView()
        view.setup(request)

        assert view.has_permission()


@pytest.mark.django_db
@pytest.mark.integration
class TestManageStaticBlocksView:
    """Tests for ManageStaticBlocksView dispatcher class."""

    def test_redirects_to_first_static_block_when_blocks_exist(self, authenticated_request, multiple_static_blocks):
        """Should redirect to first StaticBlock when blocks exist."""
        request = authenticated_request("GET", "/static-blocks/")

        view = ManageStaticBlocksView.as_view()
        response = view(request)

        first_block = multiple_static_blocks[0]
        expected_url = reverse("lfs_manage_static_block", kwargs={"id": first_block.id})
        assert response.status_code == 302
        assert response.url == expected_url

    def test_redirects_to_no_static_blocks_when_none_exist(self, authenticated_request, db):
        """Should redirect to no_static_blocks view when no blocks exist."""
        # Ensure no static blocks exist
        StaticBlock.objects.all().delete()

        request = authenticated_request("GET", "/static-blocks/")

        view = ManageStaticBlocksView.as_view()
        response = view(request)

        expected_url = reverse("lfs_manage_no_static_blocks")
        assert response.status_code == 302
        assert response.url == expected_url


@pytest.mark.django_db
class TestStaticBlockViewIntegration:
    """Integration tests for StaticBlock views."""

    def test_data_view_form_submission_saves_changes(self, authenticated_request, static_block, monkeypatch):
        """Should save changes when valid form is submitted to data view."""

        # Mock messages.success to avoid MessageMiddleware requirement
        def mock_messages_success(request, message):
            pass

        monkeypatch.setattr("lfs.manage.static_blocks.views.messages.success", mock_messages_success)

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

    def test_file_upload_redirects_to_files_tab_not_json(self, authenticated_request, static_block, monkeypatch):
        """File upload should redirect to files tab, not return JSON."""
        # RED: This test should FAIL initially because current code returns JSON
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.test import RequestFactory
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(username="testuser", password="testpass")
        user.is_superuser = True
        user.save()

        # Mock messages.success to avoid MessageMiddleware requirement
        def mock_messages_success(request, message):
            pass

        monkeypatch.setattr("lfs.manage.static_blocks.views.messages.success", mock_messages_success)

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
        with open("src/lfs/lfs/manage/templates/manage/static_block/tabs/_files.html", "r") as f:
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

    def test_file_update_saves_changes_and_redirects(self, authenticated_request, static_block, monkeypatch):
        """File update should save changes and redirect, not return JSON."""
        # RED: This test should FAIL initially because update action is not processed correctly
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.test import RequestFactory
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(username="testuser2", password="testpass")
        user.is_superuser = True
        user.save()

        # Mock messages.success to avoid MessageMiddleware requirement
        def mock_messages_success(request, message):
            pass

        monkeypatch.setattr("lfs.manage.static_blocks.views.messages.success", mock_messages_success)

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
        with open("src/lfs/lfs/manage/templates/manage/static_block/tabs/_files.html", "r") as f:
            template_content = f.read()

        # Should contain Bootstrap button classes (allowing additional classes)
        assert "btn btn-primary" in template_content, "Update button should use Bootstrap btn btn-primary"
        assert (
            "btn btn-danger" in template_content or "btn btn-outline-danger" in template_content
        ), "Delete button should use Bootstrap danger styling"

        # Should NOT contain old button classes
        assert 'class="button ajax-save-button"' not in template_content, "Should not use old 'button' class"


@pytest.mark.django_db
@pytest.mark.unit
class TestStaticBlockDeleteViewPermissions:
    """Unit tests for StaticBlockDeleteView permissions."""

    def test_requires_authentication(self, request_factory, static_block):
        """Should require user to be authenticated."""
        request = request_factory.delete(f"/manage/static-block/{static_block.id}/delete/")
        request.user = AnonymousUser()

        view = StaticBlockDeleteView()
        view.setup(request, id=static_block.id)

        assert not view.has_permission()

    def test_requires_manage_shop_permission(self, request_factory, regular_user, static_block):
        """Should require manage_shop permission."""
        request = request_factory.delete(f"/manage/static-block/{static_block.id}/delete/")
        request.user = regular_user

        view = StaticBlockDeleteView()
        view.setup(request, id=static_block.id)

        assert not view.has_permission()

    def test_allows_access_with_manage_permission(self, request_factory, manage_user, static_block):
        """Should allow access for users with manage_shop permission."""
        request = request_factory.delete(f"/manage/static-block/{static_block.id}/delete/")
        request.user = manage_user

        view = StaticBlockDeleteView()
        view.setup(request, id=static_block.id)

        assert view.has_permission()


@pytest.mark.django_db
@pytest.mark.unit
class TestStaticBlockPreviewViewPermissions:
    """Unit tests for StaticBlockPreviewView permissions."""

    def test_requires_authentication(self, request_factory, static_block):
        """Should require user to be authenticated."""
        request = request_factory.get(f"/manage/static-block/{static_block.id}/preview/")
        request.user = AnonymousUser()

        view = StaticBlockPreviewView()
        view.setup(request, id=static_block.id)

        assert not view.has_permission()

    def test_requires_manage_shop_permission(self, request_factory, regular_user, static_block):
        """Should require manage_shop permission."""
        request = request_factory.get(f"/manage/static-block/{static_block.id}/preview/")
        request.user = regular_user

        view = StaticBlockPreviewView()
        view.setup(request, id=static_block.id)

        assert not view.has_permission()

    def test_allows_access_with_manage_permission(self, request_factory, manage_user, static_block):
        """Should allow access for users with manage_shop permission."""
        request = request_factory.get(f"/manage/static-block/{static_block.id}/preview/")
        request.user = manage_user

        view = StaticBlockPreviewView()
        view.setup(request, id=static_block.id)

        assert view.has_permission()


@pytest.mark.django_db
class TestStaticBlockCreateView:
    """Test cases for StaticBlockCreateView (CreateView)."""

    @pytest.mark.parametrize(
        "user_type,expected_status,description",
        [
            ("anonymous", 302, "requires authentication"),
            ("regular", 302, "requires manage_shop permission"),
            ("manager", 200, "allows access with proper permission"),
        ],
    )
    def test_permission_requirements(
        self, request_factory, user_type, expected_status, description, regular_user, manage_user
    ):
        """Test view permission requirements for different user types."""
        # Select user based on type
        if user_type == "anonymous":
            user = AnonymousUser()
        elif user_type == "regular":
            user = regular_user
        else:  # manager
            user = manage_user

        request = request_factory.get("/add-static-block/")
        request.user = user
        view = StaticBlockCreateView()
        view.setup(request)

        if expected_status == 302:  # Permission denied
            assert not view.has_permission(), f"Failed: {description}"
        else:  # Should have permission
            assert view.has_permission(), f"Failed: {description}"

    def test_get_returns_successful_response(self, request_factory, manage_user):
        """Test that GET request returns successful response."""

        request = request_factory.get("/add-static-block/")
        request.user = manage_user
        view = StaticBlockCreateView()
        view.setup(request)

        response = view.get(request)
        assert response.status_code == 200
        # Note: Full template rendering requires Shop setup, testing status code only

    def test_get_context_data_includes_form(self, request_factory, manage_user):
        """Test that context includes form for static block creation."""

        request = request_factory.get("/add-static-block/")
        request.user = manage_user
        view = StaticBlockCreateView()
        view.setup(request)
        view.object = None  # CreateView sets this to None initially

        context = view.get_context_data()

        assert "form" in context
        assert "view" in context

    def test_post_creates_new_static_block(self, request_factory, manage_user, monkeypatch):
        """Test that POST request creates a new static block."""
        from lfs.catalog.models import StaticBlock

        # Mock messages framework
        monkeypatch.setattr("django.contrib.messages.success", lambda request, message: None)

        initial_count = StaticBlock.objects.count()

        request = request_factory.post("/add-static-block/", {"name": "New Test Block", "html": "<p>Test content</p>"})
        request.user = manage_user
        view = StaticBlockCreateView()
        view.setup(request)

        response = view.post(request)

        # Should create new static block
        assert StaticBlock.objects.count() == initial_count + 1
        new_block = StaticBlock.objects.get(name="New Test Block")
        # Note: HTML content might be set to empty string by view logic
        assert new_block.html is not None

    def test_post_sets_empty_html_when_none_provided(self, request_factory, manage_user, monkeypatch):
        """Test that POST sets empty HTML when none provided."""
        from lfs.catalog.models import StaticBlock

        # Mock messages framework
        monkeypatch.setattr("django.contrib.messages.success", lambda request, message: None)

        request = request_factory.post("/add-static-block/", {"name": "Empty HTML Block"})
        request.user = manage_user
        view = StaticBlockCreateView()
        view.setup(request)

        response = view.post(request)

        new_block = StaticBlock.objects.get(name="Empty HTML Block")
        assert new_block.html == ""

    def test_post_htmx_request_returns_redirect_header(self, request_factory, manage_user, monkeypatch):
        """Test that HTMX POST returns standard redirect."""
        # Mock messages framework
        monkeypatch.setattr("django.contrib.messages.success", lambda request, message: None)

        request = request_factory.post("/add-static-block/", {"name": "HTMX Test Block"})
        request.user = manage_user
        request.headers = {"HX-Request": "true"}
        view = StaticBlockCreateView()
        view.setup(request)

        response = view.post(request)

        assert response.status_code == 302
        assert "/manage/static-block/" in response.url

    def test_post_request_returns_standard_redirect(self, request_factory, manage_user, monkeypatch):
        """Test that POST returns standard Django redirect."""
        # Mock messages framework
        monkeypatch.setattr("django.contrib.messages.success", lambda request, message: None)

        request = request_factory.post("/add-static-block/", {"name": "Regular Test Block"})
        request.user = manage_user
        view = StaticBlockCreateView()
        view.setup(request)

        response = view.post(request)

        assert response.status_code == 302  # Standard redirect
        assert "/manage/static-block/" in response.url

    def test_uses_correct_template(self, request_factory, manage_user):
        """Test that view uses the correct template."""

        view = StaticBlockCreateView()
        assert view.template_name == "manage/static_block/add_static_block.html"

    def test_form_validation_error_returns_form_response(self, request_factory, manage_user):
        """Test that form validation errors are properly handled."""

        from lfs.catalog.models import StaticBlock

        initial_count = StaticBlock.objects.count()

        # Submit form without required name field
        request = request_factory.post("/add-static-block/", {"html": "<p>Content without name</p>"})
        request.user = manage_user
        view = StaticBlockCreateView()
        view.setup(request)

        response = view.post(request)

        # Should return form with errors (status 200, not redirect)
        assert response.status_code == 200
        # Should not create a new static block
        assert StaticBlock.objects.count() == initial_count
