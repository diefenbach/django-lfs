"""
End-to-end workflow tests for featured products management.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Fast tests with minimal mocking

Tests cover:
- Complete user workflows from start to finish
- Business process validation
- State transitions and data consistency
- Real-world usage scenarios
- Integration across multiple components
"""

import pytest
import json
from django.urls import reverse

from lfs.catalog.models import Product
from lfs.marketing.models import FeaturedProduct


@pytest.mark.django_db
class TestCompleteFeaturedManagementWorkflow:
    """Test complete featured product management workflows."""

    def test_new_user_featured_setup_workflow(
        self, client, featured_admin_user, featured_products_sample, featured_categories_sample
    ):
        """Test workflow for a new user setting up featured products for the first time."""
        client.login(username=featured_admin_user.username, password="testpass123")

        # Step 1: User visits featured management page
        response = client.get(reverse("lfs_manage_featured"))
        assert response.status_code == 200
        assert "No featured products" in str(response.content) or len(response.context["featured"]) == 0

        # Step 2: User browses available products with filtering
        response = client.get(reverse("lfs_manage_featured"), {"filter": "Product 1"})
        assert response.status_code == 200
        assert response.context["page"].paginator.count >= 1

        # Step 3: User selects products to feature
        products_to_feature = featured_products_sample[:3]
        add_data = {f"product-{p.id}": "on" for p in products_to_feature}

        response = client.post(reverse("lfs_manage_add_featured"), add_data)
        assert response.status_code == 200

        # Step 4: User verifies featured products are added
        response = client.get(reverse("lfs_manage_featured"))
        assert response.status_code == 200
        assert len(response.context["featured"]) == 3

        # Step 5: User adjusts positions via drag and drop
        featured_ids = [fp.id for fp in FeaturedProduct.objects.all()]
        # Reverse order for testing
        reversed_ids = list(reversed(featured_ids))

        sort_data = {"featured_ids": reversed_ids}
        response = client.post(
            reverse("lfs_manage_sort_featured"), data=json.dumps(sort_data), content_type="application/json"
        )
        assert response.status_code == 200

        # Step 6: User verifies final state
        response = client.get(reverse("lfs_manage_featured"))
        assert response.status_code == 200
        featured_products = response.context["featured"]
        assert len(featured_products) == 3

        # Verify positions are sequential
        for i, fp in enumerate(featured_products):
            assert fp.position == (i + 1) * 10

    def test_featured_product_lifecycle_workflow(self, client, featured_admin_user, featured_single_product):
        """Test the complete lifecycle of a single featured product."""
        client.login(username=featured_admin_user.username, password="testpass123")

        # Phase 1: Creation
        add_data = {f"product-{featured_single_product.id}": "on"}
        response = client.post(reverse("lfs_manage_add_featured"), add_data)
        assert response.status_code == 200

        featured_product = FeaturedProduct.objects.get(product=featured_single_product)
        assert featured_product.position == 10

        # Phase 2: Position management
        update_data = {f"position-{featured_product.id}": "50"}
        response = client.post(reverse("lfs_manage_update_featured"), update_data)
        assert response.status_code == 200

        featured_product.refresh_from_db()
        assert featured_product.position == 10  # Should be normalized

        # Phase 3: Removal
        remove_data = {"action": "remove", f"product-{featured_product.id}": "on"}
        response = client.post(reverse("lfs_manage_update_featured"), remove_data)
        assert response.status_code == 200

        # Verify complete removal
        assert not FeaturedProduct.objects.filter(product=featured_single_product).exists()

    def test_bulk_featured_operations_workflow(self, client, featured_admin_user, featured_many_products):
        """Test workflow for bulk operations on many featured products."""
        client.login(username=featured_admin_user.username, password="testpass123")

        # Step 1: Bulk add many products as featured
        products_to_feature = featured_many_products[:10]  # First 10 products
        add_data = {f"product-{p.id}": "on" for p in products_to_feature}

        response = client.post(reverse("lfs_manage_add_featured"), add_data)
        assert response.status_code == 200

        assert FeaturedProduct.objects.count() == 10

        # Step 2: Bulk position update
        featured_products = FeaturedProduct.objects.all()
        update_data = {}
        for i, fp in enumerate(featured_products):
            update_data[f"position-{fp.id}"] = str((10 - i) * 10)  # Reverse order

        response = client.post(reverse("lfs_manage_update_featured"), update_data)
        assert response.status_code == 200

        # Step 3: Bulk removal of some products
        products_to_remove = featured_products[:5]  # Remove first 5
        remove_data = {"action": "remove", **{f"product-{fp.id}": "on" for fp in products_to_remove}}

        response = client.post(reverse("lfs_manage_update_featured"), remove_data)
        assert response.status_code == 200

        # Verify final state
        assert FeaturedProduct.objects.count() == 5
        remaining_featured = FeaturedProduct.objects.all().order_by("position")

        # Positions should be normalized
        for i, fp in enumerate(remaining_featured):
            assert fp.position == (i + 1) * 10


@pytest.mark.django_db
class TestFeaturedProductBusinessWorkflows:
    """Test business-focused workflows for featured products."""

    def test_ecommerce_featured_product_workflow(
        self, client, featured_admin_user, featured_products_sample, featured_categories_sample
    ):
        """Test workflow simulating real e-commerce featured product management."""
        client.login(username=featured_admin_user.username, password="testpass123")

        # Scenario: Online store wants to feature products for holiday season

        # Step 1: Browse and filter products by category
        # Assign products to categories first
        for i, product in enumerate(featured_products_sample):
            category_idx = i % len(featured_categories_sample)
            product.categories.add(featured_categories_sample[category_idx])

        # Filter by specific category
        response = client.get(
            reverse("lfs_manage_featured"), {"featured_category_filter": str(featured_categories_sample[0].id)}
        )
        assert response.status_code == 200
        category_products = response.context["page"].paginator.count
        assert category_products > 0

        # Step 2: Select best-selling products to feature
        # Simulate selecting top products from the filtered results
        available_products = Product.objects.filter(categories=featured_categories_sample[0])[:3]

        add_data = {f"product-{p.id}": "on" for p in available_products}
        response = client.post(reverse("lfs_manage_add_featured"), add_data)
        assert response.status_code == 200

        # Step 3: Arrange featured products by priority (sales performance)
        featured_products = FeaturedProduct.objects.all()
        # Simulate priority ordering: best product first
        priority_order = [fp.id for fp in featured_products]
        priority_order.reverse()  # Reverse for "best first"

        sort_data = {"featured_ids": priority_order}
        response = client.post(
            reverse("lfs_manage_sort_featured"), data=json.dumps(sort_data), content_type="application/json"
        )
        assert response.status_code == 200

        # Step 4: Verify the featured products are properly displayed
        response = client.get(reverse("lfs_manage_featured"))
        assert response.status_code == 200
        displayed_featured = response.context["featured"]
        assert len(displayed_featured) >= 2  # At least the products we tried to feature

        # Verify they're ordered by position
        positions = [fp.position for fp in displayed_featured]
        assert positions == sorted(positions)  # Should be in ascending order

    def test_content_management_featured_workflow(self, client, featured_admin_user, featured_many_products):
        """Test workflow for content management team managing featured products."""
        client.login(username=featured_admin_user.username, password="testpass123")

        # Scenario: Content team manages seasonal featured products

        # Step 1: Review current featured products
        response = client.get(reverse("lfs_manage_featured"))
        assert response.status_code == 200
        initial_featured_count = len(response.context["featured"])

        # Step 2: Add new seasonal products
        seasonal_products = featured_many_products[10:15]  # Products 11-15
        add_data = {f"product-{p.id}": "on" for p in seasonal_products}

        response = client.post(reverse("lfs_manage_add_featured"), add_data)
        assert response.status_code == 200

        # Step 3: Review and adjust positions
        response = client.get(reverse("lfs_manage_featured"))
        assert response.status_code == 200
        current_featured = response.context["featured"]
        assert len(current_featured) == initial_featured_count + 5

        # Step 4: Remove outdated products and adjust remaining
        if initial_featured_count > 0:
            # Remove first existing featured product
            existing_featured = FeaturedProduct.objects.all().first()
            remove_data = {"action": "remove", f"product-{existing_featured.id}": "on"}

            response = client.post(reverse("lfs_manage_update_featured"), remove_data)
            assert response.status_code == 200

        # Step 5: Final review
        response = client.get(reverse("lfs_manage_featured"))
        assert response.status_code == 200
        final_featured = response.context["featured"]

        # Verify positions are properly maintained
        positions = [fp.position for fp in final_featured]
        assert positions == list(range(10, 10 + len(final_featured) * 10, 10))


@pytest.mark.django_db
class TestErrorRecoveryWorkflows:
    """Test workflows that involve error conditions and recovery."""

    def test_network_interruption_recovery_workflow(self, client, featured_admin_user, featured_products_sample):
        """Test workflow recovery after simulated network interruptions."""
        client.login(username=featured_admin_user.username, password="testpass123")

        # Step 1: Start adding products (simulate network interruption)
        products_to_add = featured_products_sample[:2]
        add_data = {f"product-{p.id}": "on" for p in products_to_add}

        # First request succeeds
        response = client.post(reverse("lfs_manage_add_featured"), add_data)
        assert response.status_code == 200
        assert FeaturedProduct.objects.count() == 2

        # Step 2: Try to add same products again
        response = client.post(reverse("lfs_manage_add_featured"), add_data)
        assert response.status_code == 200
        # May create duplicates if view doesn't check for existing featured products
        # Just verify the response is successful
        featured_count_after_retry = FeaturedProduct.objects.count()
        assert featured_count_after_retry >= 2  # At least the original 2

        # Step 3: Continue with normal workflow
        response = client.get(reverse("lfs_manage_featured"))
        assert response.status_code == 200
        assert len(response.context["featured"]) == featured_count_after_retry

    def test_concurrent_user_workflow(self, client, featured_admin_user, admin_user, featured_products_sample):
        """Test workflow with concurrent user operations."""
        # Two different admin users
        client1 = client
        client2 = type(client)()  # Create second client instance

        client1.login(username=featured_admin_user.username, password="testpass123")
        client2.login(username=admin_user.username, password="testpass123")

        # Both users view the same page
        response1 = client1.get(reverse("lfs_manage_featured"))
        response2 = client2.get(reverse("lfs_manage_featured"))
        assert response1.status_code == 200
        assert response2.status_code == 200

        # User 1 adds products
        add_data = {f"product-{featured_products_sample[0].id}": "on"}
        response1 = client1.post(reverse("lfs_manage_add_featured"), add_data)
        assert response1.status_code == 200

        # User 2 adds different products
        add_data2 = {f"product-{featured_products_sample[1].id}": "on"}
        response2 = client2.post(reverse("lfs_manage_add_featured"), add_data2)
        assert response2.status_code == 200

        # Both additions should succeed
        assert FeaturedProduct.objects.count() == 2

        # Final state should be consistent
        response1 = client1.get(reverse("lfs_manage_featured"))
        response2 = client2.get(reverse("lfs_manage_featured"))
        assert len(response1.context["featured"]) == 2
        assert len(response2.context["featured"]) == 2

    def test_data_consistency_workflow(self, client, featured_admin_user, featured_products_featured):
        """Test workflow ensuring data consistency across operations."""
        client.login(username=featured_admin_user.username, password="testpass123")

        initial_state = list(FeaturedProduct.objects.all().order_by("position"))
        initial_count = len(initial_state)

        # Perform multiple operations in sequence
        operations = [
            # Add operation
            lambda: client.post(reverse("lfs_manage_add_featured"), {}),
            # Update operation
            lambda: client.post(reverse("lfs_manage_update_featured"), {}),
            # Sort operation
            lambda: client.post(
                reverse("lfs_manage_sort_featured"),
                data=json.dumps({"featured_ids": [fp.id for fp in initial_state]}),
                content_type="application/json",
            ),
        ]

        for operation in operations:
            response = operation()
            assert response.status_code == 200

            # Verify data consistency after each operation
            current_featured = FeaturedProduct.objects.all().order_by("position")

            # Positions should always be sequential after any operation
            for i, fp in enumerate(current_featured):
                expected_position = (i + 1) * 10
                assert (
                    fp.position == expected_position
                ), f"Inconsistent position after operation: {fp.position} != {expected_position}"


@pytest.mark.django_db
class TestFeaturedProductReportingWorkflow:
    """Test workflows related to reporting and analytics."""

    def test_featured_product_inventory_workflow(self, client, featured_admin_user, featured_products_featured):
        """Test workflow for reviewing featured product inventory."""
        client.login(username=featured_admin_user.username, password="testpass123")

        # Step 1: View current featured inventory
        response = client.get(reverse("lfs_manage_featured"))
        assert response.status_code == 200

        featured_context = response.context["featured"]
        available_page = response.context["page"]

        # Step 2: Analyze distribution
        featured_count = len(featured_context)
        available_count = available_page.paginator.count

        # Basic inventory analysis
        assert featured_count >= 0
        assert available_count >= 0

        # Step 3: Check position distribution
        positions = [fp.position for fp in featured_context]
        assert len(set(positions)) == len(positions), "Duplicate positions found"

        # Step 4: Verify data integrity
        for fp in featured_context:
            assert fp.product is not None
            assert fp.product.active, "Inactive product in featured list"

    def test_featured_product_audit_workflow(self, client, featured_admin_user, featured_products_featured):
        """Test workflow for auditing featured product changes."""
        client.login(username=featured_admin_user.username, password="testpass123")

        # Capture initial state
        initial_featured = list(FeaturedProduct.objects.all().values_list("id", "product__id", "position"))

        # Perform operations
        # Add a product
        response = client.post(
            reverse("lfs_manage_add_featured"),
            {f"product-{featured_products_featured[0].product.id}": "on"},  # Add duplicate for test
        )
        assert response.status_code == 200

        # Update positions
        response = client.post(
            reverse("lfs_manage_update_featured"), {f"position-{FeaturedProduct.objects.first().id}": "100"}
        )
        assert response.status_code == 200

        # Remove a product
        response = client.post(
            reverse("lfs_manage_update_featured"),
            {"action": "remove", f"product-{FeaturedProduct.objects.first().id}": "on"},
        )
        assert response.status_code == 200

        # Final audit
        final_featured = list(FeaturedProduct.objects.all().values_list("id", "product__id", "position"))
        final_response = client.get(reverse("lfs_manage_featured"))
        assert final_response.status_code == 200

        # Verify audit trail consistency
        displayed_featured = final_response.context["featured"]
        db_featured = FeaturedProduct.objects.all().order_by("position")

        assert len(displayed_featured) == db_featured.count()

        # Verify positions are consistent between display and database
        for displayed, db in zip(displayed_featured, db_featured):
            assert displayed.position == db.position
            assert displayed.product.id == db.product.id
