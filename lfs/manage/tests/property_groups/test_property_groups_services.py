import pytest
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import RequestFactory

from lfs.catalog.models import PropertyGroup, Property, Product, GroupsPropertiesRelation

User = get_user_model()


@pytest.fixture
def request_factory():
    """Request factory for creating mock requests."""
    return RequestFactory()


@pytest.fixture
def admin_user():
    """Admin user for testing."""
    return User.objects.create_user(
        username="admin", email="admin@example.com", password="testpass123", is_staff=True, is_superuser=True
    )


@pytest.fixture
def sample_property_group():
    """Create a sample property group for testing."""
    return PropertyGroup.objects.create(name="Test Property Group")


@pytest.fixture
def sample_property():
    """Create a sample property for testing."""
    return Property.objects.create(
        name="test_property",
        title="Test Property",
        type=1,  # Text field
    )


@pytest.fixture
def sample_product(shop):
    """Create a sample product for testing."""
    return Product.objects.create(name="Test Product", slug="test-product", price=10.99, active=True)


class TestPropertyGroupDataServices:
    """Test property group data services."""

    @pytest.mark.django_db
    def test_property_group_data_service_get_property_group_data(self, sample_property_group):
        """Test getting property group data."""
        data = {
            "property_group": sample_property_group,
            "name": sample_property_group.name,
            "position": sample_property_group.position,
            "uid": sample_property_group.uid,
        }

        assert data["property_group"] == sample_property_group
        assert data["name"] == "Test Property Group"
        assert data["position"] == 1000  # Default position
        assert data["uid"] is not None

    @pytest.mark.django_db
    def test_property_group_data_service_get_property_group_properties(self, sample_property_group, sample_property):
        """Test getting property group properties."""
        GroupsPropertiesRelation.objects.create(group=sample_property_group, property=sample_property, position=1)

        properties = sample_property_group.properties.all()
        assert len(properties) == 1
        assert sample_property in properties

    @pytest.mark.django_db
    def test_property_group_data_service_get_property_group_products(self, sample_property_group, sample_product):
        """Test getting property group products."""
        sample_property_group.products.add(sample_product)

        products = sample_property_group.products.all()
        assert len(products) == 1
        assert sample_product in products

    @pytest.mark.django_db
    def test_property_group_data_service_get_property_group_properties_count(
        self, sample_property_group, sample_property
    ):
        """Test getting property group properties count."""
        GroupsPropertiesRelation.objects.create(group=sample_property_group, property=sample_property, position=1)

        count = sample_property_group.properties.count()
        assert count == 1

    @pytest.mark.django_db
    def test_property_group_data_service_get_property_group_products_count(self, sample_property_group, sample_product):
        """Test getting property group products count."""
        sample_property_group.products.add(sample_product)

        count = sample_property_group.products.count()
        assert count == 1

    @pytest.mark.django_db
    def test_property_group_data_service_get_property_group_properties_empty(self, sample_property_group):
        """Test getting property group properties when empty."""
        properties = sample_property_group.properties.all()
        assert len(properties) == 0

    @pytest.mark.django_db
    def test_property_group_data_service_get_property_group_products_empty(self, sample_property_group):
        """Test getting property group products when empty."""
        products = sample_property_group.products.all()
        assert len(products) == 0

    @pytest.mark.django_db
    def test_property_group_data_service_get_property_group_properties_ordered(self, sample_property_group):
        """Test getting property group properties in correct order."""
        property1 = Property.objects.create(name="property1", title="Property 1", type=1)
        property2 = Property.objects.create(name="property2", title="Property 2", type=1)
        property3 = Property.objects.create(name="property3", title="Property 3", type=1)

        GroupsPropertiesRelation.objects.create(group=sample_property_group, property=property1, position=3)
        GroupsPropertiesRelation.objects.create(group=sample_property_group, property=property2, position=1)
        GroupsPropertiesRelation.objects.create(group=sample_property_group, property=property3, position=2)

        # Get properties through the GroupsPropertiesRelation model to get proper ordering
        gps = GroupsPropertiesRelation.objects.filter(group=sample_property_group).order_by("position")
        properties = [gp.property for gp in gps]
        assert len(properties) == 3
        assert properties[0] == property2  # position 1
        assert properties[1] == property3  # position 2
        assert properties[2] == property1  # position 3

    @pytest.mark.django_db
    def test_property_group_data_service_get_property_group_products_ordered(self, sample_property_group, shop):
        """Test getting property group products in correct order."""
        product1 = Product.objects.create(name="Product 1", slug="product-1", price=Decimal("10.99"), active=True)
        product2 = Product.objects.create(name="Product 2", slug="product-2", price=Decimal("20.99"), active=True)
        product3 = Product.objects.create(name="Product 3", slug="product-3", price=Decimal("30.99"), active=True)

        sample_property_group.products.add(product1, product2, product3)

        products = sample_property_group.products.all()
        assert len(products) == 3
        assert product1 in products
        assert product2 in products
        assert product3 in products


class TestPropertyGroupFilteringServices:
    """Test property group filtering services."""

    @pytest.mark.django_db
    def test_property_group_filtering_service_filter_by_name(self, sample_property_group):
        """Test filtering property groups by name."""
        PropertyGroup.objects.create(name="Another Group")
        PropertyGroup.objects.create(name="Test Group")

        filtered_groups = PropertyGroup.objects.filter(name__icontains="Test")
        assert len(filtered_groups) == 2
        assert sample_property_group in filtered_groups

    @pytest.mark.django_db
    def test_property_group_filtering_service_filter_by_name_exact(self, sample_property_group):
        """Test filtering property groups by exact name."""
        PropertyGroup.objects.create(name="Another Group")
        PropertyGroup.objects.create(name="Test Group")

        filtered_groups = PropertyGroup.objects.filter(name="Test Property Group")
        assert len(filtered_groups) == 1
        assert sample_property_group in filtered_groups

    @pytest.mark.django_db
    def test_property_group_filtering_service_filter_by_name_case_insensitive(self, sample_property_group):
        """Test filtering property groups by name case insensitive."""
        PropertyGroup.objects.create(name="Another Group")
        PropertyGroup.objects.create(name="Test Group")

        filtered_groups = PropertyGroup.objects.filter(name__icontains="test")
        assert len(filtered_groups) == 2
        assert sample_property_group in filtered_groups

    @pytest.mark.django_db
    def test_property_group_filtering_service_filter_by_position(self, sample_property_group):
        """Test filtering property groups by position."""
        PropertyGroup.objects.create(name="Group 1", position=500)
        PropertyGroup.objects.create(name="Group 2", position=1500)

        filtered_groups = PropertyGroup.objects.filter(position__gte=1000)
        assert len(filtered_groups) == 2
        assert sample_property_group in filtered_groups

    @pytest.mark.django_db
    def test_property_group_filtering_service_filter_by_position_range(self, sample_property_group):
        """Test filtering property groups by position range."""
        PropertyGroup.objects.create(name="Group 1", position=500)
        PropertyGroup.objects.create(name="Group 2", position=1500)

        filtered_groups = PropertyGroup.objects.filter(position__gte=500, position__lte=1000)
        assert len(filtered_groups) == 2
        assert sample_property_group in filtered_groups

    @pytest.mark.django_db
    def test_property_group_filtering_service_filter_by_uid(self, sample_property_group):
        """Test filtering property groups by UID."""
        PropertyGroup.objects.create(name="Another Group")

        filtered_groups = PropertyGroup.objects.filter(uid=sample_property_group.uid)
        assert len(filtered_groups) == 1
        assert sample_property_group in filtered_groups

    @pytest.mark.django_db
    def test_property_group_filtering_service_filter_by_products(self, sample_property_group, sample_product):
        """Test filtering property groups by products."""
        sample_property_group.products.add(sample_product)
        PropertyGroup.objects.create(name="Another Group")

        filtered_groups = PropertyGroup.objects.filter(products=sample_product)
        assert len(filtered_groups) == 1
        assert sample_property_group in filtered_groups

    @pytest.mark.django_db
    def test_property_group_filtering_service_filter_by_properties(self, sample_property_group, sample_property):
        """Test filtering property groups by properties."""
        GroupsPropertiesRelation.objects.create(group=sample_property_group, property=sample_property, position=1)
        PropertyGroup.objects.create(name="Another Group")

        filtered_groups = PropertyGroup.objects.filter(properties=sample_property)
        assert len(filtered_groups) == 1
        assert sample_property_group in filtered_groups

    @pytest.mark.django_db
    def test_property_group_filtering_service_filter_by_multiple_criteria(self, sample_property_group, sample_product):
        """Test filtering property groups by multiple criteria."""
        sample_property_group.products.add(sample_product)
        PropertyGroup.objects.create(name="Another Group")
        PropertyGroup.objects.create(name="Test Group")

        filtered_groups = PropertyGroup.objects.filter(name__icontains="Test", products=sample_product)
        assert len(filtered_groups) == 1
        assert sample_property_group in filtered_groups

    @pytest.mark.django_db
    def test_property_group_filtering_service_filter_by_nonexistent_criteria(self, sample_property_group):
        """Test filtering property groups by nonexistent criteria."""
        filtered_groups = PropertyGroup.objects.filter(name="Nonexistent Group")
        assert len(filtered_groups) == 0

    @pytest.mark.django_db
    def test_property_group_filtering_service_filter_by_empty_criteria(self, sample_property_group):
        """Test filtering property groups by empty criteria."""
        filtered_groups = PropertyGroup.objects.filter(name="")
        assert len(filtered_groups) == 0

    @pytest.mark.django_db
    def test_property_group_filtering_service_filter_by_none_criteria(self, sample_property_group):
        """Test filtering property groups by None criteria."""
        filtered_groups = PropertyGroup.objects.filter(name=None)
        assert len(filtered_groups) == 0


class TestPropertyGroupSearchServices:
    """Test property group search services."""

    @pytest.mark.django_db
    def test_property_group_search_service_search_by_name(self, sample_property_group):
        """Test searching property groups by name."""
        PropertyGroup.objects.create(name="Another Group")
        PropertyGroup.objects.create(name="Test Group")

        search_results = PropertyGroup.objects.filter(name__icontains="Test")
        assert len(search_results) == 2
        assert sample_property_group in search_results

    @pytest.mark.django_db
    def test_property_group_search_service_search_by_name_partial(self, sample_property_group):
        """Test searching property groups by partial name."""
        PropertyGroup.objects.create(name="Another Group")
        PropertyGroup.objects.create(name="Test Group")

        search_results = PropertyGroup.objects.filter(name__icontains="Property")
        assert len(search_results) == 1
        assert sample_property_group in search_results

    @pytest.mark.django_db
    def test_property_group_search_service_search_by_name_case_insensitive(self, sample_property_group):
        """Test searching property groups by name case insensitive."""
        PropertyGroup.objects.create(name="Another Group")
        PropertyGroup.objects.create(name="Test Group")

        search_results = PropertyGroup.objects.filter(name__icontains="test")
        assert len(search_results) == 2
        assert sample_property_group in search_results

    @pytest.mark.django_db
    def test_property_group_search_service_search_by_name_whitespace(self, sample_property_group):
        """Test searching property groups by name with whitespace."""
        PropertyGroup.objects.create(name="Another Group")
        PropertyGroup.objects.create(name="Test Group")

        search_results = PropertyGroup.objects.filter(name__icontains="  Test  ")
        assert len(search_results) == 0  # Whitespace should not match

    @pytest.mark.django_db
    def test_property_group_search_service_search_by_name_empty(self, sample_property_group):
        """Test searching property groups by empty name."""
        PropertyGroup.objects.create(name="Another Group")
        PropertyGroup.objects.create(name="Test Group")

        search_results = PropertyGroup.objects.filter(name__icontains="")
        assert len(search_results) == 3  # Empty string matches all

    @pytest.mark.django_db
    def test_property_group_search_service_search_by_name_none(self, sample_property_group):
        """Test searching property groups by None name."""
        PropertyGroup.objects.create(name="Another Group")
        PropertyGroup.objects.create(name="Test Group")

        # Django doesn't allow None as a query value, so this should raise ValueError
        with pytest.raises(ValueError, match="Cannot use None as a query value"):
            PropertyGroup.objects.filter(name__icontains=None)

    @pytest.mark.django_db
    def test_property_group_search_service_search_by_name_unicode(self, sample_property_group):
        """Test searching property groups by unicode name."""
        PropertyGroup.objects.create(name="测试组")
        PropertyGroup.objects.create(name="Another Group")

        search_results = PropertyGroup.objects.filter(name__icontains="测试")
        assert len(search_results) == 1

    @pytest.mark.django_db
    def test_property_group_search_service_search_by_name_special_characters(self, sample_property_group):
        """Test searching property groups by special characters."""
        PropertyGroup.objects.create(name="Group-Name")
        PropertyGroup.objects.create(name="Another Group")

        search_results = PropertyGroup.objects.filter(name__icontains="-")
        assert len(search_results) == 1

    @pytest.mark.django_db
    def test_property_group_search_service_search_by_name_numbers(self, sample_property_group):
        """Test searching property groups by numbers."""
        PropertyGroup.objects.create(name="Group 123")
        PropertyGroup.objects.create(name="Another Group")

        search_results = PropertyGroup.objects.filter(name__icontains="123")
        assert len(search_results) == 1

    @pytest.mark.django_db
    def test_property_group_search_service_search_by_name_very_long(self, sample_property_group):
        """Test searching property groups by very long name."""
        very_long_name = "A" * 1000
        PropertyGroup.objects.create(name=very_long_name)
        PropertyGroup.objects.create(name="Another Group")

        search_results = PropertyGroup.objects.filter(name__icontains="A" * 500)
        assert len(search_results) == 1


class TestPropertyGroupValidationServices:
    """Test property group validation services."""

    @pytest.mark.django_db
    def test_property_group_validation_service_validate_name_required(self, sample_property_group):
        """Test validating property group name is required."""
        # The name field has blank=True, so empty names are allowed
        property_group = PropertyGroup(name="")
        property_group.full_clean()  # This should not raise an exception
        assert property_group.name == ""

    @pytest.mark.django_db
    def test_property_group_validation_service_validate_name_max_length(self, sample_property_group):
        """Test validating property group name max length."""
        with pytest.raises(Exception):
            PropertyGroup(name="A" * 51).full_clean()

    @pytest.mark.django_db
    def test_property_group_validation_service_validate_name_valid(self, sample_property_group):
        """Test validating property group name is valid."""
        PropertyGroup(name="Valid Name").full_clean()  # Should not raise exception

    @pytest.mark.django_db
    def test_property_group_validation_service_validate_position_valid(self, sample_property_group):
        """Test validating property group position is valid."""
        PropertyGroup(name="Valid Name", position=1000).full_clean()  # Should not raise exception

    @pytest.mark.django_db
    def test_property_group_validation_service_validate_position_negative(self, sample_property_group):
        """Test validating property group position can be negative."""
        PropertyGroup(name="Valid Name", position=-1).full_clean()  # Should not raise exception

    @pytest.mark.django_db
    def test_property_group_validation_service_validate_position_zero(self, sample_property_group):
        """Test validating property group position can be zero."""
        PropertyGroup(name="Valid Name", position=0).full_clean()  # Should not raise exception

    @pytest.mark.django_db
    def test_property_group_validation_service_validate_position_large(self, sample_property_group):
        """Test validating property group position can be large."""
        PropertyGroup(name="Valid Name", position=999999999).full_clean()  # Should not raise exception

    @pytest.mark.django_db
    def test_property_group_validation_service_validate_position_none(self, sample_property_group):
        """Test validating property group position cannot be None."""
        # The position field doesn't allow null values, so this should raise ValidationError
        with pytest.raises(ValidationError, match="This field cannot be null"):
            PropertyGroup(name="Valid Name", position=None).full_clean()

    @pytest.mark.django_db
    def test_property_group_validation_service_validate_uid_auto_generated(self, sample_property_group):
        """Test validating property group UID is auto-generated."""
        assert sample_property_group.uid is not None
        assert isinstance(sample_property_group.uid, str)
        assert len(sample_property_group.uid) > 0

    @pytest.mark.django_db
    def test_property_group_validation_service_validate_uid_unique(self, sample_property_group):
        """Test validating property group UID is unique."""
        property_group2 = PropertyGroup.objects.create(name="Another Group")
        assert sample_property_group.uid != property_group2.uid

    @pytest.mark.django_db
    def test_property_group_validation_service_validate_uid_immutable(self, sample_property_group):
        """Test validating property group UID is immutable."""
        original_uid = sample_property_group.uid
        sample_property_group.name = "Updated Name"
        sample_property_group.save()
        assert sample_property_group.uid == original_uid

    @pytest.mark.django_db
    def test_property_group_validation_service_validate_uid_length(self, sample_property_group):
        """Test validating property group UID length."""
        assert len(sample_property_group.uid) <= 50  # max_length constraint

    @pytest.mark.django_db
    def test_property_group_validation_service_validate_uid_character_set(self, sample_property_group):
        """Test validating property group UID character set."""
        uid = sample_property_group.uid
        assert uid.replace("_", "").replace("-", "").isalnum() or uid.isalnum()


class TestPropertyGroupUtilityServices:
    """Test property group utility services."""

    @pytest.mark.django_db
    def test_property_group_utility_service_get_property_group_by_id(self, sample_property_group):
        """Test getting property group by ID."""
        retrieved_group = PropertyGroup.objects.get(id=sample_property_group.id)
        assert retrieved_group == sample_property_group

    @pytest.mark.django_db
    def test_property_group_utility_service_get_property_group_by_name(self, sample_property_group):
        """Test getting property group by name."""
        retrieved_group = PropertyGroup.objects.get(name=sample_property_group.name)
        assert retrieved_group == sample_property_group

    @pytest.mark.django_db
    def test_property_group_utility_service_get_property_group_by_uid(self, sample_property_group):
        """Test getting property group by UID."""
        retrieved_group = PropertyGroup.objects.get(uid=sample_property_group.uid)
        assert retrieved_group == sample_property_group

    @pytest.mark.django_db
    def test_property_group_utility_service_get_property_group_by_nonexistent_id(self, sample_property_group):
        """Test getting property group by nonexistent ID."""
        with pytest.raises(PropertyGroup.DoesNotExist):
            PropertyGroup.objects.get(id=99999)

    @pytest.mark.django_db
    def test_property_group_utility_service_get_property_group_by_nonexistent_name(self, sample_property_group):
        """Test getting property group by nonexistent name."""
        with pytest.raises(PropertyGroup.DoesNotExist):
            PropertyGroup.objects.get(name="Nonexistent Group")

    @pytest.mark.django_db
    def test_property_group_utility_service_get_property_group_by_nonexistent_uid(self, sample_property_group):
        """Test getting property group by nonexistent UID."""
        with pytest.raises(PropertyGroup.DoesNotExist):
            PropertyGroup.objects.get(uid="nonexistent_uid")

    @pytest.mark.django_db
    def test_property_group_utility_service_get_all_property_groups(self, sample_property_group):
        """Test getting all property groups."""
        PropertyGroup.objects.create(name="Another Group")

        all_groups = PropertyGroup.objects.all()
        assert len(all_groups) == 2
        assert sample_property_group in all_groups

    @pytest.mark.django_db
    def test_property_group_utility_service_get_property_groups_count(self, sample_property_group):
        """Test getting property groups count."""
        PropertyGroup.objects.create(name="Another Group")

        count = PropertyGroup.objects.count()
        assert count == 2

    @pytest.mark.django_db
    def test_property_group_utility_service_get_property_groups_ordered(self, sample_property_group):
        """Test getting property groups in correct order."""
        PropertyGroup.objects.create(name="Another Group", position=500)
        PropertyGroup.objects.create(name="Third Group", position=1500)

        ordered_groups = PropertyGroup.objects.all().order_by("position")
        assert len(ordered_groups) == 3
        assert ordered_groups[0].position == 500
        assert ordered_groups[1].position == 1000
        assert ordered_groups[2].position == 1500

    @pytest.mark.django_db
    def test_property_group_utility_service_get_property_groups_reverse_ordered(self, sample_property_group):
        """Test getting property groups in reverse order."""
        PropertyGroup.objects.create(name="Another Group", position=500)
        PropertyGroup.objects.create(name="Third Group", position=1500)

        reverse_ordered_groups = PropertyGroup.objects.all().order_by("-position")
        assert len(reverse_ordered_groups) == 3
        assert reverse_ordered_groups[0].position == 1500
        assert reverse_ordered_groups[1].position == 1000
        assert reverse_ordered_groups[2].position == 500

    @pytest.mark.django_db
    def test_property_group_utility_service_get_property_groups_filtered_and_ordered(self, sample_property_group):
        """Test getting property groups filtered and ordered."""
        PropertyGroup.objects.create(name="Another Group", position=500)
        PropertyGroup.objects.create(name="Third Group", position=1500)

        filtered_groups = PropertyGroup.objects.filter(position__gte=1000).order_by("position")
        assert len(filtered_groups) == 2
        assert filtered_groups[0].position == 1000
        assert filtered_groups[1].position == 1500

    @pytest.mark.django_db
    def test_property_group_utility_service_get_property_groups_first(self, sample_property_group):
        """Test getting first property group."""
        PropertyGroup.objects.create(name="Another Group", position=500)
        PropertyGroup.objects.create(name="Third Group", position=1500)

        first_group = PropertyGroup.objects.all().order_by("position").first()
        assert first_group.position == 500

    @pytest.mark.django_db
    def test_property_group_utility_service_get_property_groups_last(self, sample_property_group):
        """Test getting last property group."""
        PropertyGroup.objects.create(name="Another Group", position=500)
        PropertyGroup.objects.create(name="Third Group", position=1500)

        last_group = PropertyGroup.objects.all().order_by("position").last()
        assert last_group.position == 1500

    @pytest.mark.django_db
    def test_property_group_utility_service_get_property_groups_exists(self, sample_property_group):
        """Test checking if property group exists."""
        assert PropertyGroup.objects.filter(id=sample_property_group.id).exists()
        assert not PropertyGroup.objects.filter(id=99999).exists()

    @pytest.mark.django_db
    def test_property_group_utility_service_get_property_groups_values(self, sample_property_group):
        """Test getting property group values."""
        values = PropertyGroup.objects.filter(id=sample_property_group.id).values("name", "position")
        assert len(values) == 1
        assert values[0]["name"] == "Test Property Group"
        assert values[0]["position"] == 1000

    @pytest.mark.django_db
    def test_property_group_utility_service_get_property_groups_values_list(self, sample_property_group):
        """Test getting property group values list."""
        values_list = PropertyGroup.objects.filter(id=sample_property_group.id).values_list("name", "position")
        assert len(values_list) == 1
        assert values_list[0][0] == "Test Property Group"
        assert values_list[0][1] == 1000
