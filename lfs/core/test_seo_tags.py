"""lfs_seo_tags: absolute URLs, image sizes and the ProductGroup JSON-LD of product variants."""

import json
from io import BytesIO

import pytest
from django.core.files.base import ContentFile
from django.core.management import call_command
from django.template import Context, Template
from django.test import RequestFactory
from PIL import Image as PILImage

from lfs.catalog.models import Image, Product, ProductPropertyValue, Property, PropertyGroup, PropertyOption
from lfs.catalog.settings import PRODUCT_WITH_VARIANTS, PROPERTY_SELECT_FIELD, PROPERTY_VALUE_TYPE_VARIANT, VARIANT
from lfs.core.models import Country
from lfs.core.templatetags.lfs_seo_tags import (
    image_size,
    merchant_return_policy,
    own_sku,
    thumbnail_size,
    variant_aspect,
    variant_name,
)
from lfs.core.utils import get_default_shop
from lfs.manufacturer.models import Manufacturer


def png(width, height):
    """Return a PNG of the given size as an uploadable file."""
    buffer = BytesIO()
    PILImage.new("RGB", (width, height)).save(buffer, "PNG")
    return ContentFile(buffer.getvalue())


def render(source, **context):
    """Render a template snippet that loads lfs_seo_tags."""
    request = RequestFactory().get("/")
    return Template("{% load lfs_seo_tags %}" + source).render(Context({"request": request, **context}))


@pytest.fixture
def shop(db):
    """The default shop, which saving products needs."""
    call_command("loaddata", "lfs_shop.xml", verbosity=0)


@pytest.fixture
def parent(shop):
    """A deck board with two length variants; only the second has its own SKU."""
    parent = Product.objects.create(name="Terrassendiele", slug="diele", sku="07-006", active=True, price=20,
                                    sub_type=PRODUCT_WITH_VARIANTS)
    length = Property.objects.create(name="Länge", title="Länge", type=PROPERTY_SELECT_FIELD, variants=True)
    group = PropertyGroup.objects.create(name="Längen")
    group.products.add(parent)
    for position, value in enumerate(["2,15 m", "2,44 m"]):
        option = PropertyOption.objects.create(property=length, name=value)
        variant = Product.objects.create(slug=f"diele-{position}", sub_type=VARIANT, parent=parent, active=True,
                                         variant_position=position, active_price=True, price=22 + position,
                                         sku="07-006-244" if position else "", active_sku=bool(position))
        ProductPropertyValue.objects.create(product=variant, property=length, property_group=group,
                                            value=str(option.id), type=PROPERTY_VALUE_TYPE_VARIANT)
    return parent


def test_absolute_urls_use_the_request_host():
    assert render("{% absolute_uri request '/media/a.png' %}") == "http://testserver/media/a.png"
    assert render("{% absolute_static request 'img/a.jpg' %}").startswith("http://testserver/static/img/a")


def test_image_and_thumbnail_sizes_and_missing_files(shop, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    product = Product.objects.create(name="Diele", slug="d", active=True, price=1)
    image = Image(content=product, title="Diele", position=0)
    image.image.save("diele.png", png(800, 600))
    assert image_size(image.image) == (800, 600)
    assert thumbnail_size(image.image, "200x200") == (200, 150)
    assert image_size(None) is None and thumbnail_size(None, "200x200") is None
    (tmp_path / image.image.name).unlink()
    # Fresh from the database: a field file keeps the dimensions it has read once.
    assert image_size(Image.objects.get(pk=image.pk).image) is None


@pytest.mark.parametrize(("title", "aspect"), [
    ("Länge", "size"), ("Höhe in cm", "size"), ("Farbe", "color"), ("Holzart", "material"), ("Ausführung", None),
])
def test_variant_aspect_maps_property_titles_to_schema_org(title, aspect):
    assert variant_aspect(title) == aspect


def test_variants_are_named_by_their_properties_and_keep_only_their_own_sku(parent):
    first, second = parent.get_variants()
    assert variant_name(first) == "Terrassendiele – Länge 2,15 m"
    assert own_sku(first) == "" and own_sku(second) == "07-006-244"
    assert own_sku(parent) == "07-006"


def test_product_group_lists_all_variants_and_references_the_shown_one(parent):
    first, second = parent.get_variants()
    group = json.loads(render("{% product_group_json product %}", product=first))
    assert group["@type"] == "ProductGroup"
    assert group["url"] == "https://testserver/product/diele/"
    assert group["productGroupID"] == "07-006"
    assert group["variesBy"] == ["https://schema.org/size"]
    shown, other = group["hasVariant"]
    assert shown == {"@id": "https://testserver/product/diele-0/#product", "size": "2,15 m"}
    assert other["sku"] == "07-006-244" and other["offers"]["price"] == "23.00"


def test_product_without_variants_has_no_group(parent):
    assert render("{% product_group_json product %}", product=parent) == ""


def test_other_variants_show_the_parent_image_without_an_own_one(parent, settings, tmp_path):
    # Google rejects a variant Product with an offer but without image as invalid.
    settings.MEDIA_ROOT = tmp_path
    Image(content=parent, title="Diele", position=0).image.save("diele.png", png(800, 600))
    first, _ = parent.get_variants()
    other = json.loads(render("{% product_group_json product %}", product=first))["hasVariant"][1]
    assert other["image"].startswith("https://testserver/media/") and ".400x400." in other["image"]


def test_other_variants_show_the_parent_short_description_without_an_own_one(parent):
    parent.short_description = "<p>Lärche, <b>glatt</b></p>"
    parent.save()
    first, _ = parent.get_variants()
    other = json.loads(render("{% product_group_json product %}", product=first))["hasVariant"][1]
    assert other["description"] == "Lärche, glatt"


def test_other_variants_have_the_brand_of_the_parent_manufacturer(parent):
    parent.manufacturer = Manufacturer.objects.create(name="Holzmüller", slug="holzmueller")
    parent.save()
    first, _ = parent.get_variants()
    other = json.loads(render("{% product_group_json product %}", product=first))["hasVariant"][1]
    assert other["brand"] == {"@type": "Brand", "name": "Holzmüller"}


@pytest.fixture
def returns(shop):
    """The shop ships to Germany and Austria and takes products back by mail within 14 days for free."""
    shop = get_default_shop()
    shop.shipping_countries.set(
        [Country.objects.get_or_create(code=code, defaults={"name": code})[0] for code in ("de", "at")]
    )
    shop.return_policy_url = "/page/widerrufsbelehrung/"
    shop.save()
    return shop


def test_return_policy_comes_from_the_shop(returns):
    policy = merchant_return_policy(RequestFactory().get("/"))
    assert policy == {
        "@type": "MerchantReturnPolicy",
        "applicableCountry": ["AT", "DE"],
        "returnPolicyCategory": "https://schema.org/MerchantReturnFiniteReturnWindow",
        "merchantReturnDays": 14,
        "returnMethod": "https://schema.org/ReturnByMail",
        "returnFees": "https://schema.org/FreeReturn",
        "refundType": "https://schema.org/FullRefund",
        "merchantReturnLink": "https://testserver/page/widerrufsbelehrung/",
    }


def test_shop_without_returns_says_so(returns):
    returns.return_days = 0
    returns.save()
    policy = merchant_return_policy(RequestFactory().get("/"))
    assert policy == {
        "@type": "MerchantReturnPolicy",
        "applicableCountry": ["AT", "DE"],
        "returnPolicyCategory": "https://schema.org/MerchantReturnNotPermitted",
    }


def test_other_variants_offer_the_shop_return_policy(parent, returns):
    first, _ = parent.get_variants()
    other = json.loads(render("{% product_group_json product %}", product=first))["hasVariant"][1]
    assert other["offers"]["hasMerchantReturnPolicy"]["merchantReturnDays"] == 14


def test_return_policy_tag_renders_json_for_the_themes(returns):
    policy = json.loads(render("{% merchant_return_policy_json %}"))
    assert policy["returnFees"] == "https://schema.org/FreeReturn"


def test_shop_without_a_return_policy_page_claims_no_return_policy(parent):
    """Until the shop names its return policy page, LFS does not tell search engines "free return in 14 days"."""
    assert get_default_shop().return_policy_url == ""
    first, _ = parent.get_variants()

    assert merchant_return_policy(RequestFactory().get("/")) is None
    assert json.loads(render("{% merchant_return_policy_json %}")) is None
    other = json.loads(render("{% product_group_json product %}", product=first))["hasVariant"][1]
    assert "hasMerchantReturnPolicy" not in other["offers"]


def test_product_group_has_the_parent_short_description(parent):
    parent.short_description = "<p>Lärche, <b>glatt</b></p>"
    parent.save()
    first, _ = parent.get_variants()
    group = json.loads(render("{% product_group_json product %}", product=first))
    assert group["description"] == "Lärche, glatt"
