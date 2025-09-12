"""
Comprehensive unit tests for static_blocks views.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Fast tests with minimal mocking

Tests cover:
- View method logic and context data
- Form handling and validation
- Permission checks
- Error handling
- Edge cases and boundary conditions
"""

import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from django.http import Http404, HttpResponseRedirect
from django.test import RequestFactory
from django.urls import reverse

from lfs.catalog.models import StaticBlock
from lfs.manage.static_blocks.views import (
    ManageStaticBlocksView,
    NoStaticBlocksView,
    StaticBlockTabMixin,
    StaticBlockDataView,
    StaticBlockFilesView,
    StaticBlockCreateView,
    StaticBlockDeleteConfirmView,
    StaticBlockDeleteView,
    StaticBlockPreviewView,
)

User = get_user_model()


@pytest.fixture
def request_factory():
    """Request factory for creating mock requests."""
    return RequestFactory()


@pytest.fixture
def mock_request(request_factory):
    """Mock request object for testing."""
    request = request_factory.get("/")
    request.session = {}
    # Mock messages framework for unit tests
    messages_mock = type(
        "MockMessages",
        (),
        {
            "success": lambda msg: None,
            "error": lambda msg: None,
            "add": lambda self, level, message, extra_tags="": None,
        },
    )()
    request._messages = messages_mock
    return request


@pytest.fixture
def admin_user():
    """Admin user for testing."""
    return User.objects.create_user(
        username="admin", email="admin@example.com", password="testpass123", is_staff=True, is_superuser=True
    )


@pytest.fixture
def regular_user():
    """Regular user for testing."""
    return User.objects.create_user(username="user", email="user@example.com", password="testpass123")


class TestManageStaticBlocksView:
    """Test ManageStaticBlocksView functionality."""

    @pytest.mark.django_db
    def test_get_redirect_url_with_existing_static_blocks(self, mock_request, admin_user, sample_static_blocks):
        """Test redirect URL when static blocks exist."""
        view = ManageStaticBlocksView()
        view.request = mock_request
        view.request.user = admin_user

        url = view.get_redirect_url()

        expected_url = reverse("lfs_manage_static_block", kwargs={"id": sample_static_blocks[0].id})
        assert url == expected_url

    @pytest.mark.django_db
    def test_get_redirect_url_with_no_static_blocks(self, mock_request, admin_user):
        """Test redirect URL when no static blocks exist."""
        view = ManageStaticBlocksView()
        view.request = mock_request
        view.request.user = admin_user

        url = view.get_redirect_url()

        expected_url = reverse("lfs_manage_no_static_blocks")
        assert url == expected_url

    @pytest.mark.django_db
    def test_permission_required(self, mock_request, regular_user):
        """Test that view requires proper permissions."""
        view = ManageStaticBlocksView()
        view.request = mock_request
        view.request.user = regular_user

        # PermissionRequiredMixin checks permissions in dispatch, not in individual methods
        # So this test should just verify the view has the correct permission requirement
        assert view.permission_required == "core.manage_shop"


class TestNoStaticBlocksView:
    """Test NoStaticBlocksView functionality."""

    @pytest.mark.django_db
    def test_template_name(self, mock_request, admin_user):
        """Test that view uses correct template."""
        view = NoStaticBlocksView()
        view.request = mock_request
        view.request.user = admin_user

        assert view.template_name == "manage/static_block/no_static_blocks.html"

    @pytest.mark.django_db
    def test_permission_required(self, mock_request, regular_user):
        """Test that view requires proper permissions."""
        view = NoStaticBlocksView()
        view.request = mock_request
        view.request.user = regular_user

        # PermissionRequiredMixin checks permissions in dispatch, not in individual methods
        # So this test should just verify the view has the correct permission requirement
        assert view.permission_required == "core.manage_shop"


class TestStaticBlockTabMixin:
    """Test StaticBlockTabMixin functionality."""

    @pytest.mark.django_db
    def test_get_static_block_returns_correct_object(self, mock_request, admin_user, sample_static_block):
        """Test that get_static_block returns the correct StaticBlock."""
        mixin = StaticBlockTabMixin()
        mixin.request = mock_request
        mixin.kwargs = {"id": sample_static_block.id}

        result = mixin.get_static_block()

        assert result == sample_static_block

    @pytest.mark.django_db
    def test_get_static_block_raises_404_for_invalid_id(self, mock_request, admin_user):
        """Test that get_static_block raises 404 for invalid ID."""
        mixin = StaticBlockTabMixin()
        mixin.request = mock_request
        mixin.kwargs = {"id": 99999}

        with pytest.raises(Http404):
            mixin.get_static_block()

    @pytest.mark.django_db
    def test_get_static_blocks_queryset_returns_all_blocks(self, mock_request, admin_user, sample_static_blocks):
        """Test that get_static_blocks_queryset returns all static blocks."""
        mixin = StaticBlockTabMixin()
        mixin.request = mock_request

        queryset = mixin.get_static_blocks_queryset()

        assert queryset.count() == len(sample_static_blocks)
        assert list(queryset) == list(StaticBlock.objects.all().order_by("name"))

    @pytest.mark.django_db
    def test_get_static_blocks_queryset_filters_by_search_query(self, mock_request, admin_user, sample_static_blocks):
        """Test that get_static_blocks_queryset filters by search query."""
        mixin = StaticBlockTabMixin()
        mock_request.GET = {"q": "Block 1"}
        mixin.request = mock_request

        queryset = mixin.get_static_blocks_queryset()

        assert queryset.count() == 1
        assert queryset.first().name == "Test Static Block 1"

    @pytest.mark.django_db
    def test_get_static_blocks_queryset_handles_empty_search_query(
        self, mock_request, admin_user, sample_static_blocks
    ):
        """Test that get_static_blocks_queryset handles empty search query."""
        mixin = StaticBlockTabMixin()
        mock_request.GET = {"q": ""}
        mixin.request = mock_request

        queryset = mixin.get_static_blocks_queryset()

        assert queryset.count() == len(sample_static_blocks)

    @pytest.mark.django_db
    def test_get_context_data_includes_required_keys(self, mock_request, admin_user, sample_static_block):
        """Test that get_context_data includes all required context keys."""
        from django.views.generic import TemplateView

        class TestView(StaticBlockTabMixin, TemplateView):
            pass

        view = TestView()
        view.request = mock_request
        view.kwargs = {"id": sample_static_block.id}
        view.tab_name = "data"

        context = view.get_context_data()

        assert "static_block" in context
        assert "static_blocks" in context
        assert "search_query" in context
        assert "active_tab" in context
        assert "tabs" in context

    @pytest.mark.django_db
    def test_get_context_data_uses_object_if_available(self, mock_request, admin_user, sample_static_block):
        """Test that get_context_data uses object if available."""
        from django.views.generic import TemplateView

        class TestView(StaticBlockTabMixin, TemplateView):
            pass

        view = TestView()
        view.request = mock_request
        view.kwargs = {"id": sample_static_block.id}
        view.object = sample_static_block

        context = view.get_context_data()

        assert context["static_block"] == sample_static_block

    @pytest.mark.django_db
    def test_get_tabs_returns_correct_tab_urls(self, mock_request, admin_user, sample_static_block):
        """Test that _get_tabs returns correct tab URLs."""
        mixin = StaticBlockTabMixin()
        mixin.request = mock_request
        mixin.kwargs = {"id": sample_static_block.id}

        tabs = mixin._get_tabs(sample_static_block)

        assert len(tabs) == 2
        assert tabs[0][0] == "data"
        assert tabs[1][0] == "files"
        assert "/manage/static-block/" in tabs[0][1]
        assert "/manage/static-block/" in tabs[1][1]

    @pytest.mark.django_db
    def test_get_tabs_includes_search_query_in_urls(self, mock_request, admin_user, sample_static_block):
        """Test that _get_tabs includes search query in URLs."""
        mixin = StaticBlockTabMixin()
        mock_request.GET = {"q": "test search"}
        mixin.request = mock_request
        mixin.kwargs = {"id": sample_static_block.id}

        tabs = mixin._get_tabs(sample_static_block)

        assert "q=test+search" in tabs[0][1]
        assert "q=test+search" in tabs[1][1]


class TestStaticBlockDataView:
    """Test StaticBlockDataView functionality."""

    @pytest.mark.django_db
    def test_model_is_static_block(self, mock_request, admin_user):
        """Test that view uses StaticBlock model."""
        view = StaticBlockDataView()
        assert view.model == StaticBlock

    @pytest.mark.django_db
    def test_fields_are_correct(self, mock_request, admin_user):
        """Test that view has correct fields."""
        view = StaticBlockDataView()
        assert view.fields == ["name", "html"]

    @pytest.mark.django_db
    def test_tab_name_is_data(self, mock_request, admin_user):
        """Test that view has correct tab name."""
        view = StaticBlockDataView()
        assert view.tab_name == "data"

    @pytest.mark.django_db
    def test_pk_url_kwarg_is_id(self, mock_request, admin_user):
        """Test that view uses correct URL kwarg."""
        view = StaticBlockDataView()
        assert view.pk_url_kwarg == "id"

    @pytest.mark.django_db
    def test_get_success_url_returns_correct_url(self, mock_request, admin_user, sample_static_block):
        """Test that get_success_url returns correct URL."""
        view = StaticBlockDataView()
        view.object = sample_static_block

        url = view.get_success_url()

        expected_url = reverse("lfs_manage_static_block", kwargs={"id": sample_static_block.pk})
        assert url == expected_url

    @pytest.mark.django_db
    def test_form_valid_shows_success_message(self, mock_request, admin_user, sample_static_block):
        """Test that form_valid shows success message."""
        view = StaticBlockDataView()
        view.request = mock_request
        view.object = sample_static_block

        with patch("lfs.manage.static_blocks.views.messages.success") as mock_messages:
            form = MagicMock()
            form.is_valid.return_value = True
            form.save.return_value = sample_static_block

            response = view.form_valid(form)

            mock_messages.assert_called_once_with(mock_request, "Static block has been saved.")
            assert isinstance(response, HttpResponseRedirect)


class TestStaticBlockFilesView:
    """Test StaticBlockFilesView functionality."""

    @pytest.mark.django_db
    def test_tab_name_is_files(self, mock_request, admin_user):
        """Test that view has correct tab name."""
        view = StaticBlockFilesView()
        assert view.tab_name == "files"

    @pytest.mark.django_db
    def test_template_name_is_correct(self, mock_request, admin_user):
        """Test that view uses correct template."""
        view = StaticBlockFilesView()
        assert view.template_name == "manage/static_block/static_block.html"

    @pytest.mark.django_db
    def test_form_class_is_file_upload_form(self, mock_request, admin_user):
        """Test that view uses correct form class."""
        from lfs.manage.static_blocks.forms import FileUploadForm

        view = StaticBlockFilesView()
        assert view.form_class == FileUploadForm

    @pytest.mark.django_db
    def test_get_success_url_returns_correct_url(self, mock_request, admin_user, sample_static_block):
        """Test that get_success_url returns correct URL."""
        view = StaticBlockFilesView()
        view.kwargs = {"id": sample_static_block.id}

        url = view.get_success_url()

        expected_url = reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id})
        assert url == expected_url

    @pytest.mark.django_db
    def test_post_handles_file_upload(self, mock_request, admin_user, sample_static_block):
        """Test that post method handles file upload."""
        view = StaticBlockFilesView()
        view.request = mock_request
        view.kwargs = {"id": sample_static_block.id}

        mock_file = MagicMock()
        mock_file.name = "test.txt"
        # Create a mock request with FILES
        mock_request_with_files = MagicMock()
        mock_request_with_files.FILES = {"files[]": [mock_file]}
        mock_request_with_files.POST = {}

        with patch.object(view, "_handle_file_upload") as mock_handle:
            mock_handle.return_value = HttpResponseRedirect("/success/")

            response = view.post(mock_request_with_files)

            mock_handle.assert_called_once_with(mock_request_with_files)
            assert isinstance(response, HttpResponseRedirect)

    @pytest.mark.django_db
    def test_post_handles_file_update(self, mock_request, admin_user, sample_static_block):
        """Test that post method handles file update."""
        view = StaticBlockFilesView()
        view.request = mock_request
        view.kwargs = {"id": sample_static_block.id}

        # Create a mock request with POST data
        mock_request_with_post = MagicMock()
        mock_request_with_post.POST = {"update": "true"}
        mock_request_with_post.FILES = {}

        with patch.object(view, "_handle_file_update") as mock_handle:
            mock_handle.return_value = HttpResponseRedirect("/success/")

            response = view.post(mock_request_with_post)

            mock_handle.assert_called_once_with(mock_request_with_post)
            assert isinstance(response, HttpResponseRedirect)

    @pytest.mark.django_db
    def test_post_handles_file_delete(self, mock_request, admin_user, sample_static_block):
        """Test that post method handles file delete."""
        view = StaticBlockFilesView()
        view.request = mock_request
        view.kwargs = {"id": sample_static_block.id}

        # Create a mock request with POST data
        mock_request_with_post = MagicMock()
        mock_request_with_post.POST = {"delete": "true"}
        mock_request_with_post.FILES = {}

        with patch.object(view, "_handle_file_delete") as mock_handle:
            mock_handle.return_value = HttpResponseRedirect("/success/")

            response = view.post(mock_request_with_post)

            mock_handle.assert_called_once_with(mock_request_with_post)
            assert isinstance(response, HttpResponseRedirect)

    @pytest.mark.django_db
    def test_refresh_file_positions_updates_positions(
        self, mock_request, admin_user, sample_static_block, sample_files
    ):
        """Test that _refresh_file_positions updates file positions."""
        view = StaticBlockFilesView()
        view.request = mock_request
        view.kwargs = {"id": sample_static_block.id}

        view._refresh_file_positions()

        files = sample_static_block.files.all().order_by("id")
        for i, file in enumerate(files):
            assert file.position == (i + 1) * 10

    @pytest.mark.django_db
    def test_delete_files_by_keys_deletes_correct_files(
        self, mock_request, admin_user, sample_static_block, sample_files
    ):
        """Test that _delete_files_by_keys deletes correct files."""
        view = StaticBlockFilesView()
        view.request = mock_request
        view.kwargs = {"id": sample_static_block.id}

        file_to_delete = sample_files[0]
        mock_request.POST = {f"delete-{file_to_delete.id}": "true"}

        initial_count = sample_static_block.files.count()
        view._delete_files_by_keys(mock_request)
        final_count = sample_static_block.files.count()

        assert final_count == initial_count - 1
        assert not sample_static_block.files.filter(id=file_to_delete.id).exists()

    @pytest.mark.django_db
    def test_update_files_by_keys_updates_titles(self, mock_request, admin_user, sample_static_block, sample_files):
        """Test that _update_files_by_keys updates file titles."""
        view = StaticBlockFilesView()
        view.request = mock_request
        view.kwargs = {"id": sample_static_block.id}

        file_to_update = sample_files[0]
        new_title = "Updated Title"
        mock_request.POST = {f"title-{file_to_update.id}": new_title}

        view._update_files_by_keys(mock_request)

        file_to_update.refresh_from_db()
        assert file_to_update.title == new_title

    @pytest.mark.django_db
    def test_update_files_by_keys_updates_positions(self, mock_request, admin_user, sample_static_block, sample_files):
        """Test that _update_files_by_keys updates file positions."""
        view = StaticBlockFilesView()
        view.request = mock_request
        view.kwargs = {"id": sample_static_block.id}

        file_to_update = sample_files[0]
        new_position = 99
        mock_request.POST = {f"position-{file_to_update.id}": str(new_position)}

        view._update_files_by_keys(mock_request)

        file_to_update.refresh_from_db()
        assert file_to_update.position == new_position


class TestStaticBlockCreateView:
    """Test StaticBlockCreateView functionality."""

    @pytest.mark.django_db
    def test_model_is_static_block(self, mock_request, admin_user):
        """Test that view uses StaticBlock model."""
        view = StaticBlockCreateView()
        assert view.model == StaticBlock

    @pytest.mark.django_db
    def test_fields_are_correct(self, mock_request, admin_user):
        """Test that view has correct fields."""
        view = StaticBlockCreateView()
        assert view.fields == ["name"]

    @pytest.mark.django_db
    def test_template_name_is_correct(self, mock_request, admin_user):
        """Test that view uses correct template."""
        view = StaticBlockCreateView()
        assert view.template_name == "manage/static_block/add_static_block.html"

    @pytest.mark.django_db
    def test_success_message_is_correct(self, mock_request, admin_user):
        """Test that view has correct success message."""
        view = StaticBlockCreateView()
        assert view.success_message == "Static block has been created."

    @pytest.mark.django_db
    def test_get_success_url_returns_correct_url(self, mock_request, admin_user, sample_static_block):
        """Test that get_success_url returns correct URL."""
        view = StaticBlockCreateView()
        view.object = sample_static_block

        url = view.get_success_url()

        expected_url = reverse("lfs_manage_static_block", kwargs={"id": sample_static_block.id})
        assert url == expected_url


class TestStaticBlockDeleteConfirmView:
    """Test StaticBlockDeleteConfirmView functionality."""

    @pytest.mark.django_db
    def test_template_name_is_correct(self, mock_request, admin_user):
        """Test that view uses correct template."""
        view = StaticBlockDeleteConfirmView()
        assert view.template_name == "manage/static_block/delete_static_block.html"

    @pytest.mark.django_db
    def test_get_context_data_includes_static_block(self, mock_request, admin_user, sample_static_block):
        """Test that get_context_data includes static_block."""
        view = StaticBlockDeleteConfirmView()
        view.request = mock_request
        view.kwargs = {"id": sample_static_block.id}

        context = view.get_context_data()

        assert "static_block" in context
        assert context["static_block"] == sample_static_block


class TestStaticBlockDeleteView:
    """Test StaticBlockDeleteView functionality."""

    @pytest.mark.django_db
    def test_model_is_static_block(self, mock_request, admin_user):
        """Test that view uses StaticBlock model."""
        view = StaticBlockDeleteView()
        assert view.model == StaticBlock

    @pytest.mark.django_db
    def test_pk_url_kwarg_is_id(self, mock_request, admin_user):
        """Test that view uses correct URL kwarg."""
        view = StaticBlockDeleteView()
        assert view.pk_url_kwarg == "id"

    @pytest.mark.django_db
    def test_success_message_is_correct(self, mock_request, admin_user):
        """Test that view has correct success message."""
        view = StaticBlockDeleteView()
        assert view.success_message == "Static block has been deleted."

    @pytest.mark.django_db
    def test_get_success_url_returns_correct_url(self, mock_request, admin_user):
        """Test that get_success_url returns correct URL."""
        view = StaticBlockDeleteView()

        url = view.get_success_url()

        expected_url = reverse("lfs_manage_static_blocks")
        assert url == expected_url


class TestStaticBlockPreviewView:
    """Test StaticBlockPreviewView functionality."""

    @pytest.mark.django_db
    def test_template_name_is_correct(self, mock_request, admin_user):
        """Test that view uses correct template."""
        view = StaticBlockPreviewView()
        assert view.template_name == "manage/static_block/preview.html"

    @pytest.mark.django_db
    def test_get_context_data_includes_static_block(self, mock_request, admin_user, sample_static_block):
        """Test that get_context_data includes static_block."""
        view = StaticBlockPreviewView()
        view.request = mock_request
        view.kwargs = {"id": sample_static_block.id}

        context = view.get_context_data()

        assert "static_block" in context
        assert context["static_block"] == sample_static_block
