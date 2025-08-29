"""
Test utilities for StaticBlock operations.

Testing utility functions that were extracted from views.
"""

import pytest
from lfs.catalog.models import File
from lfs.manage.static_blocks.views import refresh_file_positions, delete_files_by_keys, update_files_by_keys


@pytest.mark.django_db
class TestRefreshFilePositions:
    """Tests for refresh_file_positions utility function."""

    def test_sets_sequential_positions_for_files(self, static_block, files_for_static_block):
        """Should set positions in increments of 10 for all files."""
        # Update files to have random positions
        files_for_static_block[0].position = 100
        files_for_static_block[0].save()
        files_for_static_block[1].position = 5
        files_for_static_block[1].save()
        files_for_static_block[2].position = 50
        files_for_static_block[2].save()

        refresh_file_positions(static_block)

        # Refresh from database
        for file_obj in files_for_static_block:
            file_obj.refresh_from_db()

        # Files should be ordered by their creation order with positions 10, 20, 30
        files = list(static_block.files.all().order_by("pk"))
        # Check that positions are normalized to 10, 20, 30 in creation order
        positions = [f.position for f in files]
        assert set(positions) == {10, 20, 30}  # All files have correct position values

    def test_handles_static_block_with_no_files(self, static_block):
        """Should handle StaticBlock with no files without error."""
        # Should not raise any exception
        refresh_file_positions(static_block)

        assert static_block.files.count() == 0


@pytest.mark.django_db
class TestDeleteFilesByKeys:
    """Tests for delete_files_by_keys utility function."""

    def test_deletes_files_marked_for_deletion(self, files_for_static_block, request_factory):
        """Should delete files that have delete-* keys in POST data."""
        file1, file2, file3 = files_for_static_block

        # Create request with delete keys for file1 and file3
        request = request_factory.post(
            "/", {f"delete-{file1.id}": "on", f"delete-{file3.id}": "on", "other_field": "value"}
        )

        delete_files_by_keys(request)

        # file1 and file3 should be deleted, file2 should remain
        assert not File.objects.filter(id=file1.id).exists()
        assert File.objects.filter(id=file2.id).exists()
        assert not File.objects.filter(id=file3.id).exists()

    @pytest.mark.parametrize(
        "post_data,description",
        [
            ({"delete-99999": "on"}, "non-existent file ID"),
            ({"delete-invalid": "on"}, "invalid format"),
            ({"delete-": "on"}, "empty ID"),
            ({"delete-0": "on"}, "zero ID"),
            ({"delete--1": "on"}, "negative ID"),
        ],
    )
    def test_handles_invalid_file_ids_gracefully(self, request_factory, post_data, description):
        """Should handle invalid file IDs without raising errors."""
        request = request_factory.post("/", post_data)

        # Should not raise any exception
        delete_files_by_keys(request)

    def test_ignores_non_delete_keys(self, single_file, request_factory):
        """Should only process keys that start with 'delete-'."""
        request = request_factory.post("/", {"title-123": "Some title", "position-456": "10", "random_field": "value"})

        delete_files_by_keys(request)

        # File should still exist
        assert File.objects.filter(id=single_file.id).exists()


@pytest.mark.django_db
class TestUpdateFilesByKeys:
    """Tests for update_files_by_keys utility function."""

    def test_updates_file_titles(self, files_for_static_block, request_factory):
        """Should update file titles based on title-* keys."""
        file1, file2 = files_for_static_block[:2]
        file1.title = "Old Title 1"
        file1.save()
        file2.title = "Old Title 2"
        file2.save()

        request = request_factory.post("/", {f"title-{file1.id}": "New Title 1", f"title-{file2.id}": "New Title 2"})

        update_files_by_keys(request)

        file1.refresh_from_db()
        file2.refresh_from_db()
        assert file1.title == "New Title 1"
        assert file2.title == "New Title 2"

    def test_updates_file_positions(self, files_for_static_block, request_factory):
        """Should update file positions based on position-* keys."""
        file1, file2 = files_for_static_block[:2]

        request = request_factory.post("/", {f"position-{file1.id}": "30", f"position-{file2.id}": "40"})

        update_files_by_keys(request)

        file1.refresh_from_db()
        file2.refresh_from_db()
        assert file1.position == 30
        assert file2.position == 40

    @pytest.mark.parametrize(
        "post_data,description",
        [
            ({"title-99999": "New Title"}, "non-existent file title update"),
            ({"position-99999": "50"}, "non-existent file position update"),
            ({"title-invalid": "Title"}, "invalid file ID for title"),
            ({"position-invalid": "10"}, "invalid file ID for position"),
            ({"title-": "Empty ID"}, "empty file ID for title"),
            ({"position-": "20"}, "empty file ID for position"),
        ],
    )
    def test_handles_nonexistent_files_gracefully(self, request_factory, post_data, description):
        """Should handle updates for non-existent files without errors."""
        request = request_factory.post("/", post_data)

        # Should not raise any exception
        update_files_by_keys(request)

    def test_updates_both_title_and_position(self, single_file, request_factory):
        """Should update both title and position for the same file."""
        single_file.title = "Old Title"
        single_file.position = 10
        single_file.save()

        request = request_factory.post(
            "/", {f"title-{single_file.id}": "New Title", f"position-{single_file.id}": "50"}
        )

        update_files_by_keys(request)

        single_file.refresh_from_db()
        assert single_file.title == "New Title"
        assert single_file.position == 50
