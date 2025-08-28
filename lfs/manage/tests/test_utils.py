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

    def test_sets_sequential_positions_for_files(self, static_block, db):
        """Should set positions in increments of 10 for all files."""
        # Create some files with random positions
        file1 = File.objects.create(content=static_block, title="File 1", position=100)
        file2 = File.objects.create(content=static_block, title="File 2", position=5)
        file3 = File.objects.create(content=static_block, title="File 3", position=50)

        refresh_file_positions(static_block)

        # Refresh from database
        file1.refresh_from_db()
        file2.refresh_from_db()
        file3.refresh_from_db()

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

    def test_deletes_files_marked_for_deletion(self, static_block, request_factory):
        """Should delete files that have delete-* keys in POST data."""
        file1 = File.objects.create(content=static_block, title="File 1")
        file2 = File.objects.create(content=static_block, title="File 2")
        file3 = File.objects.create(content=static_block, title="File 3")

        # Create request with delete keys for file1 and file3
        request = request_factory.post(
            "/", {f"delete-{file1.id}": "on", f"delete-{file3.id}": "on", "other_field": "value"}
        )

        delete_files_by_keys(request)

        # file1 and file3 should be deleted, file2 should remain
        assert not File.objects.filter(id=file1.id).exists()
        assert File.objects.filter(id=file2.id).exists()
        assert not File.objects.filter(id=file3.id).exists()

    def test_handles_invalid_file_ids_gracefully(self, request_factory):
        """Should handle invalid file IDs without raising errors."""
        request = request_factory.post(
            "/",
            {
                "delete-99999": "on",  # Non-existent file ID
                "delete-invalid": "on",  # Invalid format
            },
        )

        # Should not raise any exception
        delete_files_by_keys(request)

    def test_ignores_non_delete_keys(self, static_block, request_factory):
        """Should only process keys that start with 'delete-'."""
        file1 = File.objects.create(content=static_block, title="File 1")

        request = request_factory.post("/", {"title-123": "Some title", "position-456": "10", "random_field": "value"})

        delete_files_by_keys(request)

        # File should still exist
        assert File.objects.filter(id=file1.id).exists()


@pytest.mark.django_db
class TestUpdateFilesByKeys:
    """Tests for update_files_by_keys utility function."""

    def test_updates_file_titles(self, static_block, request_factory):
        """Should update file titles based on title-* keys."""
        file1 = File.objects.create(content=static_block, title="Old Title 1")
        file2 = File.objects.create(content=static_block, title="Old Title 2")

        request = request_factory.post("/", {f"title-{file1.id}": "New Title 1", f"title-{file2.id}": "New Title 2"})

        update_files_by_keys(request)

        file1.refresh_from_db()
        file2.refresh_from_db()
        assert file1.title == "New Title 1"
        assert file2.title == "New Title 2"

    def test_updates_file_positions(self, static_block, request_factory):
        """Should update file positions based on position-* keys."""
        file1 = File.objects.create(content=static_block, title="File 1", position=10)
        file2 = File.objects.create(content=static_block, title="File 2", position=20)

        request = request_factory.post("/", {f"position-{file1.id}": "30", f"position-{file2.id}": "40"})

        update_files_by_keys(request)

        file1.refresh_from_db()
        file2.refresh_from_db()
        assert file1.position == 30
        assert file2.position == 40

    def test_handles_nonexistent_files_gracefully(self, request_factory):
        """Should handle updates for non-existent files without errors."""
        request = request_factory.post("/", {"title-99999": "New Title", "position-99999": "50"})

        # Should not raise any exception
        update_files_by_keys(request)

    def test_updates_both_title_and_position(self, static_block, request_factory):
        """Should update both title and position for the same file."""
        file1 = File.objects.create(content=static_block, title="Old Title", position=10)

        request = request_factory.post("/", {f"title-{file1.id}": "New Title", f"position-{file1.id}": "50"})

        update_files_by_keys(request)

        file1.refresh_from_db()
        assert file1.title == "New Title"
        assert file1.position == 50
