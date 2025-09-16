"""
Comprehensive unit tests for products services.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Parametrization for variations

Tests cover:
- ProductFilterService (filtering logic with various criteria)
- ProductDataService (data calculation and enrichment)
- Edge cases and error conditions
"""

import pytest
from datetime import datetime, date
from decimal import Decimal
from unittest.mock import Mock, patch


from lfs.catalog.models import Product, Category
from lfs.manage.products.services import ProductFilterService, ProductDataService


@pytest.fixture
def product_filter_service():
    """ProductFilterService instance for testing."""
    return ProductFilterService()


@pytest.fixture
def product_data_service():
    """ProductDataService instance for testing."""
    return ProductDataService()


@pytest.fixture
def sample_products(db, shop):
    """Create sample products with different attributes for filtering tests."""
    products = []

    # Product 1: Active product with specific attributes
    product1 = Product.objects.create(
        name="Test Product One",
        slug="test-product-one-services",
        short_description="Short description one",
        sku="SERVICES001",
        sub_type="configurable",
        price_calculator="lfs.gross_price.calculator.GrossPriceCalculator",
        active=True,
        price=Decimal("19.99"),
    )
    products.append(product1)

    # Product 2: Inactive product
    product2 = Product.objects.create(
        name="Test Product Two",
        slug="test-product-two-services",
        short_description="Short description two",
        sku="SERVICES002",
        sub_type="simple",
        price_calculator="lfs.net_price.calculator.NetPriceCalculator",
        active=False,
        price=Decimal("29.99"),
    )
    products.append(product2)

    # Product 3: Product with None price_calculator (inherits from shop)
    product3 = Product.objects.create(
        name="Another Product",
        slug="another-product-services",
        short_description="Different description",
        sku="SERVICES003",
        sub_type="configurable",
        price_calculator=None,
        active=True,
        price=Decimal("39.99"),
    )
    products.append(product3)

    return products


class TestProductFilterService:
    """Test ProductFilterService functionality."""

    def test_should_return_all_products_when_no_filters(self, product_filter_service, sample_products):
        """Should return all products when no filters are applied."""
        queryset = Product.objects.all()

        result = product_filter_service.filter_products(queryset, {})

        assert result.count() == 3
        assert list(result) == list(queryset)

    def test_should_handle_non_dict_filters_gracefully(self, product_filter_service, sample_products):
        """Should handle corrupted session data (non-dict filters) gracefully."""
        queryset = Product.objects.all()

        result = product_filter_service.filter_products(queryset, "corrupted_string")

        assert result.count() == 3  # Should return all products

    def test_should_filter_by_name_in_product_name(self, product_filter_service, sample_products):
        """Should filter products by name match in product name."""
        queryset = Product.objects.all()
        filters = {"name": "Test Product One"}

        result = product_filter_service.filter_products(queryset, filters)

        assert result.count() == 1
        assert result.first().name == "Test Product One"

    def test_should_filter_by_name_in_short_description(self, product_filter_service, sample_products):
        """Should filter products by name match in short description."""
        queryset = Product.objects.all()
        filters = {"name": "Different"}

        result = product_filter_service.filter_products(queryset, filters)

        assert result.count() == 1
        assert "Different" in result.first().short_description

    def test_should_filter_by_name_case_insensitive(self, product_filter_service, sample_products):
        """Should perform case-insensitive name filtering."""
        queryset = Product.objects.all()
        filters = {"name": "test product"}

        result = product_filter_service.filter_products(queryset, filters)

        assert result.count() == 2  # Should match "Test Product One" and "Test Product Two"

    def test_should_ignore_empty_name_filter(self, product_filter_service, sample_products):
        """Should ignore empty name filter."""
        queryset = Product.objects.all()
        filters = {"name": ""}

        result = product_filter_service.filter_products(queryset, filters)

        assert result.count() == 3

    def test_should_ignore_whitespace_only_name_filter(self, product_filter_service, sample_products):
        """Should ignore whitespace-only name filter."""
        queryset = Product.objects.all()
        filters = {"name": "   "}

        result = product_filter_service.filter_products(queryset, filters)

        assert result.count() == 3

    def test_should_filter_by_sku(self, product_filter_service, sample_products):
        """Should filter products by SKU."""
        queryset = Product.objects.all()
        filters = {"sku": "SERVICES001"}

        result = product_filter_service.filter_products(queryset, filters)

        assert result.count() == 1
        assert result.first().sku == "SERVICES001"

    def test_should_filter_by_sku_partial_match(self, product_filter_service, sample_products):
        """Should filter products by partial SKU match."""
        queryset = Product.objects.all()
        filters = {"sku": "SERVICES"}

        result = product_filter_service.filter_products(queryset, filters)

        assert result.count() == 3  # SERVICES001, SERVICES002, and SERVICES003

    def test_should_ignore_empty_sku_filter(self, product_filter_service, sample_products):
        """Should ignore empty SKU filter."""
        queryset = Product.objects.all()
        filters = {"sku": ""}

        result = product_filter_service.filter_products(queryset, filters)

        assert result.count() == 3

    def test_should_filter_by_sub_type(self, product_filter_service, sample_products):
        """Should filter products by sub_type."""
        queryset = Product.objects.all()
        filters = {"sub_type": "configurable"}

        result = product_filter_service.filter_products(queryset, filters)

        assert result.count() == 2  # product1 and product3
        for product in result:
            assert product.sub_type == "configurable"

    def test_should_ignore_empty_sub_type_filter(self, product_filter_service, sample_products):
        """Should ignore empty sub_type filter."""
        queryset = Product.objects.all()
        filters = {"sub_type": ""}

        result = product_filter_service.filter_products(queryset, filters)

        assert result.count() == 3

    def test_should_filter_by_active_status(self, product_filter_service, sample_products):
        """Should filter products by active status."""
        queryset = Product.objects.all()
        filters = {"status": "active"}

        result = product_filter_service.filter_products(queryset, filters)

        assert result.count() == 2  # product1 and product3
        for product in result:
            assert product.active is True

    def test_should_filter_by_inactive_status(self, product_filter_service, sample_products):
        """Should filter products by inactive status."""
        queryset = Product.objects.all()
        filters = {"status": "inactive"}

        result = product_filter_service.filter_products(queryset, filters)

        assert result.count() == 1  # product2
        assert result.first().active is False

    def test_should_ignore_empty_status_filter(self, product_filter_service, sample_products):
        """Should ignore empty status filter."""
        queryset = Product.objects.all()
        filters = {"status": ""}

        result = product_filter_service.filter_products(queryset, filters)

        assert result.count() == 3

    @patch("lfs.core.utils.get_default_shop")
    def test_should_filter_by_explicit_price_calculator(self, mock_get_shop, product_filter_service, sample_products):
        """Should filter products by explicit price calculator."""
        # Mock shop with different default price calculator
        mock_shop = Mock()
        mock_shop.price_calculator = "different.calculator"
        mock_get_shop.return_value = mock_shop

        queryset = Product.objects.all()
        filters = {"price_calculator": "lfs.net_price.calculator.NetPriceCalculator"}

        result = product_filter_service.filter_products(queryset, filters)

        assert result.count() == 1  # Only product2 has explicit net price calculator
        assert result.first().price_calculator == "lfs.net_price.calculator.NetPriceCalculator"

    @patch("lfs.core.utils.get_default_shop")
    def test_should_filter_by_price_calculator_including_shop_default(
        self, mock_get_shop, product_filter_service, sample_products
    ):
        """Should include products inheriting from shop when filtering by shop default price calculator."""
        # Mock shop with gross price calculator as default
        mock_shop = Mock()
        mock_shop.price_calculator = "lfs.gross_price.calculator.GrossPriceCalculator"
        mock_get_shop.return_value = mock_shop

        queryset = Product.objects.all()
        filters = {"price_calculator": "lfs.gross_price.calculator.GrossPriceCalculator"}

        result = product_filter_service.filter_products(queryset, filters)

        # Should include product1 (explicit gross) and product3 (None, inherits gross)
        assert result.count() == 2
        explicit_gross = result.filter(price_calculator="lfs.gross_price.calculator.GrossPriceCalculator")
        inherited_gross = result.filter(price_calculator__isnull=True)
        assert explicit_gross.count() == 1
        assert inherited_gross.count() == 1

    @patch("lfs.core.utils.get_default_shop")
    def test_should_exclude_inherited_when_filtering_by_non_shop_default(
        self, mock_get_shop, product_filter_service, sample_products
    ):
        """Should exclude products inheriting from shop when filtering by non-shop default."""
        # Mock shop with gross price calculator as default
        mock_shop = Mock()
        mock_shop.price_calculator = "lfs.gross_price.calculator.GrossPriceCalculator"
        mock_get_shop.return_value = mock_shop

        queryset = Product.objects.all()
        filters = {"price_calculator": "lfs.net_price.calculator.NetPriceCalculator"}  # Not the shop default

        result = product_filter_service.filter_products(queryset, filters)

        # Should only include product2 (explicit net), not product3 (inherits gross)
        assert result.count() == 1
        assert result.first().price_calculator == "lfs.net_price.calculator.NetPriceCalculator"

    def test_should_ignore_empty_price_calculator_filter(self, product_filter_service, sample_products):
        """Should ignore empty price_calculator filter."""
        queryset = Product.objects.all()
        filters = {"price_calculator": ""}

        result = product_filter_service.filter_products(queryset, filters)

        assert result.count() == 3

    def test_should_combine_multiple_filters(self, product_filter_service, sample_products):
        """Should apply multiple filters together."""
        queryset = Product.objects.all()
        filters = {"name": "Test", "sub_type": "configurable", "status": "active"}

        result = product_filter_service.filter_products(queryset, filters)

        assert result.count() == 1  # Only product1 matches all criteria
        product = result.first()
        assert "Test" in product.name
        assert product.sub_type == "configurable"
        assert product.active is True

    def test_parse_iso_date_valid_date(self, product_filter_service):
        """Should parse valid ISO date string."""
        date_string = "2023-12-25"

        result = product_filter_service.parse_iso_date(date_string)

        assert result == date(2023, 12, 25)

    def test_parse_iso_date_invalid_format(self, product_filter_service):
        """Should return None for invalid date format."""
        invalid_dates = ["", "invalid", "2023-13-45", "25-12-2023", "2023/12/25"]

        for date_string in invalid_dates:
            result = product_filter_service.parse_iso_date(date_string)
            assert result is None

    def test_parse_iso_date_none_input(self, product_filter_service):
        """Should return None for None input."""
        result = product_filter_service.parse_iso_date(None)

        assert result is None

    def test_parse_iso_date_whitespace_input(self, product_filter_service):
        """Should return None for whitespace input."""
        result = product_filter_service.parse_iso_date("   ")

        assert result is None

    def test_format_iso_date_with_date_object(self, product_filter_service):
        """Should format date object to ISO string."""
        test_date = date(2023, 12, 25)

        result = product_filter_service.format_iso_date(test_date)

        assert result == "2023-12-25"

    def test_format_iso_date_with_datetime_object(self, product_filter_service):
        """Should format datetime object to ISO string."""
        test_datetime = datetime(2023, 12, 25, 15, 30, 45)

        result = product_filter_service.format_iso_date(test_datetime)

        assert result == "2023-12-25"


class TestProductDataService:
    """Test ProductDataService functionality."""

    @patch.object(Product, "get_price")
    def test_should_return_product_summary_with_all_fields(self, mock_get_price, product_data_service, sample_products):
        """Should return complete product summary with all required fields."""
        product = sample_products[0]

        # Setup mocks and product data
        mock_get_price.return_value = Decimal("19.99")
        product.manage_stock_amount = True
        product.stock_amount = 10.0
        product.save()

        # Create categories for the product
        category1 = Category.objects.create(name="Electronics", slug="electronics")
        category2 = Category.objects.create(name="Computers", slug="computers")
        product.categories.add(category1, category2)

        result = product_data_service.get_product_summary(product)

        assert "categories" in result
        assert "price" in result
        assert "stock" in result
        assert "active" in result
        assert result["categories"] == "Electronics, Computers"
        assert result["price"] == Decimal("19.99")
        assert result["stock"] == 10.0
        assert result["active"] is True

    @patch.object(Product, "get_price")
    def test_should_limit_categories_to_first_three(self, mock_get_price, product_data_service, sample_products):
        """Should limit categories display to first three categories."""
        product = sample_products[0]

        # Setup mocks and product data
        mock_get_price.return_value = Decimal("19.99")
        product.manage_stock_amount = True
        product.stock_amount = 10.0
        product.save()

        # Create more than 3 categories
        categories = []
        for i in range(5):
            category = Category.objects.create(name=f"Category {i+1}", slug=f"category-{i+1}")
            categories.append(category)
            product.categories.add(category)

        result = product_data_service.get_product_summary(product)

        category_names = result["categories"].split(", ")
        assert len(category_names) == 3

    @patch.object(Product, "get_price")
    def test_should_handle_product_with_no_categories(self, mock_get_price, product_data_service, sample_products):
        """Should handle product with no categories."""
        product = sample_products[0]

        # Setup mocks and product data
        mock_get_price.return_value = Decimal("19.99")
        product.manage_stock_amount = True
        product.stock_amount = 10.0
        product.save()

        # Ensure no categories
        product.categories.clear()

        result = product_data_service.get_product_summary(product)

        assert result["categories"] == ""

    @patch.object(Product, "get_price")
    def test_should_call_product_methods_with_none_parameter(
        self, mock_get_price, product_data_service, sample_products
    ):
        """Should call product price method with None parameter."""
        product = sample_products[0]

        # Setup mocks and product data
        mock_get_price.return_value = Decimal("19.99")
        product.manage_stock_amount = True
        product.stock_amount = 10.0
        product.save()

        product_data_service.get_product_summary(product)

        mock_get_price.assert_called_once_with(None)

    @patch.object(Product, "get_price")
    def test_should_propagate_price_method_exceptions(self, mock_get_price, product_data_service, sample_products):
        """Should propagate exceptions from product price method (fail fast)."""
        product = sample_products[0]

        # Setup mocks - price method raises exception
        mock_get_price.side_effect = Exception("Price calculation error")
        product.manage_stock_amount = True
        product.stock_amount = 10.0
        product.save()

        # Should raise the exception
        with pytest.raises(Exception, match="Price calculation error"):
            product_data_service.get_product_summary(product)

    @patch.object(Product, "get_price")
    def test_should_return_none_stock_when_not_managed(self, mock_get_price, product_data_service, sample_products):
        """Should return None for stock when stock is not managed."""
        product = sample_products[0]

        # Setup mocks and product data - stock not managed
        mock_get_price.return_value = Decimal("19.99")
        product.manage_stock_amount = False
        product.stock_amount = 10.0  # This should be ignored
        product.save()

        result = product_data_service.get_product_summary(product)

        assert result["stock"] is None

    @patch.object(Product, "get_price")
    def test_should_return_stock_amount_when_managed(self, mock_get_price, product_data_service, sample_products):
        """Should return actual stock amount when stock is managed."""
        product = sample_products[0]

        # Setup mocks and product data - stock managed
        mock_get_price.return_value = Decimal("19.99")
        product.manage_stock_amount = True
        product.stock_amount = 15.5
        product.save()

        result = product_data_service.get_product_summary(product)

        assert result["stock"] == 15.5
