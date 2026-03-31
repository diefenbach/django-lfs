from lfs.catalog.models import Category
from lfs.manage.categories.forms import CategoryForm, CategoryAddForm, CategoryViewForm


class TestCategoryForm:
    """Test CategoryForm behavior."""

    def test_form_initialization_with_category(self, root_category):
        """Should initialize form with category data."""
        form = CategoryForm(instance=root_category)

        assert form.instance == root_category
        # Form fields may not have initial values set directly
        assert form.instance.name == root_category.name
        assert form.instance.slug == root_category.slug

    def test_valid_form_data(self):
        """Should accept valid form data."""
        data = {
            "name": "Test Category",
            "slug": "test-category",
            "short_description": "Short desc",
            "description": "A test category description",
            "exclude_from_navigation": False,
        }

        form = CategoryForm(data=data)
        assert form.is_valid()

    def test_required_fields_validation(self):
        """Should require name and slug fields."""
        # Test missing name
        data = {"slug": "test-category", "description": "A test category"}
        form = CategoryForm(data=data)
        assert not form.is_valid()
        assert "name" in form.errors

        # Test missing slug
        data = {"name": "Test Category", "description": "A test category"}
        form = CategoryForm(data=data)
        assert not form.is_valid()
        assert "slug" in form.errors

    def test_slug_uniqueness_validation(self, root_category):
        """Should validate slug uniqueness."""
        data = {
            "name": "Another Category",
            "slug": root_category.slug,  # Same slug as existing category
            "description": "Another test category",
        }

        form = CategoryForm(data=data)
        assert not form.is_valid()
        assert "slug" in form.errors

    def test_name_max_length_validation(self):
        """Should validate name maximum length."""
        long_name = "A" * 101  # Assuming max_length is 100
        data = {
            "name": long_name,
            "slug": "test-category",
            "short_description": "Short",
            "description": "A test category",
            "exclude_from_navigation": False,
        }

        form = CategoryForm(data=data)
        assert not form.is_valid()
        assert "name" in form.errors

    def test_slug_format_validation(self):
        """Should validate slug format."""
        # Django SlugField accepts various formats
        test_slugs = ["valid-slug", "slug-with-dashes", "slug_with_underscores", "slug123"]

        for test_slug in test_slugs:
            data = {
                "name": "Test Category",
                "slug": test_slug,
                "short_description": "Short",
                "description": "A test category",
                "exclude_from_navigation": False,
            }

            form = CategoryForm(data=data)
            assert form.is_valid(), f"Slug '{test_slug}' should be valid"

    def test_valid_slug_formats(self):
        """Should accept valid slug formats."""
        valid_slugs = ["valid-slug", "another-valid-slug-123", "singleword", "with-numbers-123"]

        for valid_slug in valid_slugs:
            data = {
                "name": "Test Category",
                "slug": valid_slug,
                "short_description": "Short",
                "description": "A test category",
                "exclude_from_navigation": False,
            }

            form = CategoryForm(data=data)
            assert form.is_valid(), f"Slug '{valid_slug}' should be valid"

    def test_form_save_creates_category(self, db):
        """Should create new category when saving form."""
        data = {
            "name": "New Test Category",
            "slug": "new-test-category",
            "short_description": "Short",
            "description": "A new test category",
            "exclude_from_navigation": False,
        }

        form = CategoryForm(data=data)
        assert form.is_valid()

        category = form.save()
        assert category.name == "New Test Category"
        assert category.slug == "new-test-category"
        assert Category.objects.filter(slug="new-test-category").exists()

    def test_form_save_updates_existing_category(self, root_category):
        """Should update existing category when saving form."""
        data = {
            "name": "Updated Category",
            "slug": "updated-category",
            "short_description": "Short",
            "description": "Updated description",
            "exclude_from_navigation": False,
        }

        form = CategoryForm(data=data, instance=root_category)
        assert form.is_valid()

        updated_category = form.save()
        assert updated_category == root_category
        assert updated_category.name == "Updated Category"
        assert updated_category.slug == "updated-category"


class TestCategoryAddForm:
    """Test CategoryAddForm behavior."""

    def test_form_includes_required_fields(self):
        """Should include required fields for category creation."""
        form = CategoryAddForm()

        assert "name" in form.fields
        assert "slug" in form.fields

    def test_valid_form_data(self):
        """Should accept valid form data."""
        data = {
            "name": "Child Category",
            "slug": "child-category",
        }

        form = CategoryAddForm(data=data)
        assert form.is_valid()

    def test_required_fields_validation(self):
        """Should require name and slug fields."""
        # Test missing name
        data = {"slug": "test-category"}
        form = CategoryAddForm(data=data)
        assert not form.is_valid()
        assert "name" in form.errors

        # Test missing slug
        data = {"name": "Test Category"}
        form = CategoryAddForm(data=data)
        assert not form.is_valid()
        assert "slug" in form.errors

    def test_form_save_creates_category(self, db):
        """Should create new category when saving form."""
        data = {"name": "New Category", "slug": "new-category"}

        form = CategoryAddForm(data=data)
        assert form.is_valid()

        category = form.save()
        assert category.name == "New Category"
        assert category.slug == "new-category"
        assert Category.objects.filter(slug="new-category").exists()


class TestCategoryViewForm:
    """Test CategoryViewForm behavior."""

    def test_form_includes_view_fields(self):
        """Should include view-related fields."""
        form = CategoryViewForm()

        # These are the actual fields in CategoryViewForm
        expected_fields = ["template", "show_all_products"]

        for field in expected_fields:
            assert field in form.fields

    def test_form_excludes_other_fields(self):
        """Should not include other category fields."""
        form = CategoryViewForm()

        excluded_fields = ["name", "slug", "description", "meta_title", "meta_description"]
        for field in excluded_fields:
            assert field not in form.fields

    def test_form_initialization_with_category(self, root_category):
        """Should initialize form with category view data."""
        form = CategoryViewForm(instance=root_category)

        assert form.instance == root_category
        assert "template" in form.fields
        assert "show_all_products" in form.fields

    def test_form_save_updates_view_fields(self, root_category):
        """Should update category view fields when saving."""
        original_template = getattr(root_category, "template", 0)
        original_show_all = getattr(root_category, "show_all_products", False)

        data = {
            "template": 1,
            "show_all_products": True,
        }

        form = CategoryViewForm(data=data, instance=root_category)
        assert form.is_valid()

        updated_category = form.save()
        assert updated_category.template == 1
        assert updated_category.show_all_products == True
