"""The apps LFS needs (``LFS_APPS``) and the defaults of its settings.

A project lists the apps with ``INSTALLED_APPS = ["my_theme", *LFS_APPS, ...]`` and sets only the LFS settings it
wants to change; LFS reads every other one through ``lfs_setting()`` with the default below.
"""

from typing import Any

from django.conf import settings
from django.utils.translation import gettext_lazy as _

# Django apps, LFS, and the add-ons LFS needs, in an order that works. A theme goes before them, so its templates win.
LFS_APPS = [
    "crispy_forms",
    "crispy_bootstrap5",
    "compressor",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.flatpages",
    "django.contrib.redirects",
    "django.contrib.sitemaps",
    "django_countries",
    "localflavor",
    "captcha",
    "reviews",
    "portlets",
    "postal",
    "lfs.addresses",
    "lfs.caching",
    "lfs.cart",
    "lfs.catalog",
    "lfs.checkout",
    "lfs.core",
    "lfs.criteria",
    "lfs.customer",
    "lfs.customer_tax",
    "lfs.discounts",
    "lfs.export",
    "lfs.gross_price",
    "lfs.mail",
    "lfs.manage",
    "lfs.marketing",
    "lfs.manufacturer",
    "lfs.net_price",
    "lfs.order",
    "lfs.page",
    "lfs.payment",
    "lfs.portlet",
    "lfs.search",
    "lfs.shipping",
    "lfs.supplier",
    "lfs.tax",
    "lfs.utils",
    "lfs.voucher",
    "lfs_contact",
    "lfs_order_numbers",
    "lfs_paypal",
]

_UNITS = ["l", "m", "qm", "cm", "lfm", "kg", "pcs."]

DEFAULTS: dict[str, Any] = {
    "LFS_AFTER_ADD_TO_CART": "lfs_added_to_cart",
    "LFS_DOCS": "https://github.com/diefenbach/django-lfs",
    "LFS_RECENT_PRODUCTS_LIMIT": 5,
    "LFS_ORDER_NUMBER_GENERATOR": "lfs_order_numbers.models.OrderNumberGenerator",
    "LFS_PRICE_CALCULATORS": [
        ["lfs.gross_price.calculator.GrossPriceCalculator", _("Price includes tax")],
        ["lfs.net_price.calculator.NetPriceCalculator", _("Price excludes tax")],
    ],
    "LFS_SHIPPING_METHOD_PRICE_CALCULATORS": [
        ["lfs.shipping.calculator.GrossShippingMethodPriceCalculator", _("Price includes tax")],
        ["lfs.shipping.calculator.NetShippingMethodPriceCalculator", _("Price excludes tax")],
    ],
    "LFS_UNITS": _UNITS,
    "LFS_PRICE_UNITS": _UNITS,
    "LFS_BASE_PRICE_UNITS": _UNITS,
    "LFS_PACKING_UNITS": _UNITS,
    "LFS_CRITERIA": [
        ["lfs.criteria.models.CartPriceCriterion", _("Cart Price")],
        ["lfs.criteria.models.CombinedLengthAndGirthCriterion", _("Combined Length and Girth")],
        ["lfs.criteria.models.CountryCriterion", _("Country")],
        ["lfs.criteria.models.HeightCriterion", _("Height")],
        ["lfs.criteria.models.LengthCriterion", _("Length")],
        ["lfs.criteria.models.WidthCriterion", _("Width")],
        ["lfs.criteria.models.WeightCriterion", _("Weight")],
        ["lfs.criteria.models.ShippingMethodCriterion", _("Shipping Method")],
        ["lfs.criteria.models.PaymentMethodCriterion", _("Payment Method")],
    ],
}


def lfs_setting(name: str) -> Any:
    """Return the project's setting ``name``, or LFS's default when the project does not set it.

    Raises KeyError for a name that has no default here.
    """
    return getattr(settings, name, DEFAULTS[name])
