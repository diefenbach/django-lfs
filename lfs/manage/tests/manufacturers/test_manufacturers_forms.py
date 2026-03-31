from lfs.manufacturer.models import Manufacturer
from lfs.manage.manufacturers.forms import ManufacturerForm, ManufacturerAddForm


class TestManufacturerForm:
    """Test ManufacturerForm behavior."""

    def test_form_initialization_with_manufacturer(self, manufacturer):
        """Should initialize form with manufacturer data."""
        form = ManufacturerForm(instance=manufacturer)

        assert form.instance == manufacturer
        assert form.instance.name == manufacturer.name
        assert form.instance.slug == manufacturer.slug

    def test_valid_form_data(self):
        """Should accept valid form data."""
        data = {
            "name": "Test Manufacturer",
            "slug": "test-manufacturer",
            "short_description": "Short desc",
            "description": "A test manufacturer description",
        }

        form = ManufacturerForm(data=data)
        assert form.is_valid()

    def test_required_fields_validation(self):
        """Should require name and slug fields."""
        # Test missing name
        data = {"slug": "test-manufacturer", "description": "A test manufacturer"}
        form = ManufacturerForm(data=data)
        assert not form.is_valid()
        assert "name" in form.errors

        # Test missing slug
        data = {"name": "Test Manufacturer", "description": "A test manufacturer"}
        form = ManufacturerForm(data=data)
        assert not form.is_valid()
        assert "slug" in form.errors

    def test_slug_uniqueness_validation(self, manufacturer):
        """Should validate slug uniqueness."""
        data = {
            "name": "Another Manufacturer",
            "slug": manufacturer.slug,  # Same slug as existing manufacturer
            "description": "Another test manufacturer",
        }

        form = ManufacturerForm(data=data)
        assert not form.is_valid()
        assert "slug" in form.errors

    def test_name_max_length_validation(self):
        """Should validate name maximum length."""
        long_name = "A" * 101  # Assuming max_length is 100
        data = {
            "name": long_name,
            "slug": "test-manufacturer",
            "short_description": "Short",
            "description": "A test manufacturer",
        }

        form = ManufacturerForm(data=data)
        assert not form.is_valid()
        assert "name" in form.errors

    def test_slug_format_validation(self):
        """Should validate slug format."""
        # Django SlugField accepts various formats
        test_slugs = ["valid-slug", "slug-with-dashes", "slug_with_underscores", "slug123"]

        for test_slug in test_slugs:
            data = {
                "name": "Test Manufacturer",
                "slug": test_slug,
                "short_description": "Short",
                "description": "A test manufacturer",
            }

            form = ManufacturerForm(data=data)
            assert form.is_valid(), f"Slug '{test_slug}' should be valid"

    def test_valid_slug_formats(self):
        """Should accept valid slug formats."""
        valid_slugs = ["valid-slug", "another-valid-slug-123", "singleword", "with-numbers-123"]

        for valid_slug in valid_slugs:
            data = {
                "name": "Test Manufacturer",
                "slug": valid_slug,
                "short_description": "Short",
                "description": "A test manufacturer",
            }

            form = ManufacturerForm(data=data)
            assert form.is_valid(), f"Slug '{valid_slug}' should be valid"

    def test_form_save_creates_manufacturer(self, db):
        """Should create new manufacturer when saving form."""
        data = {
            "name": "New Test Manufacturer",
            "slug": "new-test-manufacturer",
            "short_description": "Short",
            "description": "A new test manufacturer",
        }

        form = ManufacturerForm(data=data)
        assert form.is_valid()

        manufacturer = form.save()
        assert manufacturer.name == "New Test Manufacturer"
        assert manufacturer.slug == "new-test-manufacturer"
        assert Manufacturer.objects.filter(slug="new-test-manufacturer").exists()

    def test_form_save_updates_existing_manufacturer(self, manufacturer):
        """Should update existing manufacturer when saving form."""
        data = {
            "name": "Updated Manufacturer",
            "slug": "updated-manufacturer",
            "short_description": "Short",
            "description": "Updated description",
        }

        form = ManufacturerForm(data=data, instance=manufacturer)
        assert form.is_valid()

        updated_manufacturer = form.save()
        assert updated_manufacturer == manufacturer
        assert updated_manufacturer.name == "Updated Manufacturer"
        assert updated_manufacturer.slug == "updated-manufacturer"

    def test_image_field_widget(self):
        """Should use LFSImageInput widget for image field."""
        form = ManufacturerForm()

        # Check that image field exists
        assert "image" in form.fields

        # Check that it uses the custom widget
        from lfs.core.widgets.image import LFSImageInput

        assert isinstance(form.fields["image"].widget, LFSImageInput)

    def test_form_fields_included(self):
        """Should include all expected fields."""
        form = ManufacturerForm()

        expected_fields = ["name", "slug", "short_description", "description", "image"]

        for field in expected_fields:
            assert field in form.fields, f"Field '{field}' should be in form"

    def test_empty_description_allowed(self, db):
        """Should allow empty description."""
        data = {
            "name": "Test Manufacturer",
            "slug": "test-manufacturer",
            "description": "",
        }

        form = ManufacturerForm(data=data)
        assert form.is_valid()

        manufacturer = form.save()
        assert manufacturer.description == ""


class TestManufacturerAddForm:
    """Test ManufacturerAddForm behavior."""

    def test_form_includes_required_fields(self):
        """Should include required fields for manufacturer creation."""
        form = ManufacturerAddForm()

        assert "name" in form.fields
        assert "slug" in form.fields

    def test_form_excludes_other_fields(self):
        """Should only include name and slug fields."""
        form = ManufacturerAddForm()

        # Should not include other fields
        excluded_fields = ["description", "short_description", "image", "meta_title"]
        for field in excluded_fields:
            assert field not in form.fields, f"Field '{field}' should not be in add form"

    def test_valid_form_data(self):
        """Should accept valid form data."""
        data = {
            "name": "New Manufacturer",
            "slug": "new-manufacturer",
        }

        form = ManufacturerAddForm(data=data)
        assert form.is_valid()

    def test_required_fields_validation(self):
        """Should require name and slug fields."""
        # Test missing name
        data = {"slug": "test-manufacturer"}
        form = ManufacturerAddForm(data=data)
        assert not form.is_valid()
        assert "name" in form.errors

        # Test missing slug
        data = {"name": "Test Manufacturer"}
        form = ManufacturerAddForm(data=data)
        assert not form.is_valid()
        assert "slug" in form.errors

    def test_slug_uniqueness_validation(self, manufacturer):
        """Should validate slug uniqueness."""
        data = {
            "name": "Another Manufacturer",
            "slug": manufacturer.slug,  # Same slug as existing manufacturer
        }

        form = ManufacturerAddForm(data=data)
        assert not form.is_valid()
        assert "slug" in form.errors

    def test_form_save_creates_manufacturer(self, db):
        """Should create new manufacturer when saving form."""
        data = {"name": "New Manufacturer", "slug": "new-manufacturer"}

        form = ManufacturerAddForm(data=data)
        assert form.is_valid()

        manufacturer = form.save()
        assert manufacturer.name == "New Manufacturer"
        assert manufacturer.slug == "new-manufacturer"
        assert Manufacturer.objects.filter(slug="new-manufacturer").exists()

    def test_form_meta_model(self):
        """Should use Manufacturer model."""
        form = ManufacturerAddForm()
        assert form._meta.model == Manufacturer

    def test_form_meta_fields(self):
        """Should have correct Meta fields configuration."""
        form = ManufacturerAddForm()
        assert form._meta.fields == ("name", "slug")

    def test_unicode_characters_in_name(self, db):
        """Should handle unicode characters in manufacturer name."""
        unicode_name = "Hersteller mit Umlauten äöü"
        data = {
            "name": unicode_name,
            "slug": "unicode-manufacturer",
        }

        form = ManufacturerAddForm(data=data)
        assert form.is_valid()

        manufacturer = form.save()
        assert manufacturer.name == unicode_name

    def test_slug_field_validation(self, db):
        """Should validate slug field properly."""
        # Django's SlugField preserves case by default
        # Test that it works as expected
        data = {
            "name": "Test Manufacturer",
            "slug": "SLUG_WITH_CAPS",
        }

        form = ManufacturerAddForm(data=data)
        assert form.is_valid()

        manufacturer = form.save()
        # Slug should preserve original case
        assert manufacturer.slug == "SLUG_WITH_CAPS"
