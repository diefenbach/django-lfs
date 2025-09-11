"""
Comprehensive end-to-end workflow tests for property_groups management.

Following TDD principles:
- Test complete user workflows from start to finish
- Test real user scenarios and business processes
- Clear test names describing the complete workflow
- Arrange-Act-Assert structure for each workflow step
- Test data consistency across workflow steps

Workflows covered:
- Complete property group management workflow (list -> create -> edit -> delete)
- Property group data management workflow (edit name -> save -> verify)
- Property group products workflow (assign -> view -> remove)
- Property group properties workflow (assign -> view -> remove)
- Session persistence workflow (maintain state across multiple requests)
- Error recovery workflow (handle errors gracefully and maintain state)
- Permission workflow (unauthorized access -> login -> authorized access)
- Property group lifecycle workflow (create -> modify -> view -> delete)
- Property group search workflow (search -> filter -> view results)
- Property group tab navigation workflow (navigate between tabs)
"""

import pytest
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse

from lfs.catalog.models import PropertyGroup, Property, Product, GroupsPropertiesRelation

User = get_user_model()


@pytest.fixture
def admin_user(db):
    """Admin user with proper permissions."""
    return User.objects.create_user(
        username="admin", email="admin@example.com", password="testpass123", is_staff=True, is_superuser=True
    )


@pytest.fixture
def shop(db):
    """Create a default shop for testing."""
    from lfs.core.models import Shop
    from lfs.core.models import Country
    from lfs.catalog.models import DeliveryTime, DELIVERY_TIME_UNIT_DAYS

    # Create required dependencies
    country = Country.objects.create(name="Test Country", code="TC")
    delivery_time = DeliveryTime.objects.create(min=1, max=2, unit=DELIVERY_TIME_UNIT_DAYS)

    shop = Shop.objects.create(
        name="Test Shop",
        shop_owner="Test Owner",
        from_email="test@example.com",
        notification_emails="test@example.com",
        description="Test shop description",
        default_country=country,
        delivery_time=delivery_time,
    )
    shop.invoice_countries.add(country)
    shop.shipping_countries.add(country)
    return shop


@pytest.fixture
def comprehensive_property_group_data(db):
    """Comprehensive property group data for workflow testing."""
    property_groups = []

    # Create test data for different property group scenarios
    test_data = [
        {
            "name": "Electronics Properties",
            "position": 10,
            "has_properties": True,
            "has_products": True,
            "property_count": 3,
            "product_count": 2,
        },
        {
            "name": "Clothing Properties",
            "position": 20,
            "has_properties": True,
            "has_products": False,
            "property_count": 2,
            "product_count": 0,
        },
        {
            "name": "Home & Garden Properties",
            "position": 30,
            "has_properties": False,
            "has_products": True,
            "property_count": 0,
            "product_count": 3,
        },
        {
            "name": "Sports Properties",
            "position": 40,
            "has_properties": True,
            "has_products": True,
            "property_count": 4,
            "product_count": 1,
        },
        {
            "name": "Empty Properties",
            "position": 50,
            "has_properties": False,
            "has_products": False,
            "property_count": 0,
            "product_count": 0,
        },
    ]

    # Create properties for testing
    properties = []
    for i in range(10):
        property_obj = Property.objects.create(
            name=f"test_property_{i+1}",
            title=f"Test Property {i+1}",
            type=1,  # Text field
            position=i + 1,
        )
        properties.append(property_obj)

    # Create products for testing
    products = []
    for i in range(10):
        product = Product.objects.create(
            name=f"Test Product {i+1}", slug=f"test-product-{i+1}", price=Decimal(f"{(i+1)*10}.99"), active=True
        )
        products.append(product)

    for i, data in enumerate(test_data):
        # Create property group
        property_group = PropertyGroup.objects.create(name=data["name"], position=data["position"])

        # Create properties for this group
        group_properties = []
        if data["has_properties"]:
            for j in range(data["property_count"]):
                prop = properties[i * 2 + j] if i * 2 + j < len(properties) else properties[j]
                GroupsPropertiesRelation.objects.create(group=property_group, property=prop, position=j + 1)
                group_properties.append(prop)

        # Create products for this group
        group_products = []
        if data["has_products"]:
            for j in range(data["product_count"]):
                product = products[i * 2 + j] if i * 2 + j < len(products) else products[j]
                property_group.products.add(product)
                group_products.append(product)

        property_groups.append(
            {
                "property_group": property_group,
                "properties": group_properties,
                "products": group_products,
                "expected_data": data,
            }
        )

    return property_groups


class TestCompletePropertyGroupManagementWorkflow:
    """Test complete property group management workflow from start to finish."""

    def test_complete_property_group_management_workflow(
        self, client, admin_user, comprehensive_property_group_data, shop
    ):
        """Test complete workflow: login -> list -> create -> edit -> delete."""
        # Step 1: Login
        client.force_login(admin_user)

        # Step 2: View property group list (redirects to first group)
        response = client.get(reverse("lfs_manage_property_groups"))
        assert response.status_code == 302
        assert "property-group" in response.url

        # Step 3: View first property group
        first_group = comprehensive_property_group_data[0]["property_group"]
        response = client.get(reverse("lfs_manage_property_group", kwargs={"id": first_group.id}))
        assert response.status_code == 200
        assert "property_group" in response.context
        assert response.context["property_group"] == first_group

        # Step 4: Create new property group
        response = client.get(reverse("lfs_manage_add_property_group"))
        assert response.status_code == 200

        # Step 5: Submit new property group
        new_group_data = {"name": "New Test Property Group"}
        response = client.post(reverse("lfs_manage_add_property_group"), new_group_data)
        assert response.status_code == 302
        assert "property-group" in response.url

        # Step 6: Verify new property group was created
        new_group = PropertyGroup.objects.get(name="New Test Property Group")
        response = client.get(reverse("lfs_manage_property_group", kwargs={"id": new_group.id}))
        assert response.status_code == 200
        assert response.context["property_group"] == new_group

        # Step 7: Edit property group
        edit_data = {"name": "Updated Property Group Name"}
        response = client.post(reverse("lfs_manage_property_group", kwargs={"id": new_group.id}), edit_data)
        assert response.status_code == 302

        # Step 8: Verify property group was updated
        new_group.refresh_from_db()
        assert new_group.name == "Updated Property Group Name"

        # Step 9: Delete property group
        response = client.get(reverse("lfs_delete_property_group_confirm", kwargs={"id": new_group.id}))
        assert response.status_code == 200
        assert "property_group" in response.context

        # Step 10: Confirm deletion
        response = client.post(reverse("lfs_delete_property_group", kwargs={"id": new_group.id}))
        assert response.status_code == 302
        assert "property-groups" in response.url

        # Step 11: Verify property group was deleted
        assert not PropertyGroup.objects.filter(id=new_group.id).exists()

    def test_property_group_data_management_workflow(self, client, admin_user, comprehensive_property_group_data, shop):
        """Test workflow: edit property group data -> save -> verify changes."""
        client.force_login(admin_user)

        # Step 1: View property group data tab
        property_group = comprehensive_property_group_data[0]["property_group"]
        response = client.get(reverse("lfs_manage_property_group", kwargs={"id": property_group.id}))
        assert response.status_code == 200
        assert response.context["active_tab"] == "data"

        # Step 2: Edit property group name
        original_name = property_group.name
        edit_data = {"name": "Updated Electronics Properties"}
        response = client.post(reverse("lfs_manage_property_group", kwargs={"id": property_group.id}), edit_data)
        assert response.status_code == 302

        # Step 3: Verify property group was updated
        property_group.refresh_from_db()
        assert property_group.name == "Updated Electronics Properties"
        assert property_group.name != original_name

        # Step 4: View updated property group
        response = client.get(reverse("lfs_manage_property_group", kwargs={"id": property_group.id}))
        assert response.status_code == 200
        assert response.context["property_group"].name == "Updated Electronics Properties"

    def test_property_group_products_workflow(self, client, admin_user, comprehensive_property_group_data, shop):
        """Test workflow: view products tab -> assign products -> view assigned -> remove products."""
        client.force_login(admin_user)

        # Step 1: View property group products tab
        property_group = comprehensive_property_group_data[0]["property_group"]
        response = client.get(reverse("lfs_manage_property_group_products", kwargs={"id": property_group.id}))
        assert response.status_code == 200
        assert response.context["active_tab"] == "products"

        # Step 2: Verify initial products
        initial_products = response.context["group_products"]
        assert len(initial_products) == 2  # Based on test data

        # Step 3: Assign new product (this would be done via AJAX in real usage)
        # For testing, we'll directly add a product to the group
        new_product = Product.objects.create(
            name="New Test Product", slug="new-test-product", price=Decimal("99.99"), active=True
        )
        property_group.products.add(new_product)

        # Step 4: View updated products
        response = client.get(reverse("lfs_manage_property_group_products", kwargs={"id": property_group.id}))
        assert response.status_code == 200
        updated_products = response.context["group_products"]
        assert len(updated_products) == 3
        assert new_product in updated_products

        # Step 5: Remove product
        property_group.products.remove(new_product)

        # Step 6: Verify product was removed
        response = client.get(reverse("lfs_manage_property_group_products", kwargs={"id": property_group.id}))
        assert response.status_code == 200
        final_products = response.context["group_products"]
        assert len(final_products) == 2
        assert new_product not in final_products

    def test_property_group_properties_workflow(self, client, admin_user, comprehensive_property_group_data, shop):
        """Test workflow: view properties tab -> assign properties -> view assigned -> remove properties."""
        client.force_login(admin_user)

        # Step 1: View property group properties tab
        property_group = comprehensive_property_group_data[0]["property_group"]
        response = client.get(reverse("lfs_manage_property_group_properties", kwargs={"id": property_group.id}))
        assert response.status_code == 200
        assert response.context["active_tab"] == "properties"

        # Step 2: Verify initial properties
        initial_properties = property_group.properties.all()
        assert len(initial_properties) == 3  # Based on test data

        # Step 3: Assign new property (this would be done via AJAX in real usage)
        new_property = Property.objects.create(
            name="new_test_property",
            title="New Test Property",
            type=1,  # Text field
        )
        GroupsPropertiesRelation.objects.create(group=property_group, property=new_property, position=10)

        # Step 4: View updated properties
        response = client.get(reverse("lfs_manage_property_group_properties", kwargs={"id": property_group.id}))
        assert response.status_code == 200
        updated_properties = property_group.properties.all()
        assert len(updated_properties) == 4
        assert new_property in updated_properties

        # Step 5: Remove property via POST request (simulating form submission)
        response = client.post(
            reverse("lfs_manage_property_group_properties", kwargs={"id": property_group.id}),
            {
                "remove_properties": "1",
                f"property-{new_property.id}": "on",  # Checkbox checked
                "keep-filters": "1",
            },
        )
        assert response.status_code == 302  # Redirect after successful removal

        # Step 6: Verify property was removed
        response = client.get(reverse("lfs_manage_property_group_properties", kwargs={"id": property_group.id}))
        assert response.status_code == 200
        final_properties = property_group.properties.all()
        assert len(final_properties) == 3
        assert new_property not in final_properties

    def test_property_group_remove_properties_with_invalid_data(
        self, client, admin_user, comprehensive_property_group_data, shop
    ):
        """Test workflow: remove properties with invalid data (empty property IDs)."""
        client.force_login(admin_user)

        # Step 1: View property group properties tab
        property_group = comprehensive_property_group_data[0]["property_group"]
        response = client.get(reverse("lfs_manage_property_group_properties", kwargs={"id": property_group.id}))
        assert response.status_code == 200

        # Step 2: Try to remove properties with invalid data (empty property ID)
        response = client.post(
            reverse("lfs_manage_property_group_properties", kwargs={"id": property_group.id}),
            {
                "remove_properties": "1",
                "property-": "on",  # Invalid: empty property ID
                "keep-filters": "1",
            },
        )
        # Should not crash, should redirect successfully
        assert response.status_code == 302

    def test_property_group_remove_products_with_form_submission(
        self, client, admin_user, comprehensive_property_group_data, shop
    ):
        """Test workflow: remove products via form submission."""
        client.force_login(admin_user)

        # Step 1: View property group products tab
        property_group = comprehensive_property_group_data[0]["property_group"]
        response = client.get(reverse("lfs_manage_property_group_products", kwargs={"id": property_group.id}))
        assert response.status_code == 200

        # Step 2: Add a new product to remove later
        new_product = Product.objects.create(
            name="test_remove_product",
            slug="test-remove-product",
            sku="TEST-REMOVE-001",
            price=29.99,
        )
        property_group.products.add(new_product)

        # Step 3: Verify product was added
        response = client.get(reverse("lfs_manage_property_group_products", kwargs={"id": property_group.id}))
        assert response.status_code == 200
        updated_products = property_group.products.all()
        assert new_product in updated_products

        # Step 4: Remove product via POST request (simulating form submission)
        response = client.post(
            reverse("lfs_manage_property_group_products", kwargs={"id": property_group.id}),
            {
                "remove_products": "1",
                f"product-{new_product.id}": "on",  # Checkbox checked
                "keep-filters": "1",
            },
        )
        assert response.status_code == 302  # Redirect after successful removal

        # Step 5: Verify product was removed
        response = client.get(reverse("lfs_manage_property_group_products", kwargs={"id": property_group.id}))
        assert response.status_code == 200
        final_products = property_group.products.all()
        assert new_product not in final_products

    def test_property_group_search_workflow(self, client, admin_user, comprehensive_property_group_data, shop):
        """Test workflow: search property groups -> view results -> clear search."""
        client.force_login(admin_user)

        # Step 1: Search for property groups
        search_query = "Electronics"
        response = client.get(reverse("lfs_manage_property_groups"), {"q": search_query})
        assert response.status_code == 302

        # Step 2: View search results (redirects to first matching group)
        first_group = comprehensive_property_group_data[0]["property_group"]
        response = client.get(reverse("lfs_manage_property_group", kwargs={"id": first_group.id}), {"q": search_query})
        assert response.status_code == 200
        assert response.context["search_query"] == search_query

        # Step 3: Search for non-existent group
        response = client.get(reverse("lfs_manage_property_groups"), {"q": "NonExistent"})
        assert response.status_code == 302
        assert "no-property-groups" in response.url

        # Step 4: View no groups page
        response = client.get(reverse("lfs_manage_no_property_groups"))
        assert response.status_code == 200

    def test_property_group_tab_navigation_workflow(self, client, admin_user, comprehensive_property_group_data, shop):
        """Test workflow: navigate between tabs -> verify tab state persistence."""
        client.force_login(admin_user)

        property_group = comprehensive_property_group_data[0]["property_group"]

        # Step 1: Navigate to data tab
        response = client.get(reverse("lfs_manage_property_group", kwargs={"id": property_group.id}))
        assert response.status_code == 200
        assert response.context["active_tab"] == "data"

        # Step 2: Navigate to products tab
        response = client.get(reverse("lfs_manage_property_group_products", kwargs={"id": property_group.id}))
        assert response.status_code == 200
        assert response.context["active_tab"] == "products"

        # Step 3: Navigate to properties tab
        response = client.get(reverse("lfs_manage_property_group_properties", kwargs={"id": property_group.id}))
        assert response.status_code == 200
        assert response.context["active_tab"] == "properties"

        # Step 4: Navigate back to data tab
        response = client.get(reverse("lfs_manage_property_group", kwargs={"id": property_group.id}))
        assert response.status_code == 200
        assert response.context["active_tab"] == "data"

    def test_property_group_lifecycle_workflow(self, client, admin_user, shop):
        """Test complete property group lifecycle: create -> modify -> view -> delete."""
        client.force_login(admin_user)

        # Step 1: Create a new property group
        response = client.get(reverse("lfs_manage_add_property_group"))
        assert response.status_code == 200

        # Step 2: Submit new property group
        new_group_data = {"name": "Lifecycle Test Property Group"}
        response = client.post(reverse("lfs_manage_add_property_group"), new_group_data)
        assert response.status_code == 302

        # Step 3: Get the created property group
        new_group = PropertyGroup.objects.get(name="Lifecycle Test Property Group")

        # Step 4: Add properties to the group
        property1 = Property.objects.create(
            name="lifecycle_property_1",
            title="Lifecycle Property 1",
            type=1,  # Text field
        )
        property2 = Property.objects.create(
            name="lifecycle_property_2",
            title="Lifecycle Property 2",
            type=1,  # Text field
        )
        GroupsPropertiesRelation.objects.create(group=new_group, property=property1, position=1)
        GroupsPropertiesRelation.objects.create(group=new_group, property=property2, position=2)

        # Step 5: Add products to the group
        product1 = Product.objects.create(
            name="Lifecycle Product 1", slug="lifecycle-1", price=Decimal("25.99"), active=True
        )
        product2 = Product.objects.create(
            name="Lifecycle Product 2", slug="lifecycle-2", price=Decimal("15.50"), active=True
        )
        new_group.products.add(product1, product2)

        # Step 6: View property group with data
        response = client.get(reverse("lfs_manage_property_group", kwargs={"id": new_group.id}))
        assert response.status_code == 200
        assert response.context["property_group"] == new_group

        # Step 7: View products tab
        response = client.get(reverse("lfs_manage_property_group_products", kwargs={"id": new_group.id}))
        assert response.status_code == 200
        group_products = response.context["group_products"]
        assert len(group_products) == 2
        assert product1 in group_products
        assert product2 in group_products

        # Step 8: View properties tab
        response = client.get(reverse("lfs_manage_property_group_properties", kwargs={"id": new_group.id}))
        assert response.status_code == 200
        group_properties = new_group.properties.all()
        assert len(group_properties) == 2
        assert property1 in group_properties
        assert property2 in group_properties

        # Step 9: Modify property group name
        edit_data = {"name": "Updated Lifecycle Property Group"}
        response = client.post(reverse("lfs_manage_property_group", kwargs={"id": new_group.id}), edit_data)
        assert response.status_code == 302

        # Step 10: Verify modification
        new_group.refresh_from_db()
        assert new_group.name == "Updated Lifecycle Property Group"

        # Step 11: Delete property group
        response = client.post(reverse("lfs_delete_property_group", kwargs={"id": new_group.id}))
        assert response.status_code == 302

        # Step 12: Verify property group was deleted
        assert not PropertyGroup.objects.filter(id=new_group.id).exists()

    def test_error_recovery_workflow(self, client, admin_user, comprehensive_property_group_data, shop):
        """Test workflow: encounter error -> recover gracefully -> continue workflow."""
        client.force_login(admin_user)

        # Step 1: Try to access non-existent property group
        response = client.get(reverse("lfs_manage_property_group", kwargs={"id": 99999}))
        assert response.status_code == 404

        # Step 2: Verify system recovers gracefully
        response = client.get(reverse("lfs_manage_property_groups"))
        assert response.status_code == 302

        # Step 3: Access valid property group
        property_group = comprehensive_property_group_data[0]["property_group"]
        response = client.get(reverse("lfs_manage_property_group", kwargs={"id": property_group.id}))
        assert response.status_code == 200

        # Step 4: Try to submit invalid form data
        invalid_data = {"name": ""}  # Empty name should be invalid
        response = client.post(reverse("lfs_manage_property_group", kwargs={"id": property_group.id}), invalid_data)
        # Form validation should show errors, so we expect 200 with form errors
        assert response.status_code == 200

        # Step 5: Verify system still works after error
        response = client.get(reverse("lfs_manage_property_group", kwargs={"id": property_group.id}))
        assert response.status_code == 200

    def test_permission_workflow(self, client, comprehensive_property_group_data, shop):
        """Test workflow: unauthorized access -> login -> authorized access."""
        # Step 1: Try to access without authentication
        response = client.get(reverse("lfs_manage_property_groups"))
        assert response.status_code == 302
        assert "/login/" in response.url

        # Step 2: Create admin user and login
        admin_user = User.objects.create_user(
            username="admin", email="admin@example.com", password="testpass123", is_staff=True, is_superuser=True
        )
        client.force_login(admin_user)

        # Step 3: Access with authentication
        response = client.get(reverse("lfs_manage_property_groups"))
        assert response.status_code == 302

        # Step 4: Access specific property group
        property_group = comprehensive_property_group_data[0]["property_group"]
        response = client.get(reverse("lfs_manage_property_group", kwargs={"id": property_group.id}))
        assert response.status_code == 200
        assert response.context["property_group"] == property_group

    def test_property_group_creation_with_validation_workflow(self, client, admin_user, shop):
        """Test workflow: create property group with validation -> handle errors -> create successfully."""
        client.force_login(admin_user)

        # Step 1: Try to create property group with empty name
        response = client.post(reverse("lfs_manage_add_property_group"), {"name": ""})
        assert response.status_code == 200  # Form validation errors
        assert "name" in response.context["form"].errors

        # Step 2: Try to create property group with name too long
        long_name = "A" * 51  # Exceeds max_length of 50
        response = client.post(reverse("lfs_manage_add_property_group"), {"name": long_name})
        assert response.status_code == 200  # Form validation errors
        assert "name" in response.context["form"].errors

        # Step 3: Create property group with valid name
        valid_data = {"name": "Valid Property Group"}
        response = client.post(reverse("lfs_manage_add_property_group"), valid_data)
        assert response.status_code == 302

        # Step 4: Verify property group was created
        new_group = PropertyGroup.objects.get(name="Valid Property Group")
        assert new_group.name == "Valid Property Group"

    def test_property_group_editing_with_validation_workflow(
        self, client, admin_user, comprehensive_property_group_data, shop
    ):
        """Test workflow: edit property group with validation -> handle errors -> edit successfully."""
        client.force_login(admin_user)

        property_group = comprehensive_property_group_data[0]["property_group"]

        # Step 1: Try to edit with empty name
        response = client.post(reverse("lfs_manage_property_group", kwargs={"id": property_group.id}), {"name": ""})
        assert response.status_code == 200  # Form validation errors
        assert "name" in response.context["form"].errors

        # Step 2: Try to edit with name too long
        long_name = "A" * 51  # Exceeds max_length of 50
        response = client.post(
            reverse("lfs_manage_property_group", kwargs={"id": property_group.id}), {"name": long_name}
        )
        assert response.status_code == 200  # Form validation errors
        assert "name" in response.context["form"].errors

        # Step 3: Edit with valid name
        valid_data = {"name": "Updated Valid Name"}
        response = client.post(reverse("lfs_manage_property_group", kwargs={"id": property_group.id}), valid_data)
        assert response.status_code == 302

        # Step 4: Verify property group was updated
        property_group.refresh_from_db()
        assert property_group.name == "Updated Valid Name"

    def test_property_group_deletion_confirmation_workflow(
        self, client, admin_user, comprehensive_property_group_data, shop
    ):
        """Test workflow: view property group -> confirm deletion -> delete -> verify deletion."""
        client.force_login(admin_user)

        property_group = comprehensive_property_group_data[0]["property_group"]

        # Step 1: View property group
        response = client.get(reverse("lfs_manage_property_group", kwargs={"id": property_group.id}))
        assert response.status_code == 200
        assert response.context["property_group"] == property_group

        # Step 2: Go to delete confirmation
        response = client.get(reverse("lfs_delete_property_group_confirm", kwargs={"id": property_group.id}))
        assert response.status_code == 200
        assert "property_group" in response.context
        assert response.context["property_group"] == property_group

        # Step 3: Confirm deletion
        response = client.post(reverse("lfs_delete_property_group", kwargs={"id": property_group.id}))
        assert response.status_code == 302
        assert "property-groups" in response.url

        # Step 4: Verify property group was deleted
        assert not PropertyGroup.objects.filter(id=property_group.id).exists()

        # Step 5: Try to access deleted property group
        response = client.get(reverse("lfs_manage_property_group", kwargs={"id": property_group.id}))
        assert response.status_code == 404

    def test_property_group_navigation_with_search_workflow(
        self, client, admin_user, comprehensive_property_group_data, shop
    ):
        """Test workflow: search -> navigate between tabs -> maintain search context."""
        client.force_login(admin_user)

        property_group = comprehensive_property_group_data[0]["property_group"]
        search_query = "Electronics"

        # Step 1: Search and navigate to property group
        response = client.get(
            reverse("lfs_manage_property_group", kwargs={"id": property_group.id}), {"q": search_query}
        )
        assert response.status_code == 200
        assert response.context["search_query"] == search_query

        # Step 2: Navigate to products tab with search context
        response = client.get(
            reverse("lfs_manage_property_group_products", kwargs={"id": property_group.id}), {"q": search_query}
        )
        assert response.status_code == 200
        assert response.context["search_query"] == search_query

        # Step 3: Navigate to properties tab with search context
        response = client.get(
            reverse("lfs_manage_property_group_properties", kwargs={"id": property_group.id}), {"q": search_query}
        )
        assert response.status_code == 200
        assert response.context["search_query"] == search_query

        # Step 4: Navigate back to data tab with search context
        response = client.get(
            reverse("lfs_manage_property_group", kwargs={"id": property_group.id}), {"q": search_query}
        )
        assert response.status_code == 200
        assert response.context["search_query"] == search_query
