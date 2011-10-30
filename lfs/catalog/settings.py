from django.conf import settings
from django.utils.translation import gettext_lazy as _

ACTIVE_FOR_SALE_STANDARD = 0
ACTIVE_FOR_SALE_YES = 2
ACTIVE_FOR_SALE_NO = 3
ACTIVE_FOR_SALE_CHOICES = [
    (ACTIVE_FOR_SALE_STANDARD, _(u"Standard")),
    (ACTIVE_FOR_SALE_YES, _(u"Yes")),
    (ACTIVE_FOR_SALE_NO, _(u"No")),
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
    (DELIVERY_TIME_UNIT_HOURS, _(u"hours")),
    (DELIVERY_TIME_UNIT_DAYS, _(u"days")),
    (DELIVERY_TIME_UNIT_WEEKS, _(u"weeks")),
    (DELIVERY_TIME_UNIT_MONTHS, _(u"months")),
)

DELIVERY_TIME_UNIT_SINGULAR = {
    DELIVERY_TIME_UNIT_HOURS: _(u"hour"),
    DELIVERY_TIME_UNIT_DAYS: _(u"day"),
    DELIVERY_TIME_UNIT_WEEKS: _(u"week"),
    DELIVERY_TIME_UNIT_MONTHS: _(u"month"),
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

# Template configuration for product display
PRODUCT_TEMPLATES = (
    (0, {"file": "%s/%s" % (PRODUCT_PATH, "product_inline.html"),
        "image": IMAGES_PATH + "/product_default.png",
        "name": _(u"Default")
    },),
)

THUMBNAIL_SIZES = getattr(settings, 'LFS_THUMBNAIL_SIZES', ((60, 60), (100, 100), (200, 200), (300, 300), (400, 400)))
