"""The product management pages, tested through real requests as a shop manager: what each tab stores, which
products it lists, where it redirects, and the messages the manager sees."""

import importlib.util
from urllib.parse import parse_qs, urlparse

import pytest
from django.contrib.messages import get_messages
from django.http import HttpResponse
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from lfs.catalog.models import (
    Image,
    Product,
    ProductAccessories,
    ProductAttachment,
    ProductPropertyValue,
    Property,
    PropertyGroup,
    PropertyOption,
)
from lfs.catalog.settings import (
    CONFIGURABLE_PRODUCT,
    PRODUCT_TYPE_LOOKUP,
    PRODUCT_WITH_VARIANTS,
    PROPERTY_SELECT_FIELD,
    PROPERTY_VALUE_TYPE_DEFAULT,
    PROPERTY_VALUE_TYPE_FILTER,
    STANDARD_PRODUCT,
    VARIANT,
)

# The bulk prices filter uses the optional lfs_bulk_prices add-on.
requires_bulk_prices = pytest.mark.skipif(
    importlib.util.find_spec("lfs_bulk_prices") is None, reason="needs the lfs_bulk_prices add-on"
)

BULK_PRICES = "lfs_bulk_prices.calculator.BulkPricesCalculator"


@pytest.fixture
def manager(client: Client, admin_user) -> Client:
    """A test client logged in as a shop manager."""
    client.force_login(admin_user)
    return client


def messages_of(response: HttpResponse) -> list[str]:
    """Return the messages the request added for the manager."""
    return [str(m) for m in get_messages(response.wsgi_request)]


def set_session(client: Client, **values) -> None:
    """Store ``values`` in the client's session."""
    session = client.session
    session.update(values)
    session.save()


def url(name: str, product: Product) -> str:
    """Return the URL of the product tab ``name``."""
    return reverse(f"lfs_manage_product_{name}", kwargs={"id": product.id})


def form_data(form) -> dict[str, object]:
    """Return the POST data a browser sends for ``form`` unchanged: unchecked checkboxes and empty values left out."""
    data = {}
    for name in form.fields:
        value = form[name].value()
        if value is None or value is False:
            continue
        data[form.add_prefix(name)] = value
    return data


def with_variant(parent_name: str = "Widget Cord", parent_sku: str = "WC-PARENT") -> tuple[Product, Product]:
    """Create a product with variants and one variant without own name and SKU."""
    parent = Product.objects.create(
        name=parent_name, slug=parent_name.lower().replace(" ", "-"), sku=parent_sku, sub_type=PRODUCT_WITH_VARIANTS
    )
    variant = Product.objects.create(
        name="", slug=f"{parent.slug}-v1", sku="", sub_type=VARIANT, parent=parent, active_name=False, active_sku=False
    )
    return parent, variant


def available_ids(response: HttpResponse) -> tuple[list[int], dict[int, list[int]]]:
    """Return the ids of the products offered on an accessories or related tab, and their variants by parent."""
    page = response.context["available_page"]
    return [p.id for p in page.object_list], {p.id: [v.id for v in p.available_variants] for p in page.object_list}


class TestProductsStartPage:
    def test_redirects_to_the_first_product_by_name(self, manager, shop):
        Product.objects.create(name="Zebra", slug="zebra")
        apple = Product.objects.create(name="Apple", slug="apple")

        response = manager.get(reverse("lfs_manage_products"))

        assert response["Location"] == url("data", apple)

    def test_redirects_to_the_no_products_page_without_products(self, manager, shop):
        response = manager.get(reverse("lfs_manage_products"))

        assert response["Location"] == reverse("lfs_manage_no_products")


class TestDataTab:
    def test_variant_gets_the_variant_form(self, manager, variant_product):
        content = manager.get(url("data", variant_product)).content.decode()

        assert 'name="active_name"' in content

    def test_standard_product_gets_the_product_form(self, manager, product):
        content = manager.get(url("data", product)).content.decode()

        assert 'name="active_name"' not in content

    def test_saving_stores_the_data_and_keeps_the_search_query(self, manager, product):
        data = form_data(manager.get(url("data", product)).context["form"])
        data["name"] = "Renamed"

        response = manager.post(url("data", product) + "?q=test", data)

        product.refresh_from_db()
        assert product.name == "Renamed"
        assert response["Location"] == url("data", product) + "?q=test"
        assert messages_of(response) == ["Product data has been saved."]

    def test_saving_keeps_the_search_query_of_the_referring_page(self, manager, product):
        data = form_data(manager.get(url("data", product)).context["form"])

        response = manager.post(
            url("data", product), data, HTTP_REFERER=f"http://testserver{url('data', product)}?q=lamp"
        )

        assert response["Location"] == url("data", product) + "?q=lamp"

    def test_form_action_keeps_the_search_query(self, manager, product):
        content = manager.get(url("data", product) + "?q=test").content.decode()

        assert f'action="{url("data", product)}?q=test"' in content

    def test_variant_links_to_its_base_product(self, manager, variant_product):
        content = manager.get(url("data", variant_product)).content.decode()

        assert "Base Product" in content
        assert url("data", variant_product.parent) in content

    def test_standard_product_has_no_base_product_link(self, manager, product):
        assert "Base Product" not in manager.get(url("data", product)).content.decode()

    def test_view_parameter_opens_the_product_in_the_shop(self, manager, product):
        response = manager.get(url("data", product) + "?view=1")

        assert response["Location"] == reverse("lfs_product", kwargs={"slug": product.slug})

    def test_delete_request_deletes_a_product_and_returns_to_the_products(self, manager, product):
        response = manager.delete(url("data", product))

        assert not Product.objects.filter(pk=product.pk).exists()
        assert response["Location"] == reverse("lfs_manage_products")

    def test_delete_request_on_a_variant_returns_to_its_parent(self, manager, variant_product):
        response = manager.delete(url("data", variant_product))

        assert not Product.objects.filter(pk=variant_product.pk).exists()
        assert response["Location"] == url("data", variant_product.parent)


class TestStockTab:
    def test_saving_stores_the_stock_data(self, manager, product):
        data = form_data(manager.get(url("stock", product)).context["form"])
        data.update({"stock-manage_stock_amount": "on", "stock-stock_amount": "12", "stock-weight": "2.5"})

        response = manager.post(url("stock", product), data)

        product.refresh_from_db()
        assert (product.manage_stock_amount, product.stock_amount, product.weight) == (True, 12, 2.5)
        assert response["Location"] == url("stock", product)
        assert messages_of(response) == ["Product stock data has been saved."]


class TestSEOTab:
    def test_saving_stores_the_meta_data(self, manager, product):
        response = manager.post(
            url("seo", product),
            {
                "active_meta_title": "on",
                "meta_title": "Lamp",
                "meta_keywords": "lamp, light",
                "meta_description": "A lamp",
            },
        )

        product.refresh_from_db()
        assert (product.active_meta_title, product.meta_title, product.meta_keywords) == (True, "Lamp", "lamp, light")
        assert response["Location"] == url("seo", product)
        assert messages_of(response) == ["SEO data has been saved."]

    def test_too_long_meta_title_is_refused(self, manager, product):
        response = manager.post(url("seo", product), {"meta_title": "A" * 201})

        product.refresh_from_db()
        assert product.meta_title != "A" * 201
        assert "meta_title" in response.context["form"].errors


class TestImagesTab:
    def test_toggling_active_images(self, manager, product):
        response = manager.post(url("images", product), {"toggle_active_images": "1", "active_images": "1"})

        product.refresh_from_db()
        assert product.active_images is True
        assert messages_of(response) == ["Active images has been updated."]

    def test_deleting_selected_images(self, manager, product):
        image = Image.objects.create(content=product, title="test.jpg", position=10)

        response = manager.post(url("images", product), {"action": "delete", f"delete-{image.id}": "1"})

        assert not Image.objects.filter(id=image.id).exists()
        assert messages_of(response) == ["Images have been deleted."]

    def test_updating_images_stores_the_title_and_renumbers_the_positions(self, manager, product):
        image = Image.objects.create(content=product, title="old.jpg", position=10)

        manager.post(
            url("images", product), {"action": "update", f"title-{image.id}": "new.jpg", f"position-{image.id}": "20"}
        )

        image.refresh_from_db()
        assert (image.title, image.position) == ("new.jpg", 10)


class TestAttachmentsTab:
    def test_deleting_selected_attachments(self, manager, product):
        attachment = ProductAttachment.objects.create(product=product, title="test.pdf", position=10)

        response = manager.post(url("attachments", product), {"action": "delete", f"delete-{attachment.id}": "1"})

        assert not ProductAttachment.objects.filter(id=attachment.id).exists()
        assert messages_of(response) == ["Attachment has been deleted."]

    def test_updating_attachments(self, manager, product):
        attachment = ProductAttachment.objects.create(product=product, title="old.pdf", position=10, description="old")

        manager.post(
            url("attachments", product),
            {
                "action": "update",
                f"title-{attachment.id}": "new.pdf",
                f"position-{attachment.id}": "20",
                f"description-{attachment.id}": "new",
            },
        )

        attachment.refresh_from_db()
        assert (attachment.title, attachment.position, attachment.description) == ("new.pdf", 10, "new")


class TestAccessoriesTab:
    def test_toggling_active_accessories(self, manager, product):
        response = manager.post(url("accessories", product), {"action": "toggle_active", "active_accessories": "1"})

        product.refresh_from_db()
        assert product.active_accessories is True
        assert messages_of(response) == ["Accessories have been updated."]

    def test_toggling_by_htmx_shows_no_message(self, manager, product):
        response = manager.post(
            url("accessories", product), {"action": "toggle_active", "active_accessories": "1"}, HTTP_HX_REQUEST="true"
        )

        product.refresh_from_db()
        assert product.active_accessories is True
        assert messages_of(response) == []

    def test_adding_accessories(self, manager, product):
        accessory = Product.objects.create(name="Accessory", slug="accessory")

        response = manager.post(url("accessories", product), {"action": "add", f"product-{accessory.id}": "1"})

        assert ProductAccessories.objects.filter(product=product, accessory=accessory).exists()
        assert messages_of(response) == ["Accessories have been added."]

    def test_removing_accessories(self, manager, product):
        accessory = Product.objects.create(name="Accessory", slug="accessory")
        ProductAccessories.objects.create(product=product, accessory=accessory, position=10)

        response = manager.post(url("accessories", product), {"action": "remove", f"accessory-{accessory.id}": "1"})

        assert not ProductAccessories.objects.filter(product=product, accessory=accessory).exists()
        assert messages_of(response) == ["Accessories have been removed."]

    def test_saving_quantities_and_renumbering_positions(self, manager, product):
        accessory = Product.objects.create(name="Accessory", slug="accessory")
        pa = ProductAccessories.objects.create(product=product, accessory=accessory, position=10, quantity=1)

        manager.post(
            url("accessories", product),
            {"action": "save", f"quantity-{accessory.id}": "5", f"position-{accessory.id}": "20"},
        )

        pa.refresh_from_db()
        assert (pa.quantity, pa.position) == (5, 10)

    def test_filter_limits_the_offered_products(self, manager, product):
        apple = Product.objects.create(name="Apple Product", slug="apple-product")
        Product.objects.create(name="Banana Product", slug="banana-product")

        top_level, _ = available_ids(manager.get(url("accessories", product) + "?filter=apple"))

        assert top_level == [apple.id]

    @pytest.mark.parametrize("search", ["", "Widget", "WIDGET-99"])
    def test_variants_are_offered_under_their_parent(self, manager, product, search):
        parent, variant = with_variant(parent_sku="SKU-WIDGET-99")

        top_level, variants = available_ids(manager.get(url("accessories", product) + f"?filter={search}"))

        assert parent.id in top_level
        assert variant.id not in top_level
        assert variants[parent.id] == [variant.id]


class TestRelatedProductsTab:
    def test_toggling_active_related_products(self, manager, product):
        response = manager.post(url("related", product), {"action": "toggle_active", "active_related_products": "1"})

        product.refresh_from_db()
        assert product.active_related_products is True
        assert messages_of(response) == ["Related products have been updated."]

    def test_toggling_by_htmx_shows_no_message(self, manager, product):
        response = manager.post(
            url("related", product), {"action": "toggle_active", "active_related_products": "1"}, HTTP_HX_REQUEST="true"
        )

        product.refresh_from_db()
        assert product.active_related_products is True
        assert messages_of(response) == []

    def test_adding_related_products(self, manager, product):
        related = Product.objects.create(name="Related", slug="related")

        response = manager.post(url("related", product), {"action": "add", f"product-{related.id}": "1"})

        assert product.related_products.filter(pk=related.pk).exists()
        assert messages_of(response) == ["Related products have been added."]

    def test_removing_related_products(self, manager, product):
        related = Product.objects.create(name="Related", slug="related")
        product.related_products.add(related)

        response = manager.post(url("related", product), {"action": "remove", f"product-{related.id}": "1"})

        assert not product.related_products.filter(pk=related.pk).exists()
        assert messages_of(response) == ["Related products have been removed."]

    def test_lists_the_related_products_by_name(self, manager, product):
        second = Product.objects.create(name="Related 2", slug="related-2")
        first = Product.objects.create(name="Related 1", slug="related-1")
        product.related_products.add(second, first)

        response = manager.get(url("related", product))

        assert list(response.context["related_products"]) == [first, second]

    def test_offers_neither_the_product_itself_nor_products_already_related(self, manager, product):
        related = Product.objects.create(name="Related", slug="related")
        other = Product.objects.create(name="Other", slug="other")
        product.related_products.add(related)

        top_level, _ = available_ids(manager.get(url("related", product)))

        assert top_level == [other.id]

    def test_filter_limits_the_offered_products(self, manager, product):
        apple = Product.objects.create(name="Apple Product", slug="apple-product")
        Product.objects.create(name="Banana Product", slug="banana-product")

        top_level, _ = available_ids(manager.get(url("related", product) + "?filter=apple"))

        assert top_level == [apple.id]

    @pytest.mark.parametrize("search", ["", "Widget", "WIDGET-99"])
    def test_variants_are_offered_under_their_parent(self, manager, product, search):
        parent, variant = with_variant(parent_sku="SKU-WIDGET-99")

        top_level, variants = available_ids(manager.get(url("related", product) + f"?filter={search}"))

        assert parent.id in top_level
        assert variant.id not in top_level
        assert variants[parent.id] == [variant.id]


class TestVariantsTab:
    def test_deleting_the_default_variant_clears_the_default(self, manager, product):
        variant = Product.objects.create(name="Variant", slug="variant", parent=product, sub_type=VARIANT)
        product.default_variant = variant
        product.save()

        response = manager.post(url("variants", product), {"action": "delete", f"delete-{variant.id}": "1"})

        assert not Product.objects.filter(id=variant.id).exists()
        product.refresh_from_db()
        assert product.default_variant_id is None
        assert messages_of(response) == ["Variants have been deleted."]

    def test_updating_variants_stores_their_data_and_the_default_variant(self, manager, product):
        variant = Product.objects.create(name="Variant", slug="variant", sku="VAR001", parent=product, sub_type=VARIANT)

        response = manager.post(
            url("variants", product),
            {
                "action": "update",
                f"variant-{variant.id}": "1",
                f"name-{variant.id}": "Updated Variant",
                f"sku-{variant.id}": "UPD001",
                f"price-{variant.id}": "15.0",
                f"active-{variant.id}": "1",
                f"active_price-{variant.id}": "1",
                f"active_sku-{variant.id}": "1",
                f"active_name-{variant.id}": "1",
                f"position-{variant.id}": "20",
                "default_variant": str(variant.id),
            },
        )

        variant.refresh_from_db()
        assert (variant.name, variant.sku, variant.price) == ("Updated Variant", "UPD001", 15.0)
        assert variant.active and variant.active_price and variant.active_sku and variant.active_name
        assert variant.variant_position == 10
        product.refresh_from_db()
        assert product.default_variant_id == variant.id
        assert messages_of(response) == ["Variants have been saved."]

    def test_adding_variants_creates_one_per_option_with_slug_and_properties(self, manager, product):
        group = PropertyGroup.objects.create(name="Group")
        colour = Property.objects.create(name="Colour", title="Colour", type=PROPERTY_SELECT_FIELD, variants=True)
        group.properties.add(colour)
        red = PropertyOption.objects.create(name="Red", property=colour)
        blue = PropertyOption.objects.create(name="Blue", property=colour)
        product.property_groups.add(group)

        response = manager.post(
            url("variants", product), {"action": "add_variants", f"property_{group.id}_{colour.id}": "all"}
        )

        variants = Product.objects.filter(parent=product).order_by("variant_position")
        assert [v.slug for v in variants] == [f"{product.slug}-red", f"{product.slug}-blue"]
        assert [v.sku for v in variants] == [f"{product.sku}-1", f"{product.sku}-2"]
        values = ProductPropertyValue.objects.filter(product__in=variants, property=colour)
        assert sorted(v.value for v in values) == sorted([str(red.id), str(blue.id)])
        assert messages_of(response) == ["Variants have been added."]

    def test_added_variant_gets_a_unique_slug(self, manager, product):
        group = PropertyGroup.objects.create(name="Group")
        colour = Property.objects.create(name="Colour", title="Colour", type=PROPERTY_SELECT_FIELD, variants=True)
        group.properties.add(colour)
        red = PropertyOption.objects.create(name="Red", property=colour)
        product.property_groups.add(group)
        Product.objects.create(name="Taken", slug=f"{product.slug}-red")

        manager.post(
            url("variants", product), {"action": "add_variants", f"property_{group.id}_{colour.id}": str(red.id)}
        )

        assert Product.objects.get(parent=product).slug == f"{product.slug}-red-1"

    def test_changing_the_display_type(self, manager, product):
        response = manager.post(url("variants", product), {"action": "edit_sub_type", "variants_display_type": "1"})

        product.refresh_from_db()
        assert product.variants_display_type == 1
        assert messages_of(response) == ["Sub type has been saved."]

    def test_assigning_property_groups(self, manager, product):
        group = PropertyGroup.objects.create(name="Group")

        response = manager.post(
            url("variants", product), {"action": "update_property_groups", "selected-property-groups": [str(group.id)]}
        )

        assert group.products.filter(pk=product.pk).exists()
        assert messages_of(response) == ["Property groups have been updated."]

    def test_links_each_variant_to_its_management_and_shop_page(self, manager, product):
        variant = Product.objects.create(parent=product, name="Variant", slug="variant", sub_type=VARIANT)

        content = manager.get(url("variants", product)).content.decode()

        assert url("data", variant) in content
        assert url("data", variant) + "?view=1" in content


class TestPropertiesTab:
    def test_marks_the_assigned_property_groups(self, manager, product):
        assigned = PropertyGroup.objects.create(name="Assigned")
        PropertyGroup.objects.create(name="Other")
        product.property_groups.add(assigned)

        groups = manager.get(url("properties", product)).context["shop_property_groups"]

        assert [g["name"] for g in groups if g["selected"]] == ["Assigned"]

    def test_updating_property_groups_assigns_the_selected_and_removes_the_others(self, manager, product):
        selected = PropertyGroup.objects.create(name="Selected")
        removed = PropertyGroup.objects.create(name="Removed")
        product.property_groups.add(removed)

        response = manager.post(
            url("properties", product),
            {"action": "update_property_groups", "selected-property-groups": [str(selected.id)]},
        )

        assert list(product.property_groups.all()) == [selected]
        assert response["Location"] == url("properties", product)
        assert messages_of(response) == ["Property groups have been updated."]

    def test_updating_a_property_stores_its_value(self, manager, product):
        group = PropertyGroup.objects.create(name="Group")
        prop = Property.objects.create(name="Colour", title="Colour", type=PROPERTY_SELECT_FIELD)
        option = PropertyOption.objects.create(name="Red", property=prop)
        product.property_groups.add(group)

        response = manager.post(
            url("properties", product),
            {
                "action": "update_properties",
                "type": str(PROPERTY_VALUE_TYPE_DEFAULT),
                f"property-{group.id}-{prop.id}": [str(option.id)],
            },
        )

        values = ProductPropertyValue.objects.filter(product=product, property=prop, type=PROPERTY_VALUE_TYPE_DEFAULT)
        assert [v.value for v in values] == [str(option.id)]
        assert response["Location"] == url("properties", product)
        assert messages_of(response) == ["Properties have been updated."]

    def test_a_filterable_property_stores_several_values(self, manager, product):
        group = PropertyGroup.objects.create(name="Group")
        prop = Property.objects.create(name="Colour", title="Colour", type=PROPERTY_SELECT_FIELD, filterable=True)
        red = PropertyOption.objects.create(name="Red", property=prop)
        blue = PropertyOption.objects.create(name="Blue", property=prop)
        product.property_groups.add(group)

        manager.post(
            url("properties", product),
            {
                "action": "update_properties",
                "type": str(PROPERTY_VALUE_TYPE_FILTER),
                f"property-{group.id}-{prop.id}": [str(red.id), str(blue.id)],
            },
        )

        values = ProductPropertyValue.objects.filter(product=product, property=prop, type=PROPERTY_VALUE_TYPE_FILTER)
        assert sorted(v.value for v in values) == sorted([str(red.id), str(blue.id)])


class TestDeleteProduct:
    def test_confirmation_page_names_the_product(self, manager, product):
        response = manager.get(reverse("lfs_manage_delete_product_confirm", kwargs={"id": product.id}))

        assert response.context["product"] == product

    def test_deleting_returns_to_the_product_list(self, manager, product):
        response = manager.post(reverse("lfs_manage_delete_product", kwargs={"id": product.id}))

        assert not Product.objects.filter(id=product.id).exists()
        assert response["Location"] == reverse("lfs_manage_products_list")
        assert messages_of(response) == ["Product has been deleted."]


class TestProductFilters:
    def test_applying_filters_in_the_list_stores_them_and_returns_to_the_list(self, manager, shop):
        response = manager.post(reverse("lfs_apply_product_filters_list"), {"name": " Apple ", "status": "active"})

        assert manager.session["product-filters"] == {"name": "Apple", "status": "active"}
        assert response["Location"] == reverse("lfs_manage_products_list")

    def test_applying_filters_on_a_product_returns_to_the_product(self, manager, product):
        response = manager.post(reverse("lfs_apply_product_filters", kwargs={"id": product.id}), {"name": "Apple"})

        assert response["Location"] == url("data", product)

    def test_applying_filters_changes_only_the_submitted_fields(self, manager, product):
        set_session(manager, **{"product-filters": {"name": "Apple", "sku": "APP001", "sub_type": "0"}})

        manager.post(
            reverse("lfs_apply_product_filters", kwargs={"id": product.id}), {"sub_type": "", "status": "active"}
        )

        assert manager.session["product-filters"] == {"name": "Apple", "sku": "APP001", "status": "active"}

    def test_applying_filters_keeps_the_search_query(self, manager, product):
        response = manager.post(
            reverse("lfs_apply_product_filters", kwargs={"id": product.id}), {"sub_type": "0", "q": "Apple"}
        )

        location = urlparse(response["Location"])
        assert (location.path, parse_qs(location.query)) == (url("data", product), {"q": ["Apple"]})

    def test_invalid_filters_are_refused_with_a_message(self, manager, shop):
        response = manager.post(reverse("lfs_apply_product_filters_list"), {"sub_type": "no-such-type"})

        assert "product-filters" not in manager.session
        assert messages_of(response) == ["Invalid filter data."]

    def test_resetting_filters_clears_them_and_keeps_the_search_query(self, manager, product):
        set_session(manager, **{"product-filters": {"name": "Apple"}})

        response = manager.get(reverse("lfs_reset_product_filters", kwargs={"id": product.id}) + "?q=Apple")

        assert "product-filters" not in manager.session
        location = urlparse(response["Location"])
        assert (location.path, parse_qs(location.query)) == (url("data", product), {"q": ["Apple"]})

    def test_resetting_filters_without_filters_returns_to_the_list(self, manager, shop):
        response = manager.get(reverse("lfs_reset_product_filters_list"))

        assert response["Location"] == reverse("lfs_manage_products_list")


class TestProductSidebar:
    """The product list beside each product tab follows the search query and the stored filters."""

    def sidebar(self, manager: Client, product: Product, query: str = "") -> list[str]:
        """Return the names of the products in the sidebar of the data tab."""
        return [p.name for p in manager.get(url("data", product) + query).context["products"]]

    def test_filters_by_the_stored_product_type(self, manager, product):
        Product.objects.create(name="With Variants", slug="with-variants", sub_type=PRODUCT_WITH_VARIANTS)
        Product.objects.create(name="Configurable", slug="configurable", sub_type=CONFIGURABLE_PRODUCT)

        set_session(manager, **{"product-filters": {"sub_type": STANDARD_PRODUCT}})
        assert self.sidebar(manager, product) == [product.name]
        set_session(manager, **{"product-filters": {"sub_type": CONFIGURABLE_PRODUCT}})
        assert self.sidebar(manager, product) == ["Configurable"]

    @requires_bulk_prices
    def test_filters_by_the_stored_price_calculator(self, manager, product):
        Product.objects.create(name="Bulk", slug="bulk", price_calculator=BULK_PRICES)
        set_session(manager, **{"product-filters": {"price_calculator": BULK_PRICES}})

        assert self.sidebar(manager, product) == ["Bulk"]

    def test_combines_the_search_query_with_the_stored_filters(self, manager, shop):
        apple = Product.objects.create(name="Apple Standard", slug="apple-standard", sub_type=STANDARD_PRODUCT)
        Product.objects.create(name="Banana Standard", slug="banana-standard", sub_type=STANDARD_PRODUCT)
        Product.objects.create(name="Apple Configurable", slug="apple-configurable", sub_type=CONFIGURABLE_PRODUCT)
        set_session(manager, **{"product-filters": {"sub_type": STANDARD_PRODUCT}})

        assert self.sidebar(manager, apple, "?q=Apple") == ["Apple Standard"]

    def test_filter_form_shows_the_stored_filters(self, manager, product):
        set_session(manager, **{"product-filters": {"sub_type": "0", "status": "active"}})

        form = manager.get(url("data", product)).context["filter_form"]

        assert (form.initial["sub_type"], form.initial["status"]) == ("0", "active")


class TestProductList:
    def list_page(self, manager: Client, query: str = "") -> HttpResponse:
        """Return the product list page."""
        return manager.get(reverse("lfs_manage_products_list") + query)

    def test_is_linked_in_the_catalog_menu(self, manager, product):
        content = manager.get(url("data", product)).content.decode()

        assert f'href="{reverse("lfs_manage_products_list")}"' in content

    def test_shows_categories_price_stock_and_type_of_each_product(self, manager, category, shop):
        product = Product.objects.create(
            name="Shown", slug="shown", price=10.0, active=True, manage_stock_amount=True, stock_amount=5
        )
        product.categories.add(category)

        [row] = self.list_page(manager).context["products_with_data"]

        assert row["product"] == product
        assert row["categories"] == "Test Category"
        assert (row["price"], row["stock"], row["active"]) == (10.0, 5, True)
        assert row["sub_type_display"] == PRODUCT_TYPE_LOOKUP[product.sub_type]

    def test_hides_the_stock_when_it_is_not_managed(self, manager, shop):
        Product.objects.create(name="Unmanaged", slug="unmanaged", manage_stock_amount=False, stock_amount=5)

        [row] = self.list_page(manager).context["products_with_data"]

        assert row["stock"] is None

    def test_shows_at_most_three_categories(self, manager, product):
        from lfs.catalog.models import Category

        for i in range(5):
            product.categories.add(Category.objects.create(name=f"Category {i}", slug=f"category-{i}"))

        [row] = self.list_page(manager).context["products_with_data"]

        assert len(row["categories"].split(", ")) == 3

    def test_applies_the_stored_filters(self, manager, shop):
        apple = Product.objects.create(name="Apple Product", slug="apple-product")
        Product.objects.create(name="Banana Product", slug="banana-product")
        set_session(manager, **{"product-filters": {"name": "Apple"}})

        rows = self.list_page(manager).context["products_with_data"]

        assert [r["product"] for r in rows] == [apple]

    def test_shows_22_products_per_page_newest_first(self, manager, shop):
        now = timezone.now()
        for i in range(25):
            product = Product.objects.create(name=f"Product {i}", slug=f"product-{i}")
            Product.objects.filter(pk=product.pk).update(creation_date=now - timezone.timedelta(days=i))

        first = self.list_page(manager).context["products_with_data"]
        second = self.list_page(manager, "?page=2").context["products_with_data"]

        assert [r["product"].name for r in first] == [f"Product {i}" for i in range(22)]
        assert [r["product"].name for r in second] == ["Product 22", "Product 23", "Product 24"]

    def test_lists_no_variants(self, manager, variant_product):
        rows = self.list_page(manager).context["products_with_data"]

        assert [r["product"] for r in rows] == [variant_product.parent]

    def test_filter_form_shows_the_stored_filters(self, manager, shop):
        set_session(manager, **{"product-filters": {"name": "test name", "sku": "test sku", "status": "active"}})

        form = self.list_page(manager).context["filter_form"]

        assert (form.initial["name"], form.initial["sku"], form.initial["status"]) == (
            "test name",
            "test sku",
            "active",
        )
