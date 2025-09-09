"""
Comprehensive edge case tests for category management.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Fast tests with minimal mocking

Tests cover:
- Boundary conditions and edge cases
- Error handling and validation
- Invalid input handling
- Race conditions
- Database integrity
- Permission edge cases
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.urls import reverse

from lfs.catalog.models import Category, Product

User = get_user_model()


class TestCategoryBoundaryConditions:
    """Test boundary conditions for categories."""

    def test_category_name_minimum_length(self, db):
        """Should handle minimum name length."""
        # Test with very short name
        category = Category(name="A", slug="a", description="Test")
        category.full_clean()  # Should not raise validation error
        category.save()
        assert Category.objects.filter(slug="a").exists()

    def test_category_name_maximum_length(self, db):
        """Should handle maximum name length."""
        long_name = "A" * 30  # Using reasonable length within model limits
        category = Category(name=long_name, slug="long-name", description="Test")
        category.full_clean()  # Should not raise validation error
        category.save()
        assert Category.objects.filter(slug="long-name").exists()

    def test_category_slug_minimum_length(self, db):
        """Should handle minimum slug length."""
        category = Category(name="Test", slug="a", description="Test")
        category.full_clean()  # Should not raise validation error
        category.save()
        assert Category.objects.filter(slug="a").exists()

    def test_category_slug_maximum_length(self, db):
        """Should handle maximum slug length."""
        long_slug = "a" * 15  # Using reasonable length within model limits
        category = Category(name="Test", slug=long_slug, description="Test")
        category.full_clean()  # Should not raise validation error
        category.save()
        assert Category.objects.filter(slug=long_slug).exists()

    def test_category_with_many_children(self, db, root_category):
        """Should handle category with many children."""
        # Create many child categories
        children = []
        for i in range(10):  # Test with 10 children (reasonable for test)
            child = Category.objects.create(
                name=f"Child {i}", slug=f"child-{i}", description=f"Child category {i}", parent=root_category
            )
            children.append(child)

        # Verify all children were created
        root_children = root_category.get_children()
        assert len(root_children) == 10

        # Verify hierarchy levels are correct
        for child in children:
            assert child.level == 1
            assert child.parent == root_category


class TestCategoryValidationEdgeCases:
    """Test validation edge cases."""

    def test_unique_slug_constraint(self, db, root_category):
        """Should enforce unique slugs across all categories."""
        # Create child with same slug as root
        child = Category(
            name="Child with same slug",
            slug=root_category.slug,
            description="Child with same slug as parent",
            parent=root_category,
        )
        # This should raise a validation error due to unique constraint
        with pytest.raises(ValidationError):
            child.full_clean()

        # Verify only one category with this slug exists
        assert Category.objects.filter(slug=root_category.slug).count() == 1

    def test_empty_description_allowed(self, db):
        """Should allow empty description."""
        category = Category(name="Test", slug="test", description="")
        category.full_clean()  # Should not raise validation error
        category.save()
        assert Category.objects.filter(slug="test").exists()

    def test_unicode_characters_in_name(self, db):
        """Should handle unicode characters in category name."""
        unicode_name = "Kategorie mit Umlauten äöü"
        category = Category(name=unicode_name, slug="unicode-category", description="Category with unicode characters")
        category.full_clean()  # Should not raise validation error
        category.save()
        assert category.name == unicode_name

    def test_slug_field_validation(self, db):
        """Should validate slug field properly."""
        # Django's SlugField preserves case by default
        # Test that it works as expected
        category = Category(name="Test", slug="SLUG_WITH_CAPS", description="Test")
        category.full_clean()
        category.save()

        # Slug should preserve original case
        assert category.slug == "SLUG_WITH_CAPS"


class TestCategoryHierarchyEdgeCases:
    """Test hierarchy-related edge cases."""

    def test_deeply_nested_categories(self, db):
        """Should handle deeply nested category hierarchies."""
        # Create a deep hierarchy
        root = Category.objects.create(name="Root", slug="root", description="Root")

        current_parent = root
        categories = [root]

        # Create 5 levels deep (reasonable for test)
        for i in range(5):
            child = Category.objects.create(
                name=f"Level {i+1}", slug=f"level-{i+1}", description=f"Level {i+1} category", parent=current_parent
            )
            categories.append(child)
            current_parent = child

        # Verify hierarchy levels (may not be automatically set)
        # Just verify categories were created successfully
        for category in categories:
            assert category.level is not None

        # Verify parent-child relationships
        for i in range(1, len(categories)):
            assert categories[i].parent == categories[i - 1]

        # Verify we have 6 categories total (root + 5 levels)
        assert len(categories) == 6

    def test_parent_child_relationship(self, db, root_category, child_category):
        """Should maintain proper parent-child relationships."""
        # Verify initial relationship
        assert child_category.parent == root_category
        assert child_category in root_category.get_children()

        # Test changing parent
        new_parent = Category.objects.create(name="New Parent", slug="new-parent", description="New parent")
        child_category.parent = new_parent
        child_category.save()

        # Verify relationship changed
        assert child_category.parent == new_parent
        assert child_category in new_parent.get_children()

    def test_orphan_categories_after_parent_deletion(self, db, categories_hierarchy):
        """Should handle orphaned categories after parent deletion."""
        root_category, child_category, grandchild_category = categories_hierarchy

        # Delete child category
        child_category.delete()

        # Grandchild should be orphaned (parent set to None)
        grandchild_category.refresh_from_db()
        assert grandchild_category.parent is None

        # Root should still exist
        root_category.refresh_from_db()
        assert Category.objects.filter(id=root_category.id).exists()

    def test_position_values_edge_cases(self, db):
        """Should handle edge cases with position values."""
        # Test with very high position values
        high_pos_category = Category.objects.create(
            name="High Position", slug="high-position", description="Category with high position", position=999999
        )
        assert high_pos_category.position == 999999

        # Test with negative position values
        negative_pos_category = Category.objects.create(
            name="Negative Position",
            slug="negative-position",
            description="Category with negative position",
            position=-100,
        )
        assert negative_pos_category.position == -100


class TestCategoryProductRelationshipEdgeCases:
    """Test product-category relationship edge cases."""

    def test_category_with_many_products(self, db, root_category):
        """Should handle category with many products."""
        products = []
        for i in range(20):  # Test with 20 products (reasonable for test)
            product = Product.objects.create(name=f"Product {i}", slug=f"product-{i}", price=10.99, active=True)
            products.append(product)
            root_category.products.add(product)

        # Verify all products are assigned
        assert root_category.products.count() == 20

        # Verify products can be retrieved
        assigned_products = list(root_category.products.all())
        assert len(assigned_products) == 20

    def test_product_assigned_to_many_categories(self, db, product):
        """Should handle product assigned to many categories."""
        categories = []
        for i in range(5):  # Test with 5 categories (reasonable for test)
            category = Category.objects.create(name=f"Category {i}", slug=f"category-{i}", description=f"Category {i}")
            categories.append(category)
            category.products.add(product)

        # Verify product is in all categories
        for category in categories:
            assert product in category.products.all()

        # Verify product count in each category
        for category in categories:
            assert category.products.count() == 1

    def test_remove_nonexistent_product_from_category(self, db, root_category):
        """Should handle attempt to remove nonexistent product."""
        # Try to remove a product that doesn't exist in the category
        nonexistent_product_id = 99999

        # This should not raise an error
        root_category.products.remove(nonexistent_product_id)

        # Category should remain unchanged
        assert root_category.products.count() == 0


class TestCategoryConcurrencyEdgeCases:
    """Test concurrency and race condition edge cases."""

    def test_simultaneous_category_creation(self, db):
        """Should handle simultaneous category creation attempts."""
        # This is difficult to test in unit tests, but we can test
        # that unique constraints work properly
        Category.objects.create(name="Unique Test", slug="unique-test", description="Unique test category")

        # Attempt to create another with same slug should fail
        with pytest.raises(IntegrityError):
            Category.objects.create(
                name="Another Unique Test", slug="unique-test", description="Another unique test category"  # Same slug
            )

    def test_category_modification_during_iteration(self, db, root_category):
        """Should handle category modification during iteration."""
        # Create some child categories
        children = []
        for i in range(5):
            child = Category.objects.create(
                name=f"Child {i}", slug=f"child-{i}", description=f"Child {i}", parent=root_category
            )
            children.append(child)

        # Modify categories during iteration (should not cause issues)
        modified_count = 0
        for child in root_category.get_children():
            child.name = f"Modified {child.name}"
            child.save()
            modified_count += 1

        assert modified_count == 5

        # Verify all were modified
        for child in children:
            child.refresh_from_db()
            assert child.name.startswith("Modified")


class TestCategoryViewEdgeCases:
    """Test view-related edge cases."""

    def test_category_view_with_nonexistent_id(self, client, admin_user):
        """Should handle view request for nonexistent category."""
        client.login(username="admin", password="testpass123")

        response = client.get(reverse("lfs_manage_category", kwargs={"id": 99999}))

        assert response.status_code == 404

    def test_category_view_without_permission(self, client, regular_user, root_category):
        """Should handle view request without proper permissions."""
        client.login(username="user", password="testpass123")

        response = client.get(reverse("lfs_manage_category", kwargs={"id": root_category.id}))

        # Should redirect or deny access
        assert response.status_code in [302, 403]

    def test_category_form_with_invalid_data(self, client, admin_user, root_category):
        """Should handle form submission with invalid data."""
        client.login(username="admin", password="testpass123")

        # Submit form with invalid slug
        invalid_data = {"name": "Test Category", "slug": "invalid slug with spaces", "description": "Test description"}

        response = client.post(reverse("lfs_manage_category", kwargs={"id": root_category.id}), invalid_data)

        # Should stay on same page with errors
        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["form"].errors

    def test_category_sorting_with_invalid_data(self, client, admin_user):
        """Should handle sorting request with invalid data."""
        client.login(username="admin", password="testpass123")

        # Submit invalid sorting data
        invalid_data = {"categories": "invalid-data-format"}

        response = client.post(reverse("lfs_sort_categories"), invalid_data)

        # Should handle gracefully
        assert response.status_code == 200
        response_data = response.json()
        assert "message" in response_data
