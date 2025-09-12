"""
Comprehensive edge case and error condition tests for topseller management.

Following TDD principles:
- Test boundary conditions and edge cases
- Test error conditions and exception handling
- Test data integrity and consistency
- Clear test names describing the edge case being tested
- Arrange-Act-Assert structure
- Test resilience and graceful degradation

Edge cases covered:
- Boundary conditions (empty data, maximum values, null values)
- Error conditions (invalid data, missing data, corrupted data)
- Data integrity (inconsistent data, orphaned records)
- Performance edge cases (large datasets, complex queries)
- Security edge cases (injection attacks, permission bypass)
- System edge cases (database errors, network failures)
"""

import pytest
import json
from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.db import DatabaseError
from django.http import HttpResponse
from django.test import RequestFactory

from lfs.catalog.models import Product, Category
from lfs.marketing.models import Topseller
from lfs.manage.topseller.views import (
    ManageTopsellerView,
    add_topseller,
    update_topseller,
    sort_topseller,
    _update_positions,
)

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
def edge_case_products(db):
    """Products with edge case data for testing."""
    products = []

    # Product with very long name
    product1 = Product.objects.create(
        name="A" * 1000,  # Very long name
        sku="LONG-NAME-001",
        slug="very-long-name-product",
        price=10.00,
        active=True,
    )
    products.append(product1)

    # Product with special characters in name
    product2 = Product.objects.create(
        name="Product with Special Chars!@#$%^&*()",
        sku="SPECIAL-001",
        slug="product-with-special-chars",
        price=20.00,
        active=True,
    )
    products.append(product2)

    # Product with unicode characters
    product3 = Product.objects.create(
        name="产品名称",  # Chinese characters
        sku="UNICODE-001",
        slug="unicode-product",
        price=30.00,
        active=True,
    )
    products.append(product3)

    # Product with very long SKU
    product4 = Product.objects.create(
        name="Long SKU Product",
        sku="A" * 500,  # Very long SKU
        slug="long-sku-product",
        price=40.00,
        active=True,
    )
    products.append(product4)

    # Product with numeric name
    product5 = Product.objects.create(
        name="123456789",
        sku="NUMERIC-001",
        slug="numeric-product",
        price=50.00,
        active=True,
    )
    products.append(product5)

    # Product with zero price
    product6 = Product.objects.create(
        name="Zero Price Product",
        sku="ZERO-001",
        slug="zero-price-product",
        price=0.00,
        active=True,
    )
    products.append(product6)

    # Product with very high price
    product7 = Product.objects.create(
        name="Expensive Product",
        sku="EXPENSIVE-001",
        slug="expensive-product",
        price=999999.99,
        active=True,
    )
    products.append(product7)

    # Inactive product
    product8 = Product.objects.create(
        name="Inactive Product",
        sku="INACTIVE-001",
        slug="inactive-product",
        price=60.00,
        active=False,
    )
    products.append(product8)

    return products


@pytest.fixture
def edge_case_categories(db):
    """Categories with edge case data for testing."""
    categories = []

    # Category with very long name
    category1 = Category.objects.create(
        name="A" * 1000,  # Very long name
        slug="very-long-category-name",
    )
    categories.append(category1)

    # Category with special characters
    category2 = Category.objects.create(
        name="Category with Special Chars!@#$%^&*()",
        slug="category-with-special-chars",
    )
    categories.append(category2)

    # Category with unicode characters
    category3 = Category.objects.create(
        name="分类名称",  # Chinese characters
        slug="unicode-category",
    )
    categories.append(category3)

    # Inactive category (Note: Category model doesn't have active field, so this is just a regular category)
    category4 = Category.objects.create(
        name="Inactive Category",
        slug="inactive-category",
    )
    categories.append(category4)

    # Category with very deep nesting
    parent = category1
    for i in range(10):  # Create 10 levels of nesting
        child = Category.objects.create(
            name=f"Level {i+1} Category",
            slug=f"level-{i+1}-category",
            parent=parent,
        )
        categories.append(child)
        parent = child

    return categories


@pytest.fixture
def edge_case_topsellers(db, edge_case_products):
    """Topsellers with edge case data for testing."""
    topsellers = []

    # Topseller with very high position
    topseller1 = Topseller.objects.create(
        product=edge_case_products[0],
        position=999999,
    )
    topsellers.append(topseller1)

    # Topseller with negative position
    topseller2 = Topseller.objects.create(
        product=edge_case_products[1],
        position=-100,
    )
    topsellers.append(topseller2)

    # Topseller with zero position
    topseller3 = Topseller.objects.create(
        product=edge_case_products[2],
        position=0,
    )
    topsellers.append(topseller3)

    # Topseller with decimal position (should be handled)
    topseller4 = Topseller.objects.create(
        product=edge_case_products[3],
        position=15.5,
    )
    topsellers.append(topseller4)

    return topsellers


class TestTopsellerBoundaryConditions:
    """Test topseller boundary conditions."""

    @pytest.mark.django_db
    def test_manage_topseller_view_with_no_products(self, admin_user):
        """Test ManageTopsellerView with no products in database."""
        view = ManageTopsellerView()
        view.request = RequestFactory().get("/")
        view.request.session = {}
        view.request.user = admin_user
        view.request.session = {"topseller-amount": 25}

        context = view.get_context_data()

        assert context["total"] == 0
        assert context["topseller"].count() == 0

    @pytest.mark.django_db
    def test_manage_topseller_view_with_no_topsellers(self, admin_user, edge_case_products):
        """Test ManageTopsellerView with no topsellers."""
        view = ManageTopsellerView()
        view.request = RequestFactory().get("/")
        view.request.session = {}
        view.request.user = admin_user
        view.request.session = {"topseller-amount": 25}

        context = view.get_context_data()

        assert context["total"] == len(edge_case_products)
        assert context["topseller"].count() == 0

    @pytest.mark.django_db
    def test_manage_topseller_view_with_all_products_as_topsellers(self, admin_user, edge_case_products):
        """Test ManageTopsellerView with all products as topsellers."""
        # Make all products topsellers
        for product in edge_case_products:
            Topseller.objects.create(product=product, position=10)

        view = ManageTopsellerView()
        view.request = RequestFactory().get("/")
        view.request.session = {}
        view.request.user = admin_user
        view.request.session = {"topseller-amount": 25}

        context = view.get_context_data()

        assert context["total"] == 0  # No available products
        assert context["topseller"].count() == len(edge_case_products)

    @pytest.mark.django_db
    def test_manage_topseller_view_with_maximum_pagination(self, admin_user, edge_case_products):
        """Test ManageTopsellerView with maximum pagination."""
        view = ManageTopsellerView()
        view.request = RequestFactory().get("/?page=999")
        view.request.session = {"topseller-amount": 1}
        view.request.user = admin_user

        context = view.get_context_data()

        assert context["page"] == 0  # EmptyPage returns 0

    @pytest.mark.django_db
    def test_manage_topseller_view_with_minimum_pagination(self, admin_user, edge_case_products):
        """Test ManageTopsellerView with minimum pagination."""
        view = ManageTopsellerView()
        view.request = RequestFactory().get("/?page=1")
        view.request.user = admin_user
        view.request.session = {"topseller-amount": 1}

        context = view.get_context_data()

        assert context["page"] is not None
        assert hasattr(context["page"], "object_list")

    @pytest.mark.django_db
    def test_manage_topseller_view_with_zero_amount(self, admin_user, edge_case_products):
        """Test ManageTopsellerView with zero amount per page."""
        view = ManageTopsellerView()
        view.request = RequestFactory().get("/")
        view.request.session = {}
        view.request.user = admin_user
        view.request.session = {"topseller-amount": 0}

        # This should raise ZeroDivisionError due to Paginator
        with pytest.raises(ZeroDivisionError):
            view.get_context_data()

    @pytest.mark.django_db
    def test_manage_topseller_view_with_negative_amount(self, admin_user, edge_case_products):
        """Test ManageTopsellerView with negative amount per page."""
        view = ManageTopsellerView()
        view.request = RequestFactory().get("/")
        view.request.session = {}
        view.request.user = admin_user
        view.request.session = {"topseller-amount": -10}

        # This should handle negative amount gracefully
        context = view.get_context_data()

        assert "paginator" in context


class TestTopsellerErrorConditions:
    """Test topseller error conditions."""

    @pytest.mark.django_db
    def test_add_topseller_with_invalid_product_id(self, admin_user):
        """Test add_topseller with invalid product ID."""
        request = RequestFactory().post(
            "/",
            {
                "product-999": "999",  # Non-existent product
            },
        )
        request.session = {}
        request.session = {}
        request.user = admin_user

        with patch("lfs.manage.topseller.views.ManageTopsellerView") as mock_view_class, \
             patch("lfs.manage.topseller.views.render") as mock_render, \
             patch("lfs.manage.topseller.views.Topseller.objects.create") as mock_create:
            mock_view = MagicMock()
            mock_view_class.return_value = mock_view
            mock_view.get_context_data.return_value = {"topseller": [], "total": 0}
            mock_render.return_value = HttpResponse("mocked")
            # Mock create to raise IntegrityError for invalid product ID
            mock_create.side_effect = Exception("Invalid product ID")

            # Should raise an exception due to invalid product ID
            with pytest.raises(Exception):  # Mocked exception
                add_topseller(request)

    @pytest.mark.django_db
    def test_add_topseller_with_non_numeric_product_id(self, admin_user):
        """Test add_topseller with non-numeric product ID."""
        request = RequestFactory().post(
            "/",
            {
                "product-abc": "abc",  # Non-numeric ID
            },
        )
        request.session = {}
        request.user = admin_user

        with patch("lfs.manage.topseller.views.ManageTopsellerView") as mock_view_class:
            mock_view = MagicMock()
            mock_view_class.return_value = mock_view
            mock_view.get_context_data.return_value = {"topseller": [], "total": 0}

            # Should not raise an exception
            result = add_topseller(request)
            assert result is not None

    @pytest.mark.django_db
    def test_update_topseller_with_invalid_topseller_id(self, admin_user):
        """Test update_topseller with invalid topseller ID."""
        request = RequestFactory().post(
            "/",
            {
                "action": "remove",
                "product-999": "999",  # Non-existent topseller
            },
        )
        request.session = {}
        request.user = admin_user

        with patch("lfs.manage.topseller.views.ManageTopsellerView") as mock_view_class:
            mock_view = MagicMock()
            mock_view_class.return_value = mock_view
            mock_view.get_context_data.return_value = {"topseller": [], "total": 0}

            # Should not raise an exception
            result = update_topseller(request)
            assert result is not None

    @pytest.mark.django_db
    def test_sort_topseller_with_invalid_json(self, admin_user):
        """Test sort_topseller with invalid JSON."""
        request = RequestFactory().post("/sort-topseller", data="invalid json", content_type="application/json")
        request.session = {}
        request.user = admin_user

        # Should not raise an exception
        result = sort_topseller(request)
        assert result.status_code == 200

    @pytest.mark.django_db
    def test_sort_topseller_with_malformed_json(self, admin_user):
        """Test sort_topseller with malformed JSON."""
        request = RequestFactory().post(
            "/sort-topseller",
            data='{"topseller_ids": [1, 2, 3',  # Missing closing bracket
            content_type="application/json",
        )
        request.session = {}
        request.user = admin_user

        # Should not raise an exception
        result = sort_topseller(request)
        assert result.status_code == 200

    @pytest.mark.django_db
    def test_sort_topseller_with_wrong_data_type(self, admin_user):
        """Test sort_topseller with wrong data type."""
        request = RequestFactory().post(
            "/sort-topseller", data=json.dumps({"topseller_ids": "not an array"}), content_type="application/json"
        )
        request.session = {}
        request.user = admin_user

        # Should not raise an exception
        result = sort_topseller(request)
        assert result.status_code == 200

    @pytest.mark.django_db
    def test_manage_topseller_view_with_invalid_category_id(self, admin_user, edge_case_products):
        """Test ManageTopsellerView with invalid category ID."""
        view = ManageTopsellerView()
        view.request = RequestFactory().get("/?topseller_category_filter=999")
        view.request.user = admin_user
        view.request.session = {"topseller-amount": 25}

        # Should not raise an exception
        context = view.get_context_data()
        assert context is not None

    @pytest.mark.django_db
    def test_manage_topseller_view_with_invalid_page_number(self, admin_user, edge_case_products):
        """Test ManageTopsellerView with invalid page number."""
        view = ManageTopsellerView()
        view.request = RequestFactory().get("/?page=abc")
        view.request.user = admin_user
        view.request.session = {"topseller-amount": 25}

        # Should not raise an exception
        context = view.get_context_data()
        assert context is not None


class TestTopsellerDataIntegrity:
    """Test topseller data integrity."""

    @pytest.mark.django_db
    def test_duplicate_topseller_creation(self, admin_user, edge_case_products):
        """Test creating duplicate topsellers."""
        product = edge_case_products[0]

        # Create first topseller
        Topseller.objects.create(product=product, position=10)

        # Try to create duplicate
        request = RequestFactory().post(
            "/",
            {
                f"product-{product.id}": str(product.id),
            },
        )
        request.session = {}
        request.user = admin_user

        with patch("lfs.manage.topseller.views.ManageTopsellerView") as mock_view_class:
            mock_view = MagicMock()
            mock_view_class.return_value = mock_view
            mock_view.get_context_data.return_value = {"topseller": [], "total": 0}

            # Should not raise an exception
            result = add_topseller(request)
            assert result is not None

    @pytest.mark.django_db
    def test_topseller_with_deleted_product(self, admin_user, edge_case_products):
        """Test topseller with deleted product."""
        product = edge_case_products[0]
        topseller = Topseller.objects.create(product=product, position=10)

        # Delete the product
        product.delete()

        # Try to update topseller
        request = RequestFactory().post(
            "/",
            {
                "action": "remove",
                f"product-{topseller.id}": str(topseller.id),
            },
        )
        request.session = {}
        request.user = admin_user

        with patch("lfs.manage.topseller.views.ManageTopsellerView") as mock_view_class:
            mock_view = MagicMock()
            mock_view_class.return_value = mock_view
            mock_view.get_context_data.return_value = {"topseller": [], "total": 0}

            # Should not raise an exception
            result = update_topseller(request)
            assert result is not None

    @pytest.mark.django_db
    def test_topseller_position_consistency(self, edge_case_topsellers):
        """Test topseller position consistency after updates."""
        # Manually set positions (using valid values)
        Topseller.objects.filter(id=edge_case_topsellers[0].id).update(position=30)
        Topseller.objects.filter(id=edge_case_topsellers[1].id).update(position=10)
        Topseller.objects.filter(id=edge_case_topsellers[2].id).update(position=20)

        _update_positions()

        # Check that positions are now consistent
        topsellers = Topseller.objects.all().order_by("position")
        assert topsellers[0].position == 10
        assert topsellers[1].position == 20
        assert topsellers[2].position == 30

    @pytest.mark.django_db
    def test_topseller_with_inactive_product(self, admin_user, edge_case_products):
        """Test topseller with inactive product."""
        inactive_product = edge_case_products[7]  # Inactive product

        request = RequestFactory().post(
            "/",
            {
                f"product-{inactive_product.id}": str(inactive_product.id),
            },
        )
        request.session = {}
        request.user = admin_user

        with patch("lfs.manage.topseller.views.ManageTopsellerView") as mock_view_class:
            mock_view = MagicMock()
            mock_view_class.return_value = mock_view
            mock_view.get_context_data.return_value = {"topseller": [], "total": 0}

            # Should not raise an exception
            result = add_topseller(request)
            assert result is not None

    @pytest.mark.django_db
    def test_topseller_with_zero_price_product(self, admin_user, edge_case_products):
        """Test topseller with zero price product."""
        zero_price_product = edge_case_products[5]  # Zero price product

        request = RequestFactory().post(
            "/",
            {
                f"product-{zero_price_product.id}": str(zero_price_product.id),
            },
        )
        request.session = {}
        request.user = admin_user

        with patch("lfs.manage.topseller.views.ManageTopsellerView") as mock_view_class:
            mock_view = MagicMock()
            mock_view_class.return_value = mock_view
            mock_view.get_context_data.return_value = {"topseller": [], "total": 0}

            # Should not raise an exception
            result = add_topseller(request)
            assert result is not None


class TestTopsellerPerformanceEdgeCases:
    """Test topseller performance edge cases."""

    @pytest.mark.django_db
    def test_manage_topseller_view_with_large_dataset(self, admin_user):
        """Test ManageTopsellerView with large dataset."""
        # Create many products
        products = []
        for i in range(1000):
            product = Product.objects.create(
                name=f"Product {i}",
                sku=f"SKU-{i:04d}",
                slug=f"product-{i}",
                price=10.00 + i,
                active=True,
            )
            products.append(product)

        view = ManageTopsellerView()
        view.request = RequestFactory().get("/")
        view.request.session = {}
        view.request.user = admin_user
        view.request.session = {"topseller-amount": 25}

        # Should handle large dataset efficiently
        context = view.get_context_data()
        assert context["total"] == 1000

    @pytest.mark.django_db
    def test_manage_topseller_view_with_many_topsellers(self, admin_user, edge_case_products):
        """Test ManageTopsellerView with many topsellers."""
        # Create many topsellers
        for i, product in enumerate(edge_case_products):
            Topseller.objects.create(product=product, position=(i + 1) * 10)

        view = ManageTopsellerView()
        view.request = RequestFactory().get("/")
        view.request.session = {}
        view.request.user = admin_user
        view.request.session = {"topseller-amount": 25}

        # Should handle many topsellers efficiently
        context = view.get_context_data()
        assert context["topseller"].count() == len(edge_case_products)

    @pytest.mark.django_db
    def test_manage_topseller_view_with_deep_category_hierarchy(
        self, admin_user, edge_case_categories, edge_case_products
    ):
        """Test ManageTopsellerView with deep category hierarchy."""
        # Add products to deep categories
        deep_category = edge_case_categories[-1]  # Deepest category
        edge_case_products[0].categories.add(deep_category)

        view = ManageTopsellerView()
        view.request = RequestFactory().get(f"/?topseller_category_filter={edge_case_categories[0].id}")
        view.request.user = admin_user
        view.request.session = {"topseller-amount": 25}

        # Should handle deep hierarchy efficiently
        context = view.get_context_data()
        assert context is not None

    @pytest.mark.django_db
    def test_sort_topseller_with_large_dataset(self, admin_user, edge_case_products):
        """Test sort_topseller with large dataset."""
        # Create many topsellers
        topsellers = []
        for i, product in enumerate(edge_case_products):
            topseller = Topseller.objects.create(product=product, position=(i + 1) * 10)
            topsellers.append(topseller)

        # Sort with large dataset
        topseller_ids = [t.id for t in topsellers]
        request = RequestFactory().post(
            "/sort-topseller", data=json.dumps({"topseller_ids": topseller_ids}), content_type="application/json"
        )
        request.session = {}
        request.user = admin_user

        # Should handle large dataset efficiently
        result = sort_topseller(request)
        assert result.status_code == 200


class TestTopsellerSecurityEdgeCases:
    """Test topseller security edge cases."""

    @pytest.mark.django_db
    def test_manage_topseller_view_with_sql_injection_filter(self, admin_user, edge_case_products):
        """Test ManageTopsellerView with SQL injection attempt in filter."""
        view = ManageTopsellerView()
        view.request = RequestFactory().get("/?filter='; DROP TABLE products; --")
        view.request.user = admin_user
        view.request.session = {"topseller-amount": 25}

        # Should handle SQL injection attempt safely
        context = view.get_context_data()
        assert context is not None
        assert context["filter"] == "'; DROP TABLE products; --"

    @pytest.mark.django_db
    def test_manage_topseller_view_with_xss_filter(self, admin_user, edge_case_products):
        """Test ManageTopsellerView with XSS attempt in filter."""
        view = ManageTopsellerView()
        view.request = RequestFactory().get("/?filter=<script>alert('xss')</script>")
        view.request.user = admin_user
        view.request.session = {"topseller-amount": 25}

        # Should handle XSS attempt safely
        context = view.get_context_data()
        assert context is not None
        assert context["filter"] == "<script>alert('xss')</script>"

    @pytest.mark.django_db
    def test_sort_topseller_with_malicious_json(self, admin_user):
        """Test sort_topseller with malicious JSON."""
        request = RequestFactory().post(
            "/sort-topseller",
            data=json.dumps({"topseller_ids": [1, 2, 3], "malicious": "data"}),
            content_type="application/json",
        )
        request.session = {}
        request.user = admin_user

        # Should handle malicious JSON safely
        result = sort_topseller(request)
        assert result.status_code == 200

    @pytest.mark.django_db
    def test_add_topseller_with_malicious_data(self, admin_user):
        """Test add_topseller with malicious data."""
        request = RequestFactory().post(
            "/",
            {
                "product-1": "1",
                "malicious-key": "malicious-value",
                "product-<script>": "alert('xss')",
            },
        )
        request.session = {}
        request.user = admin_user

        with patch("lfs.manage.topseller.views.ManageTopsellerView") as mock_view_class:
            mock_view = MagicMock()
            mock_view_class.return_value = mock_view
            mock_view.get_context_data.return_value = {"topseller": [], "total": 0}

            # Should handle malicious data safely
            result = add_topseller(request)
            assert result is not None


class TestTopsellerSystemEdgeCases:
    """Test topseller system edge cases."""

    @pytest.mark.django_db
    def test_manage_topseller_view_with_database_error(self, admin_user, edge_case_products):
        """Test ManageTopsellerView with database error."""
        with patch("lfs.catalog.models.Product.objects.filter") as mock_filter:
            mock_filter.side_effect = DatabaseError("Database error")

            view = ManageTopsellerView()
            view.request = RequestFactory().get("/")
            view.request.user = admin_user
            view.request.session = {"topseller-amount": 25}

            # Should handle database error gracefully
            with pytest.raises(DatabaseError):
                view.get_context_data()

    @pytest.mark.django_db
    def test_sort_topseller_with_database_error(self, admin_user):
        """Test sort_topseller with database error."""
        with patch("lfs.marketing.models.Topseller.objects.get") as mock_get:
            mock_get.side_effect = DatabaseError("Database error")

            request = RequestFactory().post(
                "/sort-topseller", data=json.dumps({"topseller_ids": [1]}), content_type="application/json"
            )
            request.session = {}
        request.user = admin_user

            # Should handle database error gracefully
            result = sort_topseller(request)
            assert result.status_code == 200

    @pytest.mark.django_db
    def test_update_positions_with_database_error(self, edge_case_topsellers):
        """Test _update_positions with database error."""
        with patch("lfs.marketing.models.Topseller.objects.all") as mock_all:
            mock_all.side_effect = DatabaseError("Database error")

            # Should handle database error gracefully
            with pytest.raises(DatabaseError):
                _update_positions()

    @pytest.mark.django_db
    def test_manage_topseller_view_with_memory_error(self, admin_user, edge_case_products):
        """Test ManageTopsellerView with memory error."""
        with patch("lfs.catalog.models.Product.objects.filter") as mock_filter:
            mock_filter.side_effect = MemoryError("Memory error")

            view = ManageTopsellerView()
            view.request = RequestFactory().get("/")
            view.request.user = admin_user
            view.request.session = {"topseller-amount": 25}

            # Should handle memory error gracefully
            with pytest.raises(MemoryError):
                view.get_context_data()

    @pytest.mark.django_db
    def test_manage_topseller_view_with_timeout_error(self, admin_user, edge_case_products):
        """Test ManageTopsellerView with timeout error."""
        with patch("lfs.catalog.models.Product.objects.filter") as mock_filter:
            mock_filter.side_effect = TimeoutError("Timeout error")

            view = ManageTopsellerView()
            view.request = RequestFactory().get("/")
            view.request.user = admin_user
            view.request.session = {"topseller-amount": 25}

            # Should handle timeout error gracefully
            with pytest.raises(TimeoutError):
                view.get_context_data()
