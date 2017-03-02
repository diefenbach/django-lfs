from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy

QUANTITY_FIELD_INTEGER = 0
QUANTITY_FIELD_DECIMAL_1 = 1
QUANTITY_FIELD_DECIMAL_2 = 2

QUANTITY_FIELD_TYPES = [
    (QUANTITY_FIELD_INTEGER, _(u"Integer")),
    (QUANTITY_FIELD_DECIMAL_1, _(u"Decimal 0.1")),
    (QUANTITY_FIELD_DECIMAL_2, _(u"Decimal 0.01")),
]

CHOICES_STANDARD = 0
CHOICES_YES = 2
CHOICES_NO = 3
CHOICES = [
    (CHOICES_STANDARD, _(u"Standard")),
    (CHOICES_YES, _(u"Yes")),
    (CHOICES_NO, _(u"No")),
]

STANDARD_PRODUCT = "0"
PRODUCT_WITH_VARIANTS = "1"
VARIANT = "2"
CONFIGURABLE_PRODUCT = "3"

PRODUCT_TYPE_LOOKUP = {
    STANDARD_PRODUCT: _(u"Standard"),
    PRODUCT_WITH_VARIANTS: _(u"Product with variants"),
    VARIANT: _(u"Variant"),
    CONFIGURABLE_PRODUCT: _(u"Configurable product")
}

PRODUCT_TYPE_CHOICES = [
    (STANDARD_PRODUCT, _(u"Standard")),
    (PRODUCT_WITH_VARIANTS, _(u"Product with variants")),
    (VARIANT, _(u"Variant")),
    (CONFIGURABLE_PRODUCT, _(u"Configurable product")),
]

PRODUCT_TYPE_FORM_CHOICES = [
    (STANDARD_PRODUCT, _(u"Standard")),
    (PRODUCT_WITH_VARIANTS, _(u"Product with variants")),
    (CONFIGURABLE_PRODUCT, _(u"Configurable product")),
]

CATEGORY_VARIANT_DEFAULT = -1
CATEGORY_VARIANT_CHEAPEST_PRICE = -2
CATEGORY_VARIANT_CHEAPEST_BASE_PRICE = -3
CATEGORY_VARIANT_CHEAPEST_PRICES = -4
CATEGORY_VARIANT_CHOICES = [
    (CATEGORY_VARIANT_DEFAULT, _(u"Default")),
    (CATEGORY_VARIANT_CHEAPEST_PRICE, _(u"Cheapest price")),
    (CATEGORY_VARIANT_CHEAPEST_BASE_PRICE, _(u"Cheapest base price")),
    (CATEGORY_VARIANT_CHEAPEST_PRICES, _(u"Cheapest prices")),
]

LIST = 0
SELECT = 1
VARIANTS_DISPLAY_TYPE_CHOICES = [
    (LIST, _(u"List")),
    (SELECT, _(u"Select")),
]

CONTENT_PRODUCTS = 1
CONTENT_CATEGORIES = 2

CONTENT_CHOICES = (
    (CONTENT_PRODUCTS, _(u"Products")),
    (CONTENT_CATEGORIES, _(u"Categories")),
)

DELIVERY_TIME_UNIT_HOURS = 1
DELIVERY_TIME_UNIT_DAYS = 2
DELIVERY_TIME_UNIT_WEEKS = 3
DELIVERY_TIME_UNIT_MONTHS = 4

DELIVERY_TIME_UNIT_CHOICES = (
    (DELIVERY_TIME_UNIT_HOURS, pgettext_lazy(u"Delivery time", u"hours")),
    (DELIVERY_TIME_UNIT_DAYS, pgettext_lazy(u"Delivery time", u"days")),
    (DELIVERY_TIME_UNIT_WEEKS, pgettext_lazy(u"Delivery time", u"weeks")),
    (DELIVERY_TIME_UNIT_MONTHS, pgettext_lazy(u"Delivery time", u"months")),
)

DELIVERY_TIME_UNIT_SINGULAR = {
    DELIVERY_TIME_UNIT_HOURS: pgettext_lazy(u"Delivery time", u"hour"),
    DELIVERY_TIME_UNIT_DAYS: pgettext_lazy(u"Delivery time", u"day"),
    DELIVERY_TIME_UNIT_WEEKS: pgettext_lazy(u"Delivery time", u"week"),
    DELIVERY_TIME_UNIT_MONTHS: pgettext_lazy(u"Delivery time", u"month"),
}

PROPERTY_VALUE_TYPE_FILTER = 0
PROPERTY_VALUE_TYPE_DEFAULT = 1
PROPERTY_VALUE_TYPE_DISPLAY = 2
PROPERTY_VALUE_TYPE_VARIANT = 3

PROPERTY_NUMBER_FIELD = 1
PROPERTY_TEXT_FIELD = 2
PROPERTY_SELECT_FIELD = 3

PROPERTY_FIELD_CHOICES = (
    (PROPERTY_NUMBER_FIELD, _(u"Float field")),
    (PROPERTY_TEXT_FIELD, _(u"Text field")),
    (PROPERTY_SELECT_FIELD, _(u"Select field")),
)

PROPERTY_STEP_TYPE_AUTOMATIC = 1
PROPERTY_STEP_TYPE_FIXED_STEP = 2
PROPERTY_STEP_TYPE_MANUAL_STEPS = 3

PROPERTY_STEP_TYPE_CHOICES = (
    (PROPERTY_STEP_TYPE_AUTOMATIC, _(u"Automatic")),
    (PROPERTY_STEP_TYPE_FIXED_STEP, _(u"Fixed step")),
    (PROPERTY_STEP_TYPE_MANUAL_STEPS, _(u"Manual steps")),
)


CAT_PRODUCT_PATH = "lfs/catalog/categories/product"   # category with products
CAT_CATEGORY_PATH = "lfs/catalog/categories/category"  # category with subcategories
PRODUCT_PATH = "lfs/catalog/products"   # product templates
IMAGES_PATH = "/media/lfs/icons"  # Path to template preview images

# Template configuration for category display
CATEGORY_TEMPLATES = (
    (0, {"file": "%s/%s" % (CAT_PRODUCT_PATH, "default.html"),
         "image": IMAGES_PATH + "/product_default.png",
         "name": _(u"Category with products"),
         }),
    (1, {"file": "%s/%s" % (CAT_CATEGORY_PATH, "default.html"),
         "image": IMAGES_PATH + "/category_square.png",
         "name": _(u"Category with subcategories"),
         }),
)
CATEGORY_TEMPLATES = getattr(settings, 'CATEGORY_TEMPLATES', CATEGORY_TEMPLATES)

# Template configuration for product display
PRODUCT_TEMPLATES = (
    (0, {"file": "%s/%s" % (PRODUCT_PATH, "product_inline.html"),
         "image": IMAGES_PATH + "/product_default.png",
         "name": _(u"Default")
         },),
)
PRODUCT_TEMPLATES = getattr(settings, 'PRODUCT_TEMPLATES', PRODUCT_TEMPLATES)

THUMBNAIL_SIZES = getattr(settings, 'LFS_THUMBNAIL_SIZES', ((60, 60), (100, 100), (200, 200), (300, 300), (400, 400), (600, 600)))
DELETE_FILES = getattr(settings, "LFS_DELETE_FILES", True)
DELETE_IMAGES = getattr(settings, "LFS_DELETE_IMAGES", True)
if getattr(settings, 'SOLR_ENABLED', False):
    SORTING_MAP = (
        {'default': 'effective_price', 'ftx': 'price asc', 'title': _('Price ascending')},
        {'default': '-effective_price', 'ftx': 'price desc', 'title': _('Price descending')},
        {'default': 'name', 'ftx': 'name asc', 'title': _('Name ascending')},
        {'default': '-name', 'ftx': 'name desc', 'title': _('Name descending')},
    )
else:
    SORTING_MAP = (
        {'default': 'effective_price', 'ftx': 'price', 'title': _('Price ascending')},
        {'default': '-effective_price', 'ftx': '-price', 'title': _('Price descending')},
        {'default': 'name', 'ftx': 'name', 'title': _('Name ascending')},
        {'default': '-name', 'ftx': '-name', 'title': _('Name descending')},
    )
