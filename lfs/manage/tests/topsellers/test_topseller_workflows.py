"""
Comprehensive integration workflow tests for topseller management.

Following TDD principles:
- Test complete user workflows and integration scenarios
- Test end-to-end functionality across multiple components
- Clear test names describing the workflow being tested
- Arrange-Act-Assert structure
- Test realistic user scenarios and business processes

Workflows covered:
- Complete topseller management workflows
- User interaction flows
- Data flow between components
- Integration with other modules
- Error recovery workflows
- Performance workflows
"""

import pytest
import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client

from lfs.catalog.models import Product, Category
from lfs.marketing.models import Topseller

User = get_user_model()


@pytest.fixture
def admin_user(db):
    """Admin user with proper permissions."""
    return User.objects.create_user(
        username="admin", email="admin@example.com", password="testpass123", is_staff=True, is_superuser=True
    )


@pytest.fixture
def regular_user(db):
    """Regular user without admin permissions."""
    return User.objects.create_user(username="user", email="user@example.com", password="testpass123")


@pytest.fixture
def client(admin_user):
    """Django test client with admin user."""
    client = Client()
    client.force_login(admin_user)
    return client


@pytest.fixture
def workflow_products(db):
    """Products for workflow testing."""
    products = []

    # Create products with different characteristics
    for i in range(10):
        product = Product.objects.create(
            name=f"Workflow Product {i+1}",
            sku=f"WF-{i+1:03d}",
            slug=f"workflow-product-{i+1}",
            price=10.00 + i,
            active=True,
        )
        products.append(product)

    return products


@pytest.fixture
def workflow_categories(db):
    """Categories for workflow testing."""
    categories = []

    # Create parent category
    parent = Category.objects.create(
        name="Workflow Parent Category",
        slug="workflow-parent-category",
    )
    categories.append(parent)

    # Create child categories
    for i in range(3):
        child = Category.objects.create(
            name=f"Workflow Child Category {i+1}",
            slug=f"workflow-child-category-{i+1}",
            parent=parent,
        )
        categories.append(child)

    return categories


class TestTopsellerManagementWorkflow:
    """Test complete topseller management workflow."""

    @pytest.mark.django_db
    def test_complete_topseller_management_workflow(self, client, workflow_products, workflow_categories):
        """Test complete topseller management workflow from start to finish."""
        # Step 1: Access topseller management page
        response = client.get("/manage/topseller")
        assert response.status_code == 200
        assert "topseller" in response.context

        # Step 2: Add products to categories for filtering
        workflow_products[0].categories.add(workflow_categories[0])
        workflow_products[1].categories.add(workflow_categories[1])
        workflow_products[2].categories.add(workflow_categories[2])

        # Step 3: Filter products by category
        response = client.get(f"/manage/topseller?topseller_category_filter={workflow_categories[0].id}")
        assert response.status_code == 200
        assert response.context["category_filter"] == str(workflow_categories[0].id)

        # Step 4: Add products to topseller
        response = client.post(
            "/manage/add-topseller",
            {
                f"product-{workflow_products[0].id}": str(workflow_products[0].id),
                f"product-{workflow_products[1].id}": str(workflow_products[1].id),
            },
        )
        assert response.status_code == 200

        # Verify topsellers were created
        assert Topseller.objects.count() == 2
        assert Topseller.objects.filter(product=workflow_products[0]).exists()
        assert Topseller.objects.filter(product=workflow_products[1]).exists()

        # Step 5: Sort topseller products
        topsellers = Topseller.objects.all()
        topseller_ids = [t.id for t in topsellers]
        response = client.post(
            "/manage/sort-topseller",
            data=json.dumps({"topseller_ids": list(reversed(topseller_ids))}),
            content_type="application/json",
        )
        assert response.status_code == 200

        # Verify positions were updated
        topsellers = Topseller.objects.all().order_by("position")
        assert topsellers[0].product == workflow_products[1]
        assert topsellers[1].product == workflow_products[0]

        # Step 6: Remove a topseller product
        response = client.post(
            "/manage/update-topseller",
            {
                "action": "remove",
                f"product-{topsellers[0].id}": str(topsellers[0].id),
            },
        )
        assert response.status_code == 200

        # Verify topseller was removed
        assert Topseller.objects.count() == 1
        assert not Topseller.objects.filter(id=topsellers[0].id).exists()

    @pytest.mark.django_db
    def test_topseller_management_with_pagination_workflow(self, client, workflow_products):
        """Test topseller management workflow with pagination."""
        # Step 1: Access page with small pagination
        response = client.get("/manage/topseller?topseller-amount=2")
        assert response.status_code == 200

        # Step 2: Navigate to second page
        response = client.get("/manage/topseller?page=2")
        assert response.status_code == 200

        # Step 3: Add products from different pages
        response = client.post(
            "/manage/add-topseller",
            {
                f"product-{workflow_products[0].id}": str(workflow_products[0].id),
                f"product-{workflow_products[5].id}": str(workflow_products[5].id),
            },
        )
        assert response.status_code == 200

        # Verify topsellers were created
        assert Topseller.objects.count() == 2

    @pytest.mark.django_db
    def test_topseller_management_with_filtering_workflow(self, client, workflow_products, workflow_categories):
        """Test topseller management workflow with filtering."""
        # Step 1: Add products to categories
        workflow_products[0].categories.add(workflow_categories[0])
        workflow_products[1].categories.add(workflow_categories[1])
        workflow_products[2].categories.add(workflow_categories[2])

        # Step 2: Filter by name
        response = client.get("/manage/topseller?filter=Product 1")
        assert response.status_code == 200
        assert response.context["filter"] == "Product 1"

        # Step 3: Filter by SKU
        response = client.get("/manage/topseller?filter=WF-002")
        assert response.status_code == 200
        assert response.context["filter"] == "WF-002"

        # Step 4: Filter by category
        response = client.get(f"/manage/topseller?topseller_category_filter={workflow_categories[0].id}")
        assert response.status_code == 200
        assert response.context["category_filter"] == str(workflow_categories[0].id)

        # Step 5: Add filtered product to topseller
        response = client.post(
            "/manage/add-topseller",
            {
                f"product-{workflow_products[0].id}": str(workflow_products[0].id),
            },
        )
        assert response.status_code == 200

        # Verify topseller was created
        assert Topseller.objects.count() == 1

    @pytest.mark.django_db
    def test_topseller_management_with_session_persistence_workflow(
        self, client, workflow_products, workflow_categories
    ):
        """Test topseller management workflow with session persistence."""
        # Step 1: Set filters and pagination
        response = client.get(
            "/manage/topseller?filter=Product&topseller_category_filter=All&page=1&topseller-amount=5"
        )
        assert response.status_code == 200

        # Step 2: Add products (should maintain filters)
        response = client.post(
            "/manage/add-topseller?keep-filters=1",
            {
                f"product-{workflow_products[0].id}": str(workflow_products[0].id),
            },
        )
        assert response.status_code == 200

        # Step 3: Verify filters are maintained
        response = client.get("/manage/topseller?keep-filters=1")
        assert response.status_code == 200
        assert response.context["filter"] == "Product"
        assert response.context["category_filter"] == "All"

    @pytest.mark.django_db
    def test_topseller_management_with_ajax_workflow(self, client, workflow_products):
        """Test topseller management workflow with AJAX requests."""
        with patch("lfs.manage.topseller.views.render_to_string", return_value="<div>mocked topseller content</div>"):
            # Step 1: Add products to topseller
            response = client.post(
                "/manage/add-topseller",
                {
                    f"product-{workflow_products[0].id}": str(workflow_products[0].id),
                    f"product-{workflow_products[1].id}": str(workflow_products[1].id),
                },
            )
            assert response.status_code == 200

            # Step 2: Get inline content via AJAX
            response = client.get("/manage/topseller-inline")
            assert response.status_code == 200
            assert response["Content-Type"] == "application/json"

            data = json.loads(response.content)
            assert "html" in data
            assert len(data["html"]) == 1
            assert data["html"][0][0] == "#topseller-inline"

            # Step 3: Sort via AJAX
            topsellers = Topseller.objects.all()
            topseller_ids = [t.id for t in topsellers]
            response = client.post(
                "/manage/sort-topseller",
                data=json.dumps({"topseller_ids": list(reversed(topseller_ids))}),
                content_type="application/json",
            )
            assert response.status_code == 200

            # Step 4: Verify sorting worked
            topsellers = Topseller.objects.all().order_by("position")
            assert topsellers[0].product == workflow_products[1]
            assert topsellers[1].product == workflow_products[0]


class TestTopsellerErrorRecoveryWorkflow:
    """Test topseller error recovery workflows."""

    @pytest.mark.django_db
    def test_topseller_management_error_recovery_workflow(self, client, workflow_products):
        """Test topseller management error recovery workflow."""
        # Step 1: Try to add non-existent product (should fail with 500 due to integrity error)
        response = client.post(
            "/manage/add-topseller",
            {
                "product-999": "999",
            },
        )
        assert response.status_code == 500  # Should fail due to invalid product ID

        # Step 2: Add valid product
        response = client.post(
            "/manage/add-topseller",
            {
                f"product-{workflow_products[0].id}": str(workflow_products[0].id),
            },
        )
        assert response.status_code == 200

        # Step 3: Try to remove non-existent topseller
        response = client.post(
            "/manage/update-topseller",
            {
                "action": "remove",
                "product-999": "999",
            },
        )
        assert response.status_code == 200  # Should not crash

        # Step 4: Remove valid topseller
        topseller = Topseller.objects.first()
        response = client.post(
            "/manage/update-topseller",
            {
                "action": "remove",
                f"product-{topseller.id}": str(topseller.id),
            },
        )
        assert response.status_code == 200

        # Verify topseller was removed
        assert Topseller.objects.count() == 0

    @pytest.mark.django_db
    def test_topseller_management_with_invalid_json_workflow(self, client, workflow_products):
        """Test topseller management with invalid JSON workflow."""
        # Step 1: Add products to topseller
        response = client.post(
            "/manage/add-topseller",
            {
                f"product-{workflow_products[0].id}": str(workflow_products[0].id),
            },
        )
        assert response.status_code == 200

        # Step 2: Try to sort with invalid JSON
        response = client.post("/manage/sort-topseller", data="invalid json", content_type="application/json")
        assert response.status_code == 200  # Should not crash

        # Step 3: Sort with valid JSON
        topseller = Topseller.objects.first()
        response = client.post(
            "/manage/sort-topseller",
            data=json.dumps({"topseller_ids": [topseller.id]}),
            content_type="application/json",
        )
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_topseller_management_with_permission_error_workflow(self, workflow_products):
        """Test topseller management with permission error workflow."""
        # Create regular user client
        regular_user = User.objects.create_user(username="regular", email="regular@example.com", password="testpass123")
        client = Client()
        client.force_login(regular_user)

        # Step 1: Try to access topseller management (should be denied)
        response = client.get("/manage/topseller")
        assert response.status_code == 403  # Permission denied

        # Step 2: Try to add topseller (should be denied)
        response = client.post(
            "/manage/add-topseller",
            {
                f"product-{workflow_products[0].id}": str(workflow_products[0].id),
            },
        )
        assert response.status_code == 403  # Permission denied

        # Step 3: Try to update topseller (should be denied)
        response = client.post(
            "/manage/update-topseller",
            {
                "action": "remove",
                "product-1": "1",
            },
        )
        assert response.status_code == 403  # Permission denied

        # Step 4: Try to sort topseller (should be denied)
        response = client.post(
            "/manage/sort-topseller", data=json.dumps({"topseller_ids": [1]}), content_type="application/json"
        )
        assert response.status_code == 403  # Permission denied


class TestTopsellerDataConsistencyWorkflow:
    """Test topseller data consistency workflows."""

    @pytest.mark.django_db
    def test_topseller_data_consistency_workflow(self, client, workflow_products):
        """Test topseller data consistency workflow."""
        # Step 1: Add products to topseller
        response = client.post(
            "/manage/add-topseller",
            {
                f"product-{workflow_products[0].id}": str(workflow_products[0].id),
                f"product-{workflow_products[1].id}": str(workflow_products[1].id),
                f"product-{workflow_products[2].id}": str(workflow_products[2].id),
            },
        )
        assert response.status_code == 200

        # Step 2: Verify positions are consistent
        topsellers = Topseller.objects.all().order_by("position")
        assert topsellers[0].position == 10
        assert topsellers[1].position == 20
        assert topsellers[2].position == 30

        # Step 3: Sort topseller products
        topseller_ids = [t.id for t in topsellers]
        response = client.post(
            "/manage/sort-topseller",
            data=json.dumps({"topseller_ids": list(reversed(topseller_ids))}),
            content_type="application/json",
        )
        assert response.status_code == 200

        # Step 4: Verify positions are still consistent
        topsellers = Topseller.objects.all().order_by("position")
        assert topsellers[0].position == 10
        assert topsellers[1].position == 20
        assert topsellers[2].position == 30

        # Step 5: Remove middle topseller
        response = client.post(
            "/manage/update-topseller",
            {
                "action": "remove",
                f"product-{topsellers[1].id}": str(topsellers[1].id),
            },
        )
        assert response.status_code == 200

        # Step 6: Verify remaining positions are consistent
        topsellers = Topseller.objects.all().order_by("position")
        assert topsellers[0].position == 10
        assert topsellers[1].position == 20

    @pytest.mark.django_db
    def test_topseller_duplicate_prevention_workflow(self, client, workflow_products):
        """Test topseller duplicate prevention workflow."""
        # Step 1: Add product to topseller
        response = client.post(
            "/manage/add-topseller",
            {
                f"product-{workflow_products[0].id}": str(workflow_products[0].id),
            },
        )
        assert response.status_code == 200

        # Step 2: Try to add same product again
        response = client.post(
            "/manage/add-topseller",
            {
                f"product-{workflow_products[0].id}": str(workflow_products[0].id),
            },
        )
        assert response.status_code == 200

        # Step 3: Verify only one topseller exists
        assert Topseller.objects.count() == 1
        assert Topseller.objects.filter(product=workflow_products[0]).count() == 1

    @pytest.mark.django_db
    def test_topseller_product_deletion_workflow(self, client, workflow_products):
        """Test topseller product deletion workflow."""
        # Step 1: Add product to topseller
        response = client.post(
            "/manage/add-topseller",
            {
                f"product-{workflow_products[0].id}": str(workflow_products[0].id),
            },
        )
        assert response.status_code == 200

        # Step 2: Delete the product
        workflow_products[0].delete()

        # Step 3: Try to manage topsellers (should handle deleted product gracefully)
        response = client.get("/manage/topseller")
        assert response.status_code == 200

        # Step 4: Try to remove topseller with deleted product
        topseller = Topseller.objects.first()
        response = client.post(
            "/manage/update-topseller",
            {
                "action": "remove",
                f"product-{topseller.id}": str(topseller.id),
            },
        )
        assert response.status_code == 200


class TestTopsellerPerformanceWorkflow:
    """Test topseller performance workflows."""

    @pytest.mark.django_db
    def test_topseller_management_with_large_dataset_workflow(self, client):
        """Test topseller management with large dataset workflow."""
        # Step 1: Create many products
        products = []
        for i in range(100):
            product = Product.objects.create(
                name=f"Performance Product {i}",
                sku=f"PERF-{i:03d}",
                slug=f"performance-product-{i}",
                price=10.00 + i,
                active=True,
            )
            products.append(product)

        # Step 2: Access topseller management page
        response = client.get("/manage/topseller")
        assert response.status_code == 200

        # Step 3: Filter products
        response = client.get("/manage/topseller?filter=Performance")
        assert response.status_code == 200

        # Step 4: Add multiple products to topseller
        response = client.post(
            "/manage/add-topseller",
            {
                f"product-{products[0].id}": str(products[0].id),
                f"product-{products[1].id}": str(products[1].id),
                f"product-{products[2].id}": str(products[2].id),
            },
        )
        assert response.status_code == 200

        # Step 5: Sort topseller products
        topsellers = Topseller.objects.all()
        topseller_ids = [t.id for t in topsellers]
        response = client.post(
            "/manage/sort-topseller",
            data=json.dumps({"topseller_ids": list(reversed(topseller_ids))}),
            content_type="application/json",
        )
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_topseller_management_with_deep_category_hierarchy_workflow(self, client, workflow_products):
        """Test topseller management with deep category hierarchy workflow."""
        # Step 1: Create deep category hierarchy
        parent = Category.objects.create(
            name="Deep Parent",
            slug="deep-parent",
        )

        current = parent
        for i in range(5):  # Create 5 levels
            child = Category.objects.create(
                name=f"Deep Level {i+1}",
                slug=f"deep-level-{i+1}",
                parent=current,
            )
            current = child

        # Step 2: Add products to deep categories
        workflow_products[0].categories.add(parent)
        workflow_products[1].categories.add(current)

        # Step 3: Filter by parent category (should include children)
        response = client.get(f"/manage/topseller?topseller_category_filter={parent.id}")
        assert response.status_code == 200

        # Step 4: Add products to topseller
        response = client.post(
            "/manage/add-topseller",
            {
                f"product-{workflow_products[0].id}": str(workflow_products[0].id),
                f"product-{workflow_products[1].id}": str(workflow_products[1].id),
            },
        )
        assert response.status_code == 200

        # Verify topsellers were created
        assert Topseller.objects.count() == 2


class TestTopsellerIntegrationWorkflow:
    """Test topseller integration workflows."""

    @pytest.mark.django_db
    def test_topseller_integration_with_signals_workflow(self, client, workflow_products):
        """Test topseller integration with signals workflow."""
        # Step 1: Add product to topseller
        response = client.post(
            "/manage/add-topseller",
            {
                f"product-{workflow_products[0].id}": str(workflow_products[0].id),
            },
        )
        assert response.status_code == 200

        # Step 2: Remove topseller (should send signal)
        topseller = Topseller.objects.first()
        with patch("lfs.core.signals.topseller_changed.send") as mock_send:
            response = client.post(
                "/manage/update-topseller",
                {
                    "action": "remove",
                    f"product-{topseller.id}": str(topseller.id),
                },
            )
            assert response.status_code == 200
            mock_send.assert_called_once()

    @pytest.mark.django_db
    def test_topseller_integration_with_template_workflow(self, client, workflow_products):
        """Test topseller integration with template workflow."""
        with patch("lfs.manage.topseller.views.render_to_string", return_value="<div>mocked template content</div>"):
            # Step 1: Access main template
            response = client.get("/manage/topseller")
            assert response.status_code == 200
            # Note: Can't check template names when mocking render_to_string

            # Step 2: Add products to topseller
            response = client.post(
                "/manage/add-topseller",
                {
                    f"product-{workflow_products[0].id}": str(workflow_products[0].id),
                },
            )
            assert response.status_code == 200

            # Step 3: Access inline template
            response = client.get("/manage/topseller-inline")
            assert response.status_code == 200
            assert response["Content-Type"] == "application/json"

    @pytest.mark.django_db
    def test_topseller_integration_with_session_workflow(self, client, workflow_products, workflow_categories):
        """Test topseller integration with session workflow."""
        # Step 1: Set session data
        response = client.get("/manage/topseller?filter=test&topseller_category_filter=All&page=2&topseller-amount=10")
        assert response.status_code == 200

        # Step 2: Add products (should maintain session)
        response = client.post(
            "/manage/add-topseller?keep-filters=1",
            {
                f"product-{workflow_products[0].id}": str(workflow_products[0].id),
            },
        )
        assert response.status_code == 200

        # Step 3: Verify session is maintained
        response = client.get("/manage/topseller?keep-filters=1")
        assert response.status_code == 200
        assert response.context["filter"] == "test"
        assert response.context["category_filter"] == "All"
        assert response.context["amount_options"][2]["selected"] is True  # 10 is selected
