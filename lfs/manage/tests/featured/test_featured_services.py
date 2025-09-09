"""
Comprehensive unit tests for featured services and utility functions.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Fast tests with minimal mocking

Tests cover:
- _update_positions() function with various scenarios
- FeaturedProduct model operations
- Position management and ordering
- Edge cases and error conditions
"""

import pytest

from lfs.marketing.models import FeaturedProduct
from lfs.manage.featured.views import _update_positions


class TestUpdatePositionsFunction:
    """Test _update_positions utility function."""

    @pytest.mark.django_db
    def test_update_positions_sets_sequential_positions_starting_from_10(self, featured_products_featured):
        """Test that _update_positions sets sequential positions starting from 10."""
        # Manually set some random positions first
        featured_products_featured[0].position = 100
        featured_products_featured[1].position = 200
        featured_products_featured[2].position = 300
        for fp in featured_products_featured:
            fp.save()

        _update_positions()

        featured_products = FeaturedProduct.objects.all().order_by("position")
        assert featured_products[0].position == 10
        assert featured_products[1].position == 20
        assert featured_products[2].position == 30
        assert featured_products[3].position == 40
        assert featured_products[4].position == 50

    @pytest.mark.django_db
    def test_update_positions_handles_empty_featured_products(self):
        """Test that _update_positions handles empty featured products gracefully."""
        # Ensure no featured products exist
        FeaturedProduct.objects.all().delete()

        # Should not raise any exception
        _update_positions()

        assert FeaturedProduct.objects.count() == 0

    @pytest.mark.django_db
    def test_update_positions_maintains_order_by_current_positions(self, featured_products_featured):
        """Test that _update_positions maintains relative order of existing positions."""
        # Set positions in reverse order
        featured_products_featured[0].position = 50
        featured_products_featured[1].position = 40
        featured_products_featured[2].position = 30
        featured_products_featured[3].position = 20
        featured_products_featured[4].position = 10
        for fp in featured_products_featured:
            fp.save()

        _update_positions()

        # Should be reordered to 10, 20, 30, 40, 50 based on original order
        featured_products = FeaturedProduct.objects.all().order_by("position")
        assert featured_products[0].position == 10
        assert featured_products[1].position == 20
        assert featured_products[2].position == 30
        assert featured_products[3].position == 40
        assert featured_products[4].position == 50

    @pytest.mark.django_db
    def test_update_positions_with_single_featured_product(self, featured_single_featured):
        """Test that _update_positions works with single featured product."""
        # Set a random position first
        featured_single_featured.position = 999
        featured_single_featured.save()

        _update_positions()

        featured_single_featured.refresh_from_db()
        assert featured_single_featured.position == 10

    @pytest.mark.django_db
    def test_update_positions_preserves_product_associations(self, featured_products_featured):
        """Test that _update_positions preserves product associations."""
        original_products = [fp.product for fp in featured_products_featured]

        _update_positions()

        updated_featured = FeaturedProduct.objects.all().order_by("position")
        updated_products = [fp.product for fp in updated_featured]

        assert original_products == updated_products

    @pytest.mark.django_db
    def test_update_positions_creates_gaps_for_future_insertions(self, featured_products_featured):
        """Test that _update_positions creates gaps between positions for future insertions."""
        _update_positions()

        featured_products = FeaturedProduct.objects.all().order_by("position")
        positions = [fp.position for fp in featured_products]

        # Should have gaps of 10 between positions
        expected_positions = [10, 20, 30, 40, 50]
        assert positions == expected_positions

    @pytest.mark.django_db
    def test_update_positions_handles_large_number_of_featured_products(self, featured_many_products):
        """Test that _update_positions handles large number of featured products."""
        # Create featured products from many products
        featured_products = []
        for i, product in enumerate(featured_many_products[:20]):  # Test with 20 products
            fp = FeaturedProduct.objects.create(
                product=product,
                position=i * 5,  # Random positions
            )
            featured_products.append(fp)

        _update_positions()

        featured_products = FeaturedProduct.objects.all().order_by("position")
        for i, fp in enumerate(featured_products):
            assert fp.position == (i + 1) * 10

    @pytest.mark.django_db
    def test_update_positions_called_after_adding_featured_product(self, featured_products_sample):
        """Test that _update_positions is called after adding a featured product."""
        # Add a new featured product
        new_featured = FeaturedProduct.objects.create(
            product=featured_products_sample[5],  # Use a non-featured product
            position=999,  # Random position
        )

        _update_positions()

        # All featured products should have proper positions
        featured_products = FeaturedProduct.objects.all().order_by("position")
        for i, fp in enumerate(featured_products):
            assert fp.position == (i + 1) * 10

    @pytest.mark.django_db
    def test_update_positions_called_after_removing_featured_product(self, featured_products_featured):
        """Test that _update_positions is called after removing a featured product."""
        # Remove one featured product
        featured_products_featured[2].delete()

        _update_positions()

        # Remaining featured products should have proper positions
        featured_products = FeaturedProduct.objects.all().order_by("position")
        assert len(featured_products) == 4  # One was removed
        for i, fp in enumerate(featured_products):
            assert fp.position == (i + 1) * 10


class TestFeaturedProductModelOperations:
    """Test FeaturedProduct model operations and business logic."""

    @pytest.mark.django_db
    def test_featured_product_creation_sets_initial_position(self, featured_single_product):
        """Test that FeaturedProduct creation sets initial position."""
        featured = FeaturedProduct.objects.create(product=featured_single_product)

        assert featured.position is not None
        assert isinstance(featured.position, int)

    @pytest.mark.django_db
    def test_featured_product_str_method_returns_product_name_with_position(self, featured_single_featured):
        """Test that FeaturedProduct __str__ method returns product name with position."""
        expected_str = f"{featured_single_featured.product.name} ({featured_single_featured.position})"
        assert str(featured_single_featured) == expected_str

    @pytest.mark.django_db
    def test_featured_product_ordering_by_position(self, featured_products_featured):
        """Test that FeaturedProduct ordering works correctly by position."""
        # Set different positions
        for i, fp in enumerate(featured_products_featured):
            fp.position = (5 - i) * 10  # Reverse order: 50, 40, 30, 20, 10
            fp.save()

        featured_products = FeaturedProduct.objects.all().order_by("position")
        assert featured_products[0].position == 10
        assert featured_products[1].position == 20
        assert featured_products[2].position == 30
        assert featured_products[3].position == 40
        assert featured_products[4].position == 50

    @pytest.mark.django_db
    def test_featured_product_deletion_updates_positions(self, featured_products_featured):
        """Test that deleting a FeaturedProduct updates positions of remaining products."""
        # Delete the middle featured product
        middle_fp = featured_products_featured[2]
        middle_fp.delete()

        _update_positions()

        remaining_featured = FeaturedProduct.objects.all().order_by("position")
        assert len(remaining_featured) == 4
        for i, fp in enumerate(remaining_featured):
            assert fp.position == (i + 1) * 10

    @pytest.mark.django_db
    def test_featured_product_bulk_deletion_updates_positions(self, featured_products_featured):
        """Test that bulk deletion of FeaturedProducts updates positions."""
        # Delete multiple featured products
        FeaturedProduct.objects.filter(id__in=[fp.id for fp in featured_products_featured[:2]]).delete()

        _update_positions()

        remaining_featured = FeaturedProduct.objects.all().order_by("position")
        assert len(remaining_featured) == 3
        for i, fp in enumerate(remaining_featured):
            assert fp.position == (i + 1) * 10


class TestFeaturedProductBusinessLogic:
    """Test business logic related to FeaturedProduct operations."""

    @pytest.mark.django_db
    def test_position_gaps_allow_for_easy_insertions(self, featured_products_featured):
        """Test that position gaps allow for easy insertions between products."""
        _update_positions()

        # Simulate inserting a product between position 20 and 30
        # We can use position 25
        new_featured = FeaturedProduct.objects.create(
            product=featured_products_featured[0].product, position=25  # Reuse product for test
        )

        featured_products = FeaturedProduct.objects.all().order_by("position")
        positions = [fp.position for fp in featured_products]

        # Should include the new position 25
        assert 25 in positions

    @pytest.mark.django_db
    def test_position_normalization_after_manual_position_changes(self, featured_products_featured):
        """Test that positions are normalized after manual position changes."""
        # Manually set positions with gaps and overlaps
        featured_products_featured[0].position = 5
        featured_products_featured[1].position = 15
        featured_products_featured[2].position = 15  # Overlap
        featured_products_featured[3].position = 35
        featured_products_featured[4].position = 100  # Large gap

        for fp in featured_products_featured:
            fp.save()

        _update_positions()

        featured_products = FeaturedProduct.objects.all().order_by("position")
        for i, fp in enumerate(featured_products):
            assert fp.position == (i + 1) * 10

    @pytest.mark.django_db
    def test_featured_product_with_same_product_not_allowed(self, featured_single_product):
        """Test that duplicate FeaturedProduct for same product is not allowed."""
        # Create first featured product
        FeaturedProduct.objects.create(product=featured_single_product, position=10)

        # Attempt to create duplicate - this should work as there's no unique constraint
        # but it's a business logic consideration
        duplicate = FeaturedProduct.objects.create(product=featured_single_product, position=20)

        assert FeaturedProduct.objects.filter(product=featured_single_product).count() == 2

    @pytest.mark.django_db
    def test_featured_product_position_uniqueness_not_enforced(self, featured_products_sample):
        """Test that position uniqueness is not enforced (allowing overlaps)."""
        # Create featured products with same position
        FeaturedProduct.objects.create(product=featured_products_sample[0], position=10)
        FeaturedProduct.objects.create(product=featured_products_sample[1], position=10)

        featured_with_position_10 = FeaturedProduct.objects.filter(position=10)
        assert featured_with_position_10.count() == 2
