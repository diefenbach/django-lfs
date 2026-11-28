import pytest
from datetime import datetime, date
from decimal import Decimal


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

    def test_should_filter_by_a_price_calculator_that_is_not_the_shop_default(
        self, product_filter_service, sample_products
    ):
        """Products without own calculator inherit the shop's (gross); filtering by net finds only explicit ones."""
        filters = {"price_calculator": "lfs.net_price.calculator.NetPriceCalculator"}

        result = product_filter_service.filter_products(Product.objects.all(), filters)

        assert list(result) == [sample_products[1]]

    def test_should_include_inheriting_products_when_filtering_by_the_shop_default(
        self, product_filter_service, sample_products
    ):
        filters = {"price_calculator": "lfs.gross_price.calculator.GrossPriceCalculator"}

        result = product_filter_service.filter_products(Product.objects.all(), filters)

        assert set(result) == {sample_products[0], sample_products[2]}

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

    def test_should_return_categories_price_stock_and_status(self, product_data_service, sample_products):
        product = sample_products[0]
        product.manage_stock_amount = True
        product.stock_amount = 10.0
        product.save()
        product.categories.add(
            Category.objects.create(name="Electronics", slug="electronics"),
            Category.objects.create(name="Computers", slug="computers"),
        )

        result = product_data_service.get_product_summary(product)

        assert result == {
            "categories": "Electronics, Computers",
            "price": Decimal("19.99"),
            "stock": 10.0,
            "active": True,
        }

    def test_should_limit_categories_to_first_three(self, product_data_service, sample_products):
        product = sample_products[0]
        for i in range(5):
            product.categories.add(Category.objects.create(name=f"Category {i+1}", slug=f"category-{i+1}"))

        result = product_data_service.get_product_summary(product)

        assert len(result["categories"].split(", ")) == 3

    def test_should_return_no_stock_when_it_is_not_managed(self, product_data_service, sample_products):
        product = sample_products[0]
        product.manage_stock_amount = False
        product.stock_amount = 10.0
        product.save()

        assert product_data_service.get_product_summary(product)["stock"] is None
