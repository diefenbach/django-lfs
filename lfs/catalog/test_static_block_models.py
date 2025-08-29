"""
Unit tests for StaticBlock model.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Parametrization for variations

Tests cover:
- Model creation and field defaults
- String representation
- Field validation and constraints
- Model ordering
- Generic relation to File objects
- Meta class configuration
"""

import pytest
from django.core.exceptions import ValidationError

from lfs.catalog.models import StaticBlock, File


@pytest.mark.django_db
class TestStaticBlockCreation:
    """Tests for StaticBlock model creation and field defaults."""

    def test_create_static_block_with_required_fields(self):
        """Should create StaticBlock with only required name field."""
        static_block = StaticBlock.objects.create(name="Test Block")

        assert static_block.name == "Test Block"
        assert static_block.pk is not None

    def test_static_block_default_field_values(self):
        """Should set correct default values for optional fields."""
        static_block = StaticBlock.objects.create(name="Test Block")

        assert static_block.display_files is True
        assert static_block.html == ""
        assert static_block.position == 1000

    @pytest.mark.parametrize(
        "field_name,custom_value",
        [
            ("display_files", False),
            ("html", "<p>Custom HTML content</p>"),
            ("position", 500),
        ],
    )
    def test_create_static_block_with_custom_field_values(self, field_name, custom_value):
        """Should allow setting custom values for optional fields."""
        kwargs = {"name": "Test Block", field_name: custom_value}
        static_block = StaticBlock.objects.create(**kwargs)

        assert getattr(static_block, field_name) == custom_value


@pytest.mark.django_db
class TestStaticBlockStringRepresentation:
    """Tests for StaticBlock __str__ method."""

    @pytest.mark.parametrize(
        "name,expected_str",
        [
            ("Product Description", "Product Description"),
            ("Footer Content", "Footer Content"),
            ("", ""),  # Blank names should work
            ("Very Long Block Name", "Very Long Block Name"),
        ],
    )
    def test_str_representation_returns_name(self, name, expected_str):
        """Should return the name as string representation."""
        static_block = StaticBlock.objects.create(name=name)
        assert str(static_block) == expected_str


@pytest.mark.django_db
class TestStaticBlockFieldValidation:
    """Tests for StaticBlock field validation and constraints."""

    def test_name_field_max_length_constraint(self):
        """Should enforce max_length=30 constraint on name field."""
        long_name = "x" * 31  # Exceeds 30 char limit
        static_block = StaticBlock(name=long_name)

        with pytest.raises(ValidationError):
            static_block.full_clean()

    def test_name_field_exactly_max_length_allowed(self):
        """Should allow name with exactly 30 characters."""
        exact_length_name = "x" * 30  # Exactly 30 chars
        static_block = StaticBlock.objects.create(name=exact_length_name)

        assert static_block.name == exact_length_name
        assert len(static_block.name) == 30

    def test_html_field_allows_blank_content(self):
        """Should allow blank HTML content."""
        static_block = StaticBlock.objects.create(name="Test", html="")
        assert static_block.html == ""

    def test_html_field_allows_long_content(self):
        """Should allow long HTML content (TextField has no length limit)."""
        long_html = "<p>" + "x" * 10000 + "</p>"
        static_block = StaticBlock.objects.create(name="Test", html=long_html)

        assert static_block.html == long_html


@pytest.mark.django_db
class TestStaticBlockOrdering:
    """Tests for StaticBlock default ordering by position."""

    def test_default_ordering_by_position(self):
        """Should order StaticBlocks by position field by default."""
        block_high = StaticBlock.objects.create(name="High", position=2000)
        block_low = StaticBlock.objects.create(name="Low", position=100)
        block_default = StaticBlock.objects.create(name="Default")  # position=1000

        blocks = list(StaticBlock.objects.all())
        positions = [block.position for block in blocks]

        assert positions == [100, 1000, 2000]
        assert blocks[0].name == "Low"
        assert blocks[1].name == "Default"
        assert blocks[2].name == "High"

    def test_ordering_with_same_position_values(self):
        """Should handle multiple blocks with same position consistently."""
        block1 = StaticBlock.objects.create(name="Block A", position=500)
        block2 = StaticBlock.objects.create(name="Block B", position=500)
        block3 = StaticBlock.objects.create(name="Block C", position=100)

        blocks = list(StaticBlock.objects.all())

        # First block should be the one with position 100
        assert blocks[0].position == 100
        assert blocks[0].name == "Block C"

        # Next two should both have position 500 (order may vary)
        assert blocks[1].position == 500
        assert blocks[2].position == 500


@pytest.mark.django_db
class TestStaticBlockFilesRelation:
    """Tests for StaticBlock files GenericRelation."""

    def test_files_generic_relation_exists(self):
        """Should have files attribute as GenericRelation."""
        static_block = StaticBlock.objects.create(name="Test Block")

        # Should be able to access files attribute
        assert hasattr(static_block, "files")

        # Should return a manager/queryset
        files_queryset = static_block.files.all()
        assert files_queryset.count() == 0  # No files initially

    def test_can_add_file_to_static_block(self):
        """Should be able to add File objects to StaticBlock through generic relation."""
        static_block = StaticBlock.objects.create(name="Test Block")

        # Create a file associated with the static block
        file_obj = File.objects.create(title="Test File", content=static_block)  # GenericForeignKey to static_block

        # Should be able to retrieve the file through the relation
        files = static_block.files.all()
        assert files.count() == 1
        assert files.first() == file_obj
        assert files.first().title == "Test File"

    def test_multiple_files_can_be_associated(self):
        """Should be able to associate multiple files with one StaticBlock."""
        static_block = StaticBlock.objects.create(name="Test Block")

        file1 = File.objects.create(title="File 1", content=static_block)
        file2 = File.objects.create(title="File 2", content=static_block)
        file3 = File.objects.create(title="File 3", content=static_block)

        files = static_block.files.all()
        assert files.count() == 3

        file_titles = [f.title for f in files]
        assert "File 1" in file_titles
        assert "File 2" in file_titles
        assert "File 3" in file_titles


@pytest.mark.django_db
class TestStaticBlockMetaConfiguration:
    """Tests for StaticBlock Meta class configuration."""

    def test_meta_ordering_configuration(self):
        """Should have correct ordering configuration in Meta class."""
        # Test that the ordering is indeed by position
        assert StaticBlock._meta.ordering == ("position",)

    def test_meta_app_label_configuration(self):
        """Should have correct app_label in Meta class."""
        assert StaticBlock._meta.app_label == "catalog"

    def test_model_verbose_name(self):
        """Should use model name as verbose name by default."""
        # Django uses the model name if verbose_name is not specified and lowercases it
        assert StaticBlock._meta.verbose_name == "static block"
