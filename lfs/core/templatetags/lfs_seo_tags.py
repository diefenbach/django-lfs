"""Template tags for search engines: absolute URLs, image sizes and JSON-LD for product variants.

Theme-independent, so that every theme gets them with ``{% load lfs_seo_tags %}``.
"""

import json

from django.core.files.images import get_image_dimensions
from django.template import Library
from django.templatetags.static import static
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

from lfs.core.utils import get_default_shop

register = Library()


@register.simple_tag
def absolute_uri(request, path):
    """Return the absolute URL of a path on this site, e.g. a media file for og:image."""
    return request.build_absolute_uri(path)


@register.simple_tag
def absolute_static(request, path):
    """Return the absolute URL of a static file, e.g. for og:image, which must not be relative."""
    return request.build_absolute_uri(static(path))


@register.filter
def thumbnail_size(image, size):
    """Return (width, height) of the stored thumbnail of ``image`` for ``size``, e.g. "200x200".

    LFS scales thumbnails into the size as a bounding box, so a landscape image is 200x133; the real
    size is read from the thumbnail file's header. Returns None without an image or thumbnail file.
    """
    if not image:
        return None
    base, extension = image.name.rsplit(".", 1)
    try:
        with image.storage.open(f"{base}.{size}.{extension}") as thumbnail:
            width, height = get_image_dimensions(thumbnail)
    except FileNotFoundError:
        return None
    return (width, height) if width and height else None


@register.filter
def image_size(image):
    """Return (width, height) of ``image``, or None without an image or image file.

    ``image.width`` opens the file and raises if it is missing, which would break the whole page.
    """
    if not image:
        return None
    try:
        width, height = image.width, image.height
    except OSError:
        return None
    return (width, height) if width and height else None


# Google supports only these schema.org properties in ProductGroup.variesBy; LFS property titles are
# free text, so they are matched by keyword. Properties without a match still name the variant.
VARIANT_ASPECTS = (
    ("size", ("länge", "höhe", "größe", "breite", "stärke", "dicke", "format", "maß")),
    ("color", ("farbe", "lasur")),
    ("material", ("holzart", "material")),
)


def variant_aspect(title):
    """Return the schema.org property ("size", "color", "material") for an LFS property title, or None."""
    lowered = title.lower()
    for aspect, keywords in VARIANT_ASPECTS:
        if any(keyword in lowered for keyword in keywords):
            return aspect
    return None


def _property_text(prop):
    """Return a variant property's value with its unit, e.g. "2,15 m"."""
    return f"{prop['value']} {prop['unit']}".strip()


@register.filter
def variant_name(product):
    """Return the product name, for a variant followed by its properties, e.g. "Diele – Länge 2,15 m".

    Google asks for variant names more specific than the group name; LFS variants usually inherit the
    parent's name. A variant with its own name keeps it.
    """
    if not product.is_variant() or product.active_name:
        return product.get_name()
    properties = ", ".join(f"{prop['title']} {_property_text(prop)}" for prop in product.get_variant_properties())
    return f"{product.get_name()} – {properties}" if properties else product.get_name()


@register.filter
def own_sku(product):
    """Return the product's SKU, for a variant only if it has its own.

    LFS variants without an active SKU inherit the parent's, which is the ProductGroup's ID; as a
    variant sku it would not tell the variants apart.
    """
    if product.is_variant() and not product.active_sku:
        return ""
    return product.get_sku()


def _aspects(variant):
    """Return the variant's schema.org aspects, e.g. {"size": "2,15 m"}."""
    aspects = {}
    for prop in variant.get_variant_properties():
        aspect = variant_aspect(prop["title"])
        if aspect:
            aspects[aspect] = ", ".join(filter(None, (aspects.get(aspect), _property_text(prop))))
    return aspects


def _json(data):
    """Return ``data`` as JSON for a script element; "<" is escaped so that no value can close it."""
    return mark_safe(json.dumps(data, ensure_ascii=False, indent=4).replace("<", "\\u003c"))


def merchant_return_policy(request):
    """Return the shop's schema.org MerchantReturnPolicy for product offers.

    Google expects it in every offer of a merchant listing, including the variants of a ProductGroup.
    The countries are the shop's shipping countries.
    """
    shop = get_default_shop(request)
    policy = {
        "@type": "MerchantReturnPolicy",
        "applicableCountry": sorted(country.code.upper() for country in shop.shipping_countries.all()),
    }
    if not shop.return_days:
        policy["returnPolicyCategory"] = "https://schema.org/MerchantReturnNotPermitted"
        return policy
    policy.update({
        "returnPolicyCategory": "https://schema.org/MerchantReturnFiniteReturnWindow",
        "merchantReturnDays": shop.return_days,
        "returnMethod": f"https://schema.org/{shop.return_method}",
        "returnFees": f"https://schema.org/{shop.return_fees}",
        # The statutory right of withdrawal refunds the full price.
        "refundType": "https://schema.org/FullRefund",
    })
    link = shop.return_policy_url
    if link:
        # Like the other URLs here always https, which request.build_absolute_uri behind a proxy is not.
        policy["merchantReturnLink"] = f"https://{request.get_host()}{link}" if link.startswith("/") else link
    return policy


@register.simple_tag(takes_context=True)
def merchant_return_policy_json(context):
    """Return the shop's MerchantReturnPolicy as JSON, for the offer of a theme's Product block."""
    return _json(merchant_return_policy(context["request"]))


@register.simple_tag(takes_context=True)
def product_group_json(context, product):
    """Return the JSON-LD ProductGroup of a variant's parent with all its variants, or "" for other products.

    The shown variant is only referenced by @id: its full Product block is on the page. The others get
    name, URL, SKU, aspects and offer, so the page describes the whole group as Google's single-page
    variant model expects (one canonical URL for the group, a distinct URL per variant).
    """
    if not product.is_variant():
        return ""
    request = context["request"]
    base = f"https://{request.get_host()}"
    parent = product.parent
    variants = list(parent.get_variants())
    return_policy = merchant_return_policy(request)
    entries = []
    aspects_seen = []
    for variant in variants:
        url = f"{base}{variant.get_absolute_url()}"
        aspects = _aspects(variant)
        aspects_seen += [aspect for aspect in aspects if aspect not in aspects_seen]
        if variant.pk == product.pk:
            entries.append({"@id": f"{url}#product", **aspects})
            continue
        price = variant.get_for_sale_price(request) if variant.get_for_sale() else variant.get_price(request)
        entry = {"@type": "Product", "@id": f"{url}#product", "name": variant_name(variant), "url": url}
        # Google rejects a Product with an offer but without image; variants without own images show the parent's.
        image = variant.get_image()
        if image and image.image:
            entry["image"] = f"{base}{image.image.url_400x400}"
        description = strip_tags(variant.get_short_description() or "").strip()
        if description:
            entry["description"] = description
        if variant.get_manufacturer():
            entry["brand"] = {"@type": "Brand", "name": variant.get_manufacturer().name}
        if own_sku(variant):
            entry["sku"] = own_sku(variant)
        entry.update(aspects)
        entry["offers"] = {
            "@type": "Offer",
            "url": url,
            "priceCurrency": "EUR",
            "price": f"{price:.2f}",
            "availability": f"https://schema.org/{'InStock' if variant.is_deliverable() else 'OutOfStock'}",
            "hasMerchantReturnPolicy": return_policy,
        }
        entries.append(entry)
    group = {
        "@context": "https://schema.org",
        "@type": "ProductGroup",
        "@id": f"{base}{parent.get_absolute_url()}#group",
        "name": parent.get_name(),
        "url": f"{base}{parent.get_absolute_url()}",
        "productGroupID": parent.get_sku() or str(parent.pk),
    }
    if parent.get_manufacturer():
        group["brand"] = {"@type": "Brand", "name": parent.get_manufacturer().name}
    if aspects_seen:
        group["variesBy"] = [f"https://schema.org/{aspect}" for aspect in aspects_seen]
    group["hasVariant"] = entries
    return _json(group)
