"""
Edge cases and integration tests for static_blocks.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Fast tests with minimal mocking

Tests cover:
- Edge cases and boundary conditions
- Error handling and exception scenarios
- Integration between components
- Performance and scalability concerns
"""

import pytest
from unittest.mock import MagicMock
from django.http import Http404
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from lfs.catalog.models import StaticBlock, File

User = get_user_model()


@pytest.fixture
def client():
    """Django test client."""
    return Client()


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


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.django_db
    def test_manage_static_blocks_view_with_no_blocks(self, client, admin_user):
        """Test ManageStaticBlocksView when no static blocks exist."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_manage_static_blocks"))

        assert response.status_code == 302
        assert response.url == reverse("lfs_manage_no_static_blocks")

    @pytest.mark.django_db
    def test_static_block_data_view_with_invalid_id(self, client, admin_user):
        """Test StaticBlockDataView with invalid ID."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_manage_static_block", kwargs={"id": 99999}))

        assert response.status_code == 404

    @pytest.mark.django_db
    def test_static_block_files_view_with_invalid_id(self, client, admin_user):
        """Test StaticBlockFilesView with invalid ID."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_manage_static_block_files", kwargs={"id": 99999}))

        assert response.status_code == 404

    @pytest.mark.django_db
    def test_static_block_create_view_with_empty_name(self, client, admin_user):
        """Test StaticBlockCreateView with empty name."""
        client.force_login(admin_user)
        response = client.post(reverse("lfs_manage_add_static_block"), {"name": ""})

        assert response.status_code == 200
        assert "name" in response.context["form"].errors

    @pytest.mark.django_db
    def test_static_block_create_view_with_very_long_name(self, client, admin_user):
        """Test StaticBlockCreateView with very long name."""
        client.force_login(admin_user)
        long_name = "a" * 1000
        response = client.post(reverse("lfs_manage_add_static_block"), {"name": long_name})

        # The form might validate and return 200 with errors, or succeed with 302
        assert response.status_code in [200, 302]
        if response.status_code == 302:
            assert StaticBlock.objects.filter(name=long_name).exists()

    @pytest.mark.django_db
    def test_static_block_delete_view_with_invalid_id(self, client, admin_user):
        """Test StaticBlockDeleteView with invalid ID."""
        client.force_login(admin_user)
        response = client.post(reverse("lfs_delete_static_block", kwargs={"id": 99999}))

        assert response.status_code == 404

    @pytest.mark.django_db
    def test_static_block_tab_mixin_with_nonexistent_id(self, sample_static_block):
        """Test StaticBlockTabMixin with nonexistent ID."""
        from lfs.manage.static_blocks.views import StaticBlockTabMixin

        mixin = StaticBlockTabMixin()
        mixin.request = MagicMock()
        mixin.kwargs = {"id": 0}

        with pytest.raises(Http404):
            mixin.get_static_block()

    @pytest.mark.django_db
    def test_static_block_tab_mixin_with_negative_id(self, sample_static_block):
        """Test StaticBlockTabMixin with negative ID."""
        from lfs.manage.static_blocks.views import StaticBlockTabMixin

        mixin = StaticBlockTabMixin()
        mixin.request = MagicMock()
        mixin.kwargs = {"id": -1}

        with pytest.raises(Http404):
            mixin.get_static_block()

    @pytest.mark.django_db
    def test_static_block_tab_mixin_with_string_id(self, sample_static_block):
        """Test StaticBlockTabMixin with string ID."""
        from lfs.manage.static_blocks.views import StaticBlockTabMixin

        mixin = StaticBlockTabMixin()
        mixin.request = MagicMock()
        mixin.kwargs = {"id": "invalid"}

        # Django's get_object_or_404 will raise ValueError for invalid string IDs
        with pytest.raises(ValueError):
            mixin.get_static_block()

    @pytest.mark.django_db
    def test_static_block_files_view_with_no_files(self, client, admin_user, sample_static_block):
        """Test StaticBlockFilesView with no files."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}))

        assert response.status_code == 200
        assert "static_block" in response.context

    @pytest.mark.django_db
    def test_static_block_files_view_with_many_files(self, client, admin_user, sample_static_block):
        """Test StaticBlockFilesView with many files."""
        # Create many files
        for i in range(100):
            File.objects.create(
                content=sample_static_block,
                title=f"file_{i}.txt",
                file=f"file_{i}.txt",
                position=i * 10,
            )

        client.force_login(admin_user)
        response = client.get(reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}))

        assert response.status_code == 200
        assert sample_static_block.files.count() == 100

    @pytest.mark.django_db
    def test_static_block_data_view_with_very_long_html(self, client, admin_user, sample_static_block):
        """Test StaticBlockDataView with very long HTML."""
        client.force_login(admin_user)
        long_html = "<p>" + "a" * 10000 + "</p>"
        response = client.post(
            reverse("lfs_manage_static_block", kwargs={"id": sample_static_block.id}),
            {"name": sample_static_block.name, "html": long_html},
        )

        assert response.status_code == 302
        sample_static_block.refresh_from_db()
        assert sample_static_block.html == long_html

    @pytest.mark.django_db
    def test_static_block_data_view_with_special_characters_in_html(self, client, admin_user, sample_static_block):
        """Test StaticBlockDataView with special characters in HTML."""
        client.force_login(admin_user)
        special_html = "<p>&lt;script&gt;alert('test')&lt;/script&gt;</p>"
        response = client.post(
            reverse("lfs_manage_static_block", kwargs={"id": sample_static_block.id}),
            {"name": sample_static_block.name, "html": special_html},
        )

        assert response.status_code == 302
        sample_static_block.refresh_from_db()
        assert sample_static_block.html == special_html

    @pytest.mark.django_db
    def test_static_block_data_view_with_unicode_in_html(self, client, admin_user, sample_static_block):
        """Test StaticBlockDataView with unicode in HTML."""
        client.force_login(admin_user)
        unicode_html = "<p>Hello 世界 🌍</p>"
        response = client.post(
            reverse("lfs_manage_static_block", kwargs={"id": sample_static_block.id}),
            {"name": sample_static_block.name, "html": unicode_html},
        )

        assert response.status_code == 302
        sample_static_block.refresh_from_db()
        assert sample_static_block.html == unicode_html

    @pytest.mark.django_db
    def test_static_block_search_with_special_characters(self, client, admin_user, sample_static_blocks):
        """Test static block search with special characters."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_manage_static_blocks"), {"q": "Test & Block"})

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_search_with_unicode(self, client, admin_user, sample_static_blocks):
        """Test static block search with unicode."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_manage_static_blocks"), {"q": "Tëst Blöck"})

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_search_with_very_long_query(self, client, admin_user, sample_static_blocks):
        """Test static block search with very long query."""
        client.force_login(admin_user)
        long_query = "a" * 1000
        response = client.get(reverse("lfs_manage_static_blocks"), {"q": long_query})

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_files_view_with_invalid_file_id(self, client, admin_user, sample_static_block):
        """Test StaticBlockFilesView with invalid file ID."""
        client.force_login(admin_user)
        response = client.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}), {"delete-99999": "true"}
        )

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_files_view_with_invalid_position(self, client, admin_user, sample_static_block, sample_file):
        """Test StaticBlockFilesView with invalid position."""
        client.force_login(admin_user)
        response = client.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}),
            {f"position-{sample_file.id}": "invalid"},
        )

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_files_view_with_negative_position(self, client, admin_user, sample_static_block, sample_file):
        """Test StaticBlockFilesView with negative position."""
        client.force_login(admin_user)
        response = client.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}),
            {f"position-{sample_file.id}": "-1"},
        )

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_files_view_with_very_large_position(
        self, client, admin_user, sample_static_block, sample_file
    ):
        """Test StaticBlockFilesView with very large position."""
        client.force_login(admin_user)
        response = client.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}),
            {f"position-{sample_file.id}": "999999999"},
        )

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_files_view_with_empty_title(self, client, admin_user, sample_static_block, sample_file):
        """Test StaticBlockFilesView with empty title."""
        client.force_login(admin_user)
        response = client.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}),
            {f"title-{sample_file.id}": ""},
        )

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_files_view_with_very_long_title(self, client, admin_user, sample_static_block, sample_file):
        """Test StaticBlockFilesView with very long title."""
        client.force_login(admin_user)
        long_title = "a" * 1000
        response = client.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}),
            {f"title-{sample_file.id}": long_title},
        )

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_files_view_with_unicode_title(self, client, admin_user, sample_static_block, sample_file):
        """Test StaticBlockFilesView with unicode title."""
        client.force_login(admin_user)
        unicode_title = "Tëst Fïle 世界 🌍"
        response = client.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}),
            {f"title-{sample_file.id}": unicode_title},
        )

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_files_view_with_special_characters_title(
        self, client, admin_user, sample_static_block, sample_file
    ):
        """Test StaticBlockFilesView with special characters title."""
        client.force_login(admin_user)
        special_title = "Test & File <script>alert('test')</script>"
        response = client.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}),
            {f"title-{sample_file.id}": special_title},
        )

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_create_view_with_duplicate_name(self, client, admin_user, sample_static_block):
        """Test StaticBlockCreateView with duplicate name."""
        client.force_login(admin_user)
        response = client.post(reverse("lfs_manage_add_static_block"), {"name": sample_static_block.name})

        assert response.status_code == 302
        assert StaticBlock.objects.filter(name=sample_static_block.name).count() == 2

    @pytest.mark.django_db
    def test_static_block_delete_view_with_nonexistent_id(self, client, admin_user):
        """Test StaticBlockDeleteView with nonexistent ID."""
        client.force_login(admin_user)
        response = client.post(reverse("lfs_delete_static_block", kwargs={"id": 0}))

        assert response.status_code == 404

    @pytest.mark.django_db
    def test_static_block_delete_view_with_negative_id(self, client, admin_user):
        """Test StaticBlockDeleteView with negative ID."""
        client.force_login(admin_user)
        # Django URL routing prevents negative IDs from reaching the view
        with pytest.raises(Exception):  # NoReverseMatch or similar
            reverse("lfs_delete_static_block", kwargs={"id": -1})

    @pytest.mark.django_db
    def test_static_block_delete_view_with_string_id(self, client, admin_user):
        """Test StaticBlockDeleteView with string ID."""
        client.force_login(admin_user)
        # Django URL routing prevents invalid IDs from reaching the view
        with pytest.raises(Exception):  # NoReverseMatch or similar
            reverse("lfs_delete_static_block", kwargs={"id": "invalid"})

    @pytest.mark.django_db
    def test_static_block_preview_view_with_invalid_id(self, client, admin_user):
        """Test StaticBlockPreviewView with invalid ID."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_preview_static_block", kwargs={"id": 99999}))

        assert response.status_code == 404

    @pytest.mark.django_db
    def test_static_block_preview_view_with_nonexistent_id(self, client, admin_user):
        """Test StaticBlockPreviewView with nonexistent ID."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_preview_static_block", kwargs={"id": 0}))

        assert response.status_code == 404

    @pytest.mark.django_db
    def test_static_block_preview_view_with_negative_id(self, client, admin_user):
        """Test StaticBlockPreviewView with negative ID."""
        client.force_login(admin_user)
        # Django URL routing prevents negative IDs from reaching the view
        with pytest.raises(Exception):  # NoReverseMatch or similar
            reverse("lfs_preview_static_block", kwargs={"id": -1})

    @pytest.mark.django_db
    def test_static_block_preview_view_with_string_id(self, client, admin_user):
        """Test StaticBlockPreviewView with string ID."""
        client.force_login(admin_user)
        # Django URL routing prevents invalid IDs from reaching the view
        with pytest.raises(Exception):  # NoReverseMatch or similar
            reverse("lfs_preview_static_block", kwargs={"id": "invalid"})

    @pytest.mark.django_db
    def test_static_block_delete_confirm_view_with_invalid_id(self, client, admin_user):
        """Test StaticBlockDeleteConfirmView with invalid ID."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_manage_delete_static_block_confirm", kwargs={"id": 99999}))

        assert response.status_code == 404

    @pytest.mark.django_db
    def test_static_block_delete_confirm_view_with_nonexistent_id(self, client, admin_user):
        """Test StaticBlockDeleteConfirmView with nonexistent ID."""
        client.force_login(admin_user)
        response = client.get(reverse("lfs_manage_delete_static_block_confirm", kwargs={"id": 0}))

        assert response.status_code == 404

    @pytest.mark.django_db
    def test_static_block_delete_confirm_view_with_negative_id(self, client, admin_user):
        """Test StaticBlockDeleteConfirmView with negative ID."""
        client.force_login(admin_user)
        # Django URL routing prevents negative IDs from reaching the view
        with pytest.raises(Exception):  # NoReverseMatch or similar
            reverse("lfs_manage_delete_static_block_confirm", kwargs={"id": -1})

    @pytest.mark.django_db
    def test_static_block_delete_confirm_view_with_string_id(self, client, admin_user):
        """Test StaticBlockDeleteConfirmView with string ID."""
        client.force_login(admin_user)
        # Django URL routing prevents invalid IDs from reaching the view
        with pytest.raises(Exception):  # NoReverseMatch or similar
            reverse("lfs_manage_delete_static_block_confirm", kwargs={"id": "invalid"})

    @pytest.mark.django_db
    def test_static_block_files_view_with_malformed_post_data(self, client, admin_user, sample_static_block):
        """Test StaticBlockFilesView with malformed POST data."""
        client.force_login(admin_user)
        response = client.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}), {"malformed": "data"}
        )

        # The view redirects even with malformed data
        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_files_view_with_empty_post_data(self, client, admin_user, sample_static_block):
        """Test StaticBlockFilesView with empty POST data."""
        client.force_login(admin_user)
        response = client.post(reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}), {})

        # The view redirects even with empty POST data
        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_files_view_with_nonexistent_file_id_in_update(self, client, admin_user, sample_static_block):
        """Test StaticBlockFilesView with nonexistent file ID in update."""
        client.force_login(admin_user)
        response = client.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}),
            {"update": "true", "title-99999": "New Title"},
        )

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_files_view_with_nonexistent_file_id_in_delete(self, client, admin_user, sample_static_block):
        """Test StaticBlockFilesView with nonexistent file ID in delete."""
        client.force_login(admin_user)
        response = client.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}),
            {"delete": "true", "delete-99999": "true"},
        )

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_files_view_with_nonexistent_file_id_in_position_update(
        self, client, admin_user, sample_static_block
    ):
        """Test StaticBlockFilesView with nonexistent file ID in position update."""
        client.force_login(admin_user)
        response = client.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}),
            {"update": "true", "position-99999": "10"},
        )

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_files_view_with_invalid_file_id_format(self, client, admin_user, sample_static_block):
        """Test StaticBlockFilesView with invalid file ID format."""
        client.force_login(admin_user)
        response = client.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}),
            {"update": "true", "title-invalid": "New Title"},
        )

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_files_view_with_invalid_file_id_format_in_delete(
        self, client, admin_user, sample_static_block
    ):
        """Test StaticBlockFilesView with invalid file ID format in delete."""
        client.force_login(admin_user)
        response = client.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}),
            {"delete": "true", "delete-invalid": "true"},
        )

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_files_view_with_invalid_file_id_format_in_position_update(
        self, client, admin_user, sample_static_block
    ):
        """Test StaticBlockFilesView with invalid file ID format in position update."""
        client.force_login(admin_user)
        response = client.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}),
            {"update": "true", "position-invalid": "10"},
        )

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_files_view_with_empty_file_id_in_update(self, client, admin_user, sample_static_block):
        """Test StaticBlockFilesView with empty file ID in update."""
        client.force_login(admin_user)
        response = client.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}),
            {"update": "true", "title-": "New Title"},
        )

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_files_view_with_empty_file_id_in_delete(self, client, admin_user, sample_static_block):
        """Test StaticBlockFilesView with empty file ID in delete."""
        client.force_login(admin_user)
        response = client.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}),
            {"delete": "true", "delete-": "true"},
        )

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_files_view_with_empty_file_id_in_position_update(
        self, client, admin_user, sample_static_block
    ):
        """Test StaticBlockFilesView with empty file ID in position update."""
        client.force_login(admin_user)
        response = client.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}),
            {"update": "true", "position-": "10"},
        )

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_files_view_with_whitespace_file_id_in_update(self, client, admin_user, sample_static_block):
        """Test StaticBlockFilesView with whitespace file ID in update."""
        client.force_login(admin_user)
        response = client.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}),
            {"update": "true", "title- ": "New Title"},
        )

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_files_view_with_whitespace_file_id_in_delete(self, client, admin_user, sample_static_block):
        """Test StaticBlockFilesView with whitespace file ID in delete."""
        client.force_login(admin_user)
        response = client.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}),
            {"delete": "true", "delete- ": "true"},
        )

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_files_view_with_whitespace_file_id_in_position_update(
        self, client, admin_user, sample_static_block
    ):
        """Test StaticBlockFilesView with whitespace file ID in position update."""
        client.force_login(admin_user)
        response = client.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}),
            {"update": "true", "position- ": "10"},
        )

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_files_view_with_nonexistent_file_id_in_title_update(
        self, client, admin_user, sample_static_block
    ):
        """Test StaticBlockFilesView with nonexistent file ID in title update."""
        client.force_login(admin_user)
        response = client.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}),
            {"update": "true", "title-99999": "New Title"},
        )

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_files_view_with_nonexistent_file_id_in_position_update(
        self, client, admin_user, sample_static_block
    ):
        """Test StaticBlockFilesView with nonexistent file ID in position update."""
        client.force_login(admin_user)
        response = client.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}),
            {"update": "true", "position-99999": "10"},
        )

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_files_view_with_nonexistent_file_id_in_delete(self, client, admin_user, sample_static_block):
        """Test StaticBlockFilesView with nonexistent file ID in delete."""
        client.force_login(admin_user)
        response = client.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}),
            {"delete": "true", "delete-99999": "true"},
        )

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_files_view_with_invalid_file_id_format_in_title_update(
        self, client, admin_user, sample_static_block
    ):
        """Test StaticBlockFilesView with invalid file ID format in title update."""
        client.force_login(admin_user)
        response = client.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}),
            {"update": "true", "title-invalid": "New Title"},
        )

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_files_view_with_invalid_file_id_format_in_position_update(
        self, client, admin_user, sample_static_block
    ):
        """Test StaticBlockFilesView with invalid file ID format in position update."""
        client.force_login(admin_user)
        response = client.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}),
            {"update": "true", "position-invalid": "10"},
        )

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_files_view_with_invalid_file_id_format_in_delete(
        self, client, admin_user, sample_static_block
    ):
        """Test StaticBlockFilesView with invalid file ID format in delete."""
        client.force_login(admin_user)
        response = client.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}),
            {"delete": "true", "delete-invalid": "true"},
        )

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_files_view_with_empty_file_id_in_title_update(self, client, admin_user, sample_static_block):
        """Test StaticBlockFilesView with empty file ID in title update."""
        client.force_login(admin_user)
        response = client.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}),
            {"update": "true", "title-": "New Title"},
        )

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_files_view_with_empty_file_id_in_position_update(
        self, client, admin_user, sample_static_block
    ):
        """Test StaticBlockFilesView with empty file ID in position update."""
        client.force_login(admin_user)
        response = client.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}),
            {"update": "true", "position-": "10"},
        )

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_files_view_with_empty_file_id_in_delete(self, client, admin_user, sample_static_block):
        """Test StaticBlockFilesView with empty file ID in delete."""
        client.force_login(admin_user)
        response = client.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}),
            {"delete": "true", "delete-": "true"},
        )

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_files_view_with_whitespace_file_id_in_title_update(
        self, client, admin_user, sample_static_block
    ):
        """Test StaticBlockFilesView with whitespace file ID in title update."""
        client.force_login(admin_user)
        response = client.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}),
            {"update": "true", "title- ": "New Title"},
        )

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_files_view_with_whitespace_file_id_in_position_update(
        self, client, admin_user, sample_static_block
    ):
        """Test StaticBlockFilesView with whitespace file ID in position update."""
        client.force_login(admin_user)
        response = client.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}),
            {"update": "true", "position- ": "10"},
        )

        assert response.status_code == 302

    @pytest.mark.django_db
    def test_static_block_files_view_with_whitespace_file_id_in_delete(self, client, admin_user, sample_static_block):
        """Test StaticBlockFilesView with whitespace file ID in delete."""
        client.force_login(admin_user)
        response = client.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": sample_static_block.id}),
            {"delete": "true", "delete- ": "true"},
        )

        assert response.status_code == 302
