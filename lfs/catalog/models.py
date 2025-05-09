from html import unescape
import math
import sys
import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.urls import reverse
from django.db.models import F
from django.db import models
from django.template.defaultfilters import striptags
from django.utils import formats
from django.utils.translation import gettext_lazy as _
from django.conf import settings

import lfs.catalog.utils
from lfs.core.fields.thumbs import ImageWithThumbsField
from lfs.core import utils as core_utils
from lfs.core.managers import ActiveManager
from lfs.catalog.settings import CHOICES, CONTENT_CATEGORIES
from lfs.catalog.settings import CHOICES_STANDARD
from lfs.catalog.settings import CHOICES_YES
from lfs.catalog.settings import PRODUCT_TYPE_CHOICES
from lfs.catalog.settings import CONFIGURABLE_PRODUCT
from lfs.catalog.settings import STANDARD_PRODUCT
from lfs.catalog.settings import VARIANT
from lfs.catalog.settings import PRODUCT_WITH_VARIANTS
from lfs.catalog.settings import CAT_CATEGORY_PATH
from lfs.catalog.settings import CATEGORY_TEMPLATES
from lfs.catalog.settings import CONTENT_PRODUCTS
from lfs.catalog.settings import LIST
from lfs.catalog.settings import DELIVERY_TIME_UNIT_CHOICES
from lfs.catalog.settings import DELIVERY_TIME_UNIT_SINGULAR
from lfs.catalog.settings import DELIVERY_TIME_UNIT_HOURS
from lfs.catalog.settings import DELIVERY_TIME_UNIT_DAYS
from lfs.catalog.settings import DELIVERY_TIME_UNIT_WEEKS
from lfs.catalog.settings import DELIVERY_TIME_UNIT_MONTHS
from lfs.catalog.settings import PROPERTY_FIELD_CHOICES
from lfs.catalog.settings import PROPERTY_NUMBER_FIELD
from lfs.catalog.settings import PROPERTY_SELECT_FIELD
from lfs.catalog.settings import PROPERTY_TEXT_FIELD
from lfs.catalog.settings import PROPERTY_STEP_TYPE_CHOICES
from lfs.catalog.settings import PROPERTY_STEP_TYPE_AUTOMATIC
from lfs.catalog.settings import PROPERTY_STEP_TYPE_MANUAL_STEPS
from lfs.catalog.settings import PROPERTY_STEP_TYPE_FIXED_STEP
from lfs.catalog.settings import PROPERTY_VALUE_TYPE_DEFAULT
from lfs.catalog.settings import PROPERTY_VALUE_TYPE_DISPLAY
from lfs.catalog.settings import PROPERTY_VALUE_TYPE_VARIANT
from lfs.catalog.settings import PRODUCT_TEMPLATES
from lfs.catalog.settings import QUANTITY_FIELD_TYPES
from lfs.catalog.settings import QUANTITY_FIELD_INTEGER
from lfs.catalog.settings import QUANTITY_FIELD_DECIMAL_1
from lfs.catalog.settings import THUMBNAIL_SIZES
from lfs.catalog.settings import VARIANTS_DISPLAY_TYPE_CHOICES
from lfs.catalog.settings import CATEGORY_VARIANT_CHEAPEST_PRICE
from lfs.catalog.settings import CATEGORY_VARIANT_CHEAPEST_BASE_PRICE
from lfs.catalog.settings import CATEGORY_VARIANT_CHEAPEST_PRICES
from lfs.catalog.settings import CATEGORY_VARIANT_DEFAULT
from lfs.catalog.settings import SELECT

from lfs.tax.models import Tax
from lfs.supplier.models import Supplier
from lfs.manufacturer.models import Manufacturer


PRODUCT_TEMPLATES_CHOICES = [(ord, d["name"]) for (ord, d) in enumerate(PRODUCT_TEMPLATES)]
CATEGORY_TEMPLATES_CHOICES = [(ord, d["name"]) for (ord, d) in enumerate(CATEGORY_TEMPLATES)]


def get_unique_id_str():
    return str(uuid.uuid4())


LFS_UNITS = []
for u in settings.LFS_UNITS:
    LFS_UNITS.append([u, u])

LFS_PRICE_UNITS = []
for u in settings.LFS_PRICE_UNITS:
    LFS_PRICE_UNITS.append([u, u])

LFS_BASE_PRICE_UNITS = []
for u in settings.LFS_BASE_PRICE_UNITS:
    LFS_BASE_PRICE_UNITS.append([u, u])

LFS_PACKING_UNITS = []
for u in settings.LFS_PACKING_UNITS:
    LFS_PACKING_UNITS.append([u, u])


class Category(models.Model):
    """A category is used to browse through the shop products. A category can
    have one parent category and several child categories.

    **Attributes:**

    name
        The name of the category.

    slug
        Part of the URL

    parent
        Parent of the category. This is used to create a category tree. If
        it's None the category is a top level category.

    show_all_products
       If True the category displays it's direct products as well as products
       of it's sub categories. If False only direct products will be
       displayed.

    products
        The assigned products of the category.

    short_description
        A short description of the category. This is used in overviews.

    description
        The description of the category. This can be used in details views
        of the category.

    image
        The image of the category.

    position
        The position of the category within the shop resp. the parent
        category.

    static_block
        A assigned static block to the category.

    content
        decides which content will be displayed. At the moment this is either
        sub categories or products.

    active_formats
        If True product_rows, product_cols and category_cols are taken from
        the category otherwise from the parent.

    product_rows, product_cols, category_cols
        Format information for the category views

    meta_title
        Meta title of the category (HTML title)

    meta_keywords
        Meta keywords of the category

    meta_description
       Meta description of the category

    uid
       The unique id of the category

    level
       The level of the category within the category hierachie, e.g. if it
       is a top level category the level is 1.

    template
       Sets the template which renders the category view. If left to None, default template is used.
    """

    name = models.CharField(_("Name"), max_length=50)
    slug = models.SlugField(_("Slug"), unique=True)
    parent = models.ForeignKey("self", models.SET_NULL, verbose_name=_("Parent"), blank=True, null=True)

    # If selected it shows products of the sub categories within the product
    # view. If not it shows only direct products of the category.
    show_all_products = models.BooleanField(_("Show all products"), default=True)

    products = models.ManyToManyField("Product", verbose_name=_("Products"), blank=True, related_name="categories")
    short_description = models.TextField(_("Short description"), blank=True)
    description = models.TextField(_("Description"), blank=True)
    image = ImageWithThumbsField(_("Image"), upload_to="images", blank=True, null=True, sizes=THUMBNAIL_SIZES)
    position = models.IntegerField(_("Position"), default=1000)
    exclude_from_navigation = models.BooleanField(_("Exclude from navigation"), default=False)
    static_block = models.ForeignKey(
        "StaticBlock",
        verbose_name=_("Static block"),
        blank=True,
        null=True,
        related_name="categories",
        on_delete=models.SET_NULL,
    )
    template = models.PositiveSmallIntegerField(
        _("Category template"), blank=True, null=True, choices=CATEGORY_TEMPLATES_CHOICES
    )
    active_formats = models.BooleanField(_("Active formats"), default=False)

    product_rows = models.IntegerField(_("Product rows"), default=3)
    product_cols = models.IntegerField(_("Product cols"), default=3)
    category_cols = models.IntegerField(_("Category cols"), default=3)

    meta_title = models.CharField(_("Meta title"), max_length=100, default="<name>")
    meta_keywords = models.TextField(_("Meta keywords"), blank=True)
    meta_description = models.TextField(_("Meta description"), blank=True)

    level = models.PositiveSmallIntegerField(default=1)
    uid = models.CharField(max_length=50, editable=False, unique=True, default=get_unique_id_str)

    class Meta:
        ordering = ("position",)
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        app_label = "catalog"

    def __str__(self):
        return "%s (%s)" % (self.name, self.slug)

    def get_absolute_url(self):
        """
        Returns the absolute_url.
        """
        return reverse("lfs_category", kwargs={"slug": self.slug})

    @property
    def content_type(self):
        """
        Returns the content type of the category as lower string.
        """
        return "category"

    def get_all_children(self):
        """
        Returns all child categories of the category.
        """

        def _get_all_children(category, children):
            for category in Category.objects.filter(parent=category.id):
                children.append(category)
                _get_all_children(category, children)

        cache_key = "%s-category-all-children-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, self.id)
        children = cache.get(cache_key)
        if children is not None:
            return children

        children = []
        for category in Category.objects.filter(parent=self.id):
            children.append(category)
            _get_all_children(category, children)

        cache.set(cache_key, children)
        return children

    def get_children(self):
        """
        Returns the first level child categories.
        """
        cache_key = "%s-category-children-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, self.id)

        categories = cache.get(cache_key)
        if categories is not None:
            return categories

        categories = Category.objects.filter(parent=self.id)
        cache.set(cache_key, categories)

        return categories

    def get_format_info(self):
        """
        Returns format information.
        """
        if self.active_formats is True:
            return {
                "product_cols": self.product_cols,
                "product_rows": self.product_rows,
                "category_cols": self.category_cols,
            }
        else:
            if self.parent is None:
                try:
                    # TODO: Use cache here. Maybe we need a lfs_get_object,
                    # which raise a ObjectDoesNotExist if the object does not
                    # exist
                    from lfs.core.models import Shop

                    shop = Shop.objects.get(pk=1)
                except ObjectDoesNotExist:
                    return {
                        "product_cols": 3,
                        "product_rows": 3,
                        "category_cols": 3,
                    }
                else:
                    return {
                        "product_cols": shop.product_cols,
                        "product_rows": shop.product_rows,
                        "category_cols": shop.category_cols,
                    }
            else:
                return self.parent.get_format_info()

    def get_meta_title(self):
        """
        Returns the meta keywords of the catgory.
        """
        mt = self.meta_title.replace("<name>", self.name)
        return mt

    def get_meta_keywords(self):
        """
        Returns the meta keywords of the catgory.
        """
        mk = self.meta_keywords.replace("<name>", self.name)
        mk = mk.replace("<short-description>", self.short_description)
        return mk

    def get_meta_description(self):
        """
        Returns the meta description of the product.
        """
        md = self.meta_description.replace("<name>", self.name)
        md = md.replace("<short-description>", self.short_description)
        return md

    def get_image(self):
        """
        Returns the image of the category if it has none it inherits that from
        the parent category.
        """
        if self.image:
            return self.image
        else:
            if self.parent_id:
                return self.parent.get_image()

        return None

    def get_parents(self):
        """
        Returns all parent categories.
        """
        cache_key = "%s-category-parents-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, self.id)
        parents = cache.get(cache_key)
        if parents is not None:
            return parents

        parents = []
        category = self.parent
        while category is not None:
            parents.append(category)
            category = category.parent

        cache.set(cache_key, parents)
        return parents

    def get_products(self):
        """
        Returns the direct products of the category.
        """
        cache_key = "%s-category-products-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, self.id)
        products = cache.get(cache_key)
        if products is not None:
            return products

        products = self.products.filter(active=True).exclude(sub_type=VARIANT)
        cache.set(cache_key, products)

        return products

    def get_property_groups(self):
        """
        Returns property groups for given category.
        """
        from lfs.caching.utils import get_cache_group_id

        properties_version = get_cache_group_id("global-properties-version")
        cache_key = "%s-%s-category-property-groups-%s" % (
            settings.CACHE_MIDDLEWARE_KEY_PREFIX,
            properties_version,
            self.id,
        )
        pgs = cache.get(cache_key)
        if pgs is not None:
            return pgs
        products = self.get_products()
        pgs = lfs.catalog.models.PropertyGroup.objects.filter(products__in=products).distinct()
        cache.set(cache_key, pgs)

        return pgs

    def get_all_products(self):
        """
        Returns the direct products and all products of the sub categories
        """
        cache_key = "%s-category-all-products-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, self.id)
        products = cache.get(cache_key)
        if products is not None:
            return products

        categories = [self]
        categories.extend(self.get_all_children())

        products = (
            lfs.catalog.models.Product.objects.distinct()
            .filter(active=True, categories__in=categories)
            .exclude(sub_type=VARIANT)
            .distinct()
        )

        cache.set(cache_key, products)
        return products

    def get_filtered_products(self, filters, price_filter, sorting):
        """
        Returns products for this category filtered by passed filters,
        price_filter and sorted by passed sorting.
        """
        return lfs.catalog.utils.get_filtered_products_for_category(self, filters, price_filter, sorting)

    def get_static_block(self):
        """
        Returns the static block of the category.
        """
        cache_key = "%s-static-block-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, self.id)
        blocks = cache.get(cache_key)
        if blocks is not None:
            return blocks

        block = self.static_block
        cache.set(cache_key, blocks)

        return block

    # 3rd party contracts
    def get_parent_for_portlets(self):
        """
        Returns the parent for portlets.
        """
        # TODO: Circular imports
        import lfs.core.utils

        return self.parent or lfs.core.utils.get_default_shop()

    def get_template_name(self):
        """
        Returns the path of the category template.
        """
        if self.template is not None:
            return CATEGORY_TEMPLATES[int(self.template)]["file"]

        return None

    def get_content(self):
        """
        Returns the type of content the template is rendering depending on its
        path.
        """
        if self.get_template_name() is None:
            return CONTENT_PRODUCTS
        if self.get_template_name().startswith(CAT_CATEGORY_PATH):
            return CONTENT_CATEGORIES
        return CONTENT_PRODUCTS


class Product(models.Model):
    """
    A product is sold within a shop.

    **Parameters:**

    name
        The name of the product

    slug
        Part of the URL

    sku
        The external unique id of the product

    price
        The gross price of the product

    price_calculator
        Class that implements lfs.price.PriceCalculator for calculating product price.

    effective_price:
        Only for internal usage (price filtering).

    unit
        The unit of the product. This is displayed beside the quantity
        field.

    price_unit
        The unit of the product's price. This is displayed beside the price

    short_description
        The short description of the product. This is used within overviews.

    description
        The description of the product. This is used within the detailed view
        of the product.

    images
        The images of the product.

    meta_title
        the meta title of the product (the title of the HTML page).

    meta_keywords
        the meta keywords of the product.

    meta_description
        the meta description of the product.

    related_products
        Related products for this products.

    accessories
        Accessories for this products.

    for_sale
        If True the product is for sale and the for sale price will be
        displayed.

    for_sale_price
        The for sale price for the product. Will be displayed if the product
        is for sale.

    active
        If False the product won't be displayed to shop users.

    creation_date
        The creation date of the product

    modification_date
        The modification date of the product

    deliverable
        If True the product is deliverable. Otherwise not.

    manual_delivery_time
        If True the delivery_time of the product is taken. Otherwise the
        delivery time will be calculate on global delivery times and
        selected shipping method.

    delivery_time
        The delivery time of the product. This is only relevant if
        manual_delivery_time is set to true.

    order_time
        Order time of the product when no product is within the stock. This
        is added to the product's delivery time.

    ordered_at
        The date when the product has been ordered. To calculate the rest of
        the order time since the product has been ordered.

    manage_stock_amount
        If true the stock amount of the product will be decreased when a
        product has been saled.

    weight, height, length, width
        The dimensions of the product relevant for the the stock (IOW the
        dimension of the product's box not the product itself).

    tax
        Tax rate of the product.

    static_block
        A static block which has been assigned to the product.

    sub_type
        Sub type of the product. At the moment that is standard, product with
        variants, variant.

    default_variant
        The default variant of a product with variants. This will be
        displayed at first if the shop customer browses to a product with
        variant.

    variant_category
        The variant of a product with variants which will be displayed within
        the category overview.

    variants_display_type
        This decides howt the variants of a product with variants are
        displayed. This is select box of list.

    parent
        The parent of a variant (only relevant for variants)

    active_xxx
        If set to true the information will be taken from the variant.
        Otherwise from the parent product (only relevant for variants)

    supplier
        The supplier of the product

    template
        Sets the template, which renders the product content. If left to None, default template is used.

    active_price_calculation
        If True the price will be calculated by the field price_calculation

    price_calculation
        Formula to calculate price of the product.

    sku_manufacturer
        The product's article ID of the manufacturer (external article id)

    manufacturer
        The manufacturer of the product.

    uid
       The unique id of the product

    type_of_quantity_field
        The type of the quantity field: Integer or Decimal for now.
    """

    # All products
    name = models.CharField(_("Name"), help_text=_("The name of the product."), max_length=80, blank=True)
    slug = models.SlugField(
        _("Slug"), help_text=_("The unique last part of the Product's URL."), unique=True, max_length=120
    )
    sku = models.CharField(
        _("SKU"), help_text=_("Your unique article number of the product."), blank=True, max_length=40
    )
    price = models.FloatField(_("Price"), default=0.0)
    price_calculator = models.CharField(
        _("Price calculator"), null=True, blank=True, choices=settings.LFS_PRICE_CALCULATORS, max_length=255
    )
    effective_price = models.FloatField(_("Price"), blank=True)
    price_unit = models.CharField(_("Price unit"), blank=True, max_length=20, choices=LFS_PRICE_UNITS)
    unit = models.CharField(_("Quantity field unit"), blank=True, max_length=20, choices=LFS_UNITS)
    short_description = models.TextField(_("Short description"), blank=True)
    description = models.TextField(_("Description"), blank=True)
    images = GenericRelation(
        "Image", verbose_name=_("Images"), object_id_field="content_id", content_type_field="content_type"
    )

    meta_title = models.CharField(_("Meta title"), blank=True, default="<name>", max_length=80)
    meta_keywords = models.TextField(_("Meta keywords"), blank=True)
    meta_description = models.TextField(_("Meta description"), blank=True)

    related_products = models.ManyToManyField(
        "self",
        verbose_name=_("Related products"),
        blank=True,
        symmetrical=False,
        related_name="reverse_related_products",
    )

    accessories = models.ManyToManyField(
        "Product",
        verbose_name=_("Acessories"),
        blank=True,
        symmetrical=False,
        through="ProductAccessories",
        related_name="reverse_accessories",
    )

    for_sale = models.BooleanField(_("For sale"), default=False)
    for_sale_price = models.FloatField(_("For sale price"), default=0.0)
    active = models.BooleanField(_("Active"), default=False)
    creation_date = models.DateTimeField(_("Creation date"), auto_now_add=True)
    modification_date = models.DateTimeField(_("Modification date"), auto_now=True)

    # Stocks
    supplier = models.ForeignKey(Supplier, models.SET_NULL, related_name="product_set", null=True, blank=True)
    deliverable = models.BooleanField(_("Deliverable"), default=True)
    manual_delivery_time = models.BooleanField(_("Manual delivery time"), default=False)
    delivery_time = models.ForeignKey(
        "DeliveryTime",
        models.SET_NULL,
        verbose_name=_("Delivery time"),
        blank=True,
        null=True,
        related_name="products_delivery_time",
    )
    order_time = models.ForeignKey(
        "DeliveryTime",
        models.SET_NULL,
        verbose_name=_("Order time"),
        blank=True,
        null=True,
        related_name="products_order_time",
    )
    ordered_at = models.DateField(_("Ordered at"), blank=True, null=True)
    manage_stock_amount = models.BooleanField(_("Manage stock amount"), default=False)
    stock_amount = models.FloatField(_("Stock amount"), default=0)

    active_packing_unit = models.PositiveSmallIntegerField(_("Active packing"), default=0)
    packing_unit = models.FloatField(_("Amount per packing"), blank=True, null=True)
    packing_unit_unit = models.CharField(
        _("Packing unit"), blank=True, default="", max_length=30, choices=LFS_PACKING_UNITS
    )

    static_block = models.ForeignKey(
        "StaticBlock", models.SET_NULL, verbose_name=_("Static block"), blank=True, null=True, related_name="products"
    )

    # Dimension
    weight = models.FloatField(_("Weight"), default=0.0)
    height = models.FloatField(_("Height"), default=0.0)
    length = models.FloatField(_("Length"), default=0.0)
    width = models.FloatField(_("Width"), default=0.0)

    # Standard Products
    tax = models.ForeignKey(Tax, models.SET_NULL, verbose_name=_("Tax"), blank=True, null=True)
    sub_type = models.CharField(_("Subtype"), max_length=10, choices=PRODUCT_TYPE_CHOICES, default=STANDARD_PRODUCT)

    # Varianted Products
    default_variant = models.ForeignKey(
        "self", models.SET_NULL, verbose_name=_("Default variant"), blank=True, null=True
    )
    category_variant = models.SmallIntegerField(
        _("Category variant"),
        blank=True,
        null=True,
    )

    variants_display_type = models.IntegerField(
        _("Variants display type"), choices=VARIANTS_DISPLAY_TYPE_CHOICES, default=LIST
    )

    # Product Variants
    variant_position = models.IntegerField(default=999)
    parent = models.ForeignKey(
        "self", models.SET_NULL, blank=True, null=True, verbose_name=_("Parent"), related_name="variants"
    )
    active_name = models.BooleanField(_("Active name"), default=False)
    active_sku = models.BooleanField(_("Active SKU"), default=False)
    active_short_description = models.BooleanField(_("Active short description"), default=False)
    active_static_block = models.BooleanField(_("Active static bock"), default=False)
    active_description = models.BooleanField(_("Active description"), default=False)
    active_price = models.BooleanField(_("Active price"), default=False)
    active_for_sale = models.PositiveSmallIntegerField(_("Active for sale"), choices=CHOICES, default=CHOICES_STANDARD)
    active_for_sale_price = models.BooleanField(_("Active for sale price"), default=False)
    active_images = models.BooleanField(_("Active Images"), default=False)
    active_related_products = models.BooleanField(_("Active related products"), default=False)
    active_accessories = models.BooleanField(_("Active accessories"), default=False)
    active_meta_title = models.BooleanField(_("Active meta title"), default=False)
    active_meta_description = models.BooleanField(_("Active meta description"), default=False)
    active_meta_keywords = models.BooleanField(_("Active meta keywords"), default=False)
    active_dimensions = models.BooleanField(_("Active dimensions"), default=False)
    template = models.PositiveSmallIntegerField(
        _("Product template"), blank=True, null=True, choices=PRODUCT_TEMPLATES_CHOICES
    )

    # Price calculation
    active_price_calculation = models.BooleanField(_("Active price calculation"), default=False)
    price_calculation = models.CharField(_("Price Calculation"), blank=True, max_length=100)

    # Base price
    active_base_price = models.PositiveSmallIntegerField(_("Active base price"), default=0)
    base_price_unit = models.CharField(
        _("Base price unit"), blank=True, default="", max_length=30, choices=LFS_BASE_PRICE_UNITS
    )
    base_price_amount = models.FloatField(_("Base price amount"), default=0.0, blank=True, null=True)

    # Manufacturer
    sku_manufacturer = models.CharField(_("SKU Manufacturer"), blank=True, max_length=100)
    manufacturer = models.ForeignKey(
        Manufacturer,
        verbose_name=_("Manufacturer"),
        blank=True,
        null=True,
        related_name="products",
        on_delete=models.SET_NULL,
    )
    type_of_quantity_field = models.PositiveSmallIntegerField(
        _("Type of quantity field"), blank=True, null=True, choices=QUANTITY_FIELD_TYPES
    )

    objects = ActiveManager()

    uid = models.CharField(max_length=50, editable=False, unique=True, default=get_unique_id_str)

    class Meta:
        ordering = ("name",)
        app_label = "catalog"

    def __str__(self):
        return "%s (%s)" % (self.name, self.slug)

    def save(self, *args, **kwargs):
        """
        Overwritten to save effective_price.
        """
        # Remove html entities for a better search
        # TODO: This might be removed when a new wysiwyg editor is used
        self.description = unescape(self.description)
        self.short_description = unescape(self.short_description)

        pc = self.get_price_calculator(None)
        self.effective_price = pc.get_effective_price()
        if self.is_variant():
            dv = self.parent.get_default_variant()
            # if this is default variant
            if dv and self.pk == dv.pk:
                # trigger effective price calculation for parent to have it set to price of default variant
                super(Product, self).save(*args, **kwargs)
                self.parent.save()
            else:
                super(Product, self).save(*args, **kwargs)
        else:
            super(Product, self).save(*args, **kwargs)

    def get_absolute_url(self):
        """
        Returns the absolute url of the product.
        """
        return reverse("lfs_product", kwargs={"slug": self.slug})

    @property
    def content_type(self):
        """
        Returns the content type of the product as lower string.
        """
        return "product"

    def decrease_stock_amount(self, amount):
        """
        If the stock amount is managed by LFS, it decreases stock amount by
        given amount.
        """
        if self.manage_stock_amount:
            self.stock_amount = F("stock_amount") - amount
        self.save()

    def get_accessories(self):
        """
        Returns the ProductAccessories relationship objects - not the accessory
        (Product) objects.

        This is necessary to have also the default quantity of the relationship.
        """
        if self.is_variant() and not self.active_accessories:
            product = self.parent
        else:
            product = self

        pas = []
        for pa in ProductAccessories.objects.filter(product=product):
            if pa.accessory.is_active():
                pas.append(pa)

        return pas

    def has_accessories(self):
        """
        Returns True if the product has accessories.
        """
        return len(self.get_accessories()) > 0

    def get_attachments(self):
        """
        Returns the ProductAttachment relationship objects. If no attachments
        are found and the instance is a variant returns the parent's ones.
        """
        attachments = ProductAttachment.objects.filter(product=self)
        if not attachments and self.is_variant():
            attachments = ProductAttachment.objects.filter(product=self.parent)
        return attachments

    def has_attachments(self):
        """
        Returns True if the product has attachments.
        """
        return len(self.get_attachments()) > 0

    def get_amount_by_packages(self, quantity):
        """ """
        packing_unit, packing_unit_unit = self.get_packing_info()
        packages = math.ceil(quantity / packing_unit)
        return packages * packing_unit

    def get_categories(self, with_parents=False):
        """
        Returns the categories of the product.
        """
        cache_key = "%s-product-categories-%s-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, self.id, with_parents)
        categories = cache.get(cache_key)

        if categories is not None:
            return categories

        object = self.get_parent()

        if with_parents:
            categories = []
            for category in object.categories.all():
                while category:
                    categories.append(category)
                    category = category.parent
            categories = categories
        else:
            categories = object.categories.all()

        cache.set(cache_key, categories)
        return categories

    def get_category(self):
        """
        Returns the first category of a product.
        """
        object = self.get_parent()

        try:
            return object.get_categories()[0]
        except IndexError:
            return None

    def get_current_category(self, request):
        """
        Returns product category based on actual categories of the given product
        and the last visited category.

        This is needed if the product has more than one category to display
        breadcrumbs, selected menu points, etc. appropriately.
        """
        last_category = None
        category = None
        product_categories = self.get_categories()
        if len(product_categories) >= 1:
            try:
                if len(product_categories) == 1:
                    category = product_categories[0]
                    return category
                else:
                    last_category_id = request.session.get("last_category")
                    try:
                        last_category = Category.objects.get(pk=last_category_id)
                    except Category.DoesNotExist:
                        last_category = None

                if last_category is None:
                    return product_categories[0]

                category = None
                if last_category in product_categories:
                    category = last_category
                else:
                    children = last_category.get_all_children()
                    for product_category in product_categories:
                        if product_category in children:
                            category = product_category
                            break
                if category is None:
                    category = product_categories[0]

                request.session["last_category"] = category.id
            except IndexError:
                category = None

        return category

    def get_come_from_page(self, request):
        """Returns manufacturer or category that was last visited.
        Used to generate 'back to overview' url
        """
        lm_id = request.session.get("last_manufacturer")
        lm = Manufacturer.objects.filter(pk=lm_id).first()
        if lm and self.manufacturer == lm:
            return self.manufacturer
        return self.get_current_category(request)

    def get_description(self):
        """
        Returns the description of the product. Takes care whether the product
        is a variant and description is active or not.
        """
        if self.is_variant():
            if self.active_description:
                description = self.description
                description = description.replace("%P", self.parent.description)
            else:
                description = self.parent.description
        else:
            description = self.description

        return description

    def get_base_price_amount(self):
        if self.is_variant() and self.active_base_price == CHOICES_STANDARD:
            return self.parent.base_price_amount
        else:
            return self.base_price_amount

    def get_base_price_unit(self):
        if self.is_variant() and self.active_base_price == CHOICES_STANDARD:
            return self.parent.base_price_unit
        else:
            return self.base_price_unit

    def get_active_base_price(self):
        """
        Returns true if the base price is supposed to be displayed. Takes care
        whether the product is a variant.
        """
        if self.is_variant():
            if self.active_base_price == CHOICES_STANDARD:
                return self.parent.get_active_base_price()
            else:
                return self.active_base_price == CHOICES_YES
        else:
            return self.active_base_price in (
                1,
                CHOICES_YES,
            )  # we have to check for 1 as it's value set by checkbox input

    def get_base_packing_price(self, request, with_properties=True, amount=1):
        """
        See lfs.plugins.PriceCalculator
        """
        pc = self.get_price_calculator(request)
        return pc.get_base_packing_price(with_properties, amount)

    def get_base_packing_price_net(self, request, with_properties=True, amount=1):
        """
        See lfs.plugins.PriceCalculator
        """
        pc = self.get_price_calculator(request)
        return pc.get_base_packing_price_net(with_properties, amount)

    def get_base_packing_price_gross(self, request, with_properties=True, amount=1):
        """
        See lfs.plugins.PriceCalculator
        """
        pc = self.get_price_calculator(request)
        return pc.get_base_packing_price_gross(with_properties, amount)

    # TODO: Check whether there is a test case for that and write one if not.
    def get_for_sale(self):
        """
        Returns true if the product is for sale. Takes care whether the product
        is a variant.
        """
        if self.is_variant():
            if self.active_for_sale == CHOICES_STANDARD:
                return self.parent.for_sale
            elif self.active_for_sale == CHOICES_YES:
                return True
            else:
                return False
        else:
            return self.for_sale

    def get_short_description(self):
        """
        Returns the short description of the product. Takes care whether the
        product is a variant and short description is active or not.
        """
        if self.is_variant() and not self.active_short_description:
            return self.parent.short_description
        else:
            return self.short_description

    def get_image(self):
        """
        Returns the first image (the main image) of the product.
        """
        try:
            return self.get_images()[0]
        except IndexError:
            return None

    def get_images(self):
        """
        Returns all images of the product, including the main image.
        """
        cache_key = "%s-product-images-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, self.id)
        images = cache.get(cache_key)

        if images is None:
            if self.is_variant() and not self.active_images:
                obj = self.parent
            else:
                obj = self

            images = obj.images.all()
            cache.set(cache_key, images)

        return images

    def get_sub_images(self):
        """
        Returns all images of the product, except the main image.
        """
        return self.get_images()[1:]

    def get_meta_title(self):
        """
        Returns the meta title of the product. Takes care whether the product is
        a variant and meta title are active or not.
        """
        if self.is_variant() and not self.active_meta_title:
            mt = self.parent.meta_title
        else:
            mt = self.meta_title

        mt = mt.replace("<name>", self.get_name())
        return mt

    def get_meta_keywords(self):
        """
        Returns the meta keywords of the product. Takes care whether the product
        is a variant and meta keywords are active or not.
        """
        if self.is_variant() and not self.active_meta_keywords:
            mk = self.parent.meta_keywords
        else:
            mk = self.meta_keywords

        mk = mk.replace("<name>", self.get_name())
        mk = mk.replace("<short-description>", self.get_short_description())
        return mk

    def get_meta_description(self):
        """
        Returns the meta description of the product. Takes care whether the
        product is a variant and meta description are active or not.
        """
        if self.is_variant() and not self.active_meta_description:
            md = self.parent.meta_description
        else:
            md = self.meta_description

        md = md.replace("<name>", self.get_name())
        md = md.replace("<short-description>", striptags(self.get_short_description()))
        return md

    # TODO: Check whether there is a test case for that and write one if not.
    def get_name(self):
        """
        Returns the name of the product. Takes care whether the product is a
        variant and name is active or not.
        """
        if self.is_variant():
            if self.active_name:
                name = self.name
                name = name.replace("%P", self.parent.name)
            else:
                name = self.parent.name
        else:
            name = self.name

        return name

    def get_option(self, property_id):
        """
        Returns the id of the selected option for property with passed id.
        """
        from lfs.caching.utils import get_cache_group_id

        pid = self.get_parent().pk
        properties_version = get_cache_group_id("global-properties-version")
        group_id = "%s-%s" % (properties_version, get_cache_group_id("properties-%s" % pid))
        cache_key = "%s-%s-productpropertyvalue%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, group_id, self.id)
        options = cache.get(cache_key)
        if options is None:
            options = {}
            for pvo in self.property_values.all():
                options[pvo.property_id] = pvo.value
            cache.set(cache_key, options)
        try:
            return options[property_id]
        except KeyError:
            return None

    def get_displayed_properties(self):
        """
        Returns properties with ``display_on_product`` is True.
        """
        from lfs.caching.utils import get_cache_group_id

        pid = self.get_parent().pk
        properties_version = get_cache_group_id("global-properties-version")
        group_id = "%s-%s" % (properties_version, get_cache_group_id("properties-%s" % pid))
        cache_key = "%s-%s-displayed-properties-%s" % (group_id, settings.CACHE_MIDDLEWARE_KEY_PREFIX, self.id)
        properties = cache.get(cache_key)
        if properties:
            return properties

        properties = []
        for ppv in self.property_values.filter(
            property__display_on_product=True, type=PROPERTY_VALUE_TYPE_DISPLAY
        ).order_by("property_group__name", "property__position"):
            if ppv.property.is_select_field:
                try:
                    po = PropertyOption.objects.get(pk=int(float(ppv.value)))
                except (PropertyOption.DoesNotExist, ValueError):
                    continue
                else:
                    value = po.name
                    position = po.position
            else:
                value = ppv.value
                position = 1

            properties.append(
                {
                    "name": ppv.property.name,
                    "title": ppv.property.title,
                    "value": value,
                    "position": (ppv.property.position * 1000) + position,
                    "unit": ppv.property.unit,
                    "property_group": ppv.property_group,
                    "property_group_id": ppv.property_group_id if ppv.property_group else 0,
                }
            )
        cache.set(cache_key, properties)
        return properties

    def get_variant_properties(self):
        """
        Returns the property value of a variant in the correct ordering of the
        properties.
        """
        from lfs.caching.utils import get_cache_group_id

        pid = self.get_parent().pk
        properties_version = get_cache_group_id("global-properties-version")
        group_id = "%s-%s" % (properties_version, get_cache_group_id("properties-%s" % pid))
        cache_key = "%s-variant-properties-%s-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, group_id, self.id)

        properties = cache.get(cache_key)
        if properties is not None:
            return properties

        properties = []

        for ppv in self.property_values.filter(type=PROPERTY_VALUE_TYPE_VARIANT).order_by(
            "property_group__name", "property__position"
        ):
            if ppv.property.is_select_field:
                try:
                    po = PropertyOption.objects.get(pk=int(float(ppv.value)))
                except PropertyOption.DoesNotExist:
                    continue
                else:
                    value = po.name
            else:
                value = ppv.value
            properties.append(
                {
                    "name": ppv.property.name,
                    "title": ppv.property.title,
                    "value": value,
                    "unit": ppv.property.unit,
                    "property_group": ppv.property_group,
                    "property_group_id": ppv.property_group_id if ppv.property_group else 0,
                }
            )

        cache.set(cache_key, properties)

        return properties

    def is_select_display_type(self):
        return self.variants_display_type == SELECT

    def is_list_display_type(self):
        return self.variants_display_type == LIST

    def get_all_properties(self, variant=None):
        """Return all properties for current product
        if variant is passed then select fields for it
        """
        if not self.is_product_with_variants():
            return []
        properties = []
        if self.variants_display_type == SELECT:
            # Get all properties (sorted). We need to traverse through all
            # property/options to select the options of the current variant.
            for prop_dict in self.get_variants_properties():
                options = []
                selected_option_value = ""
                prop = prop_dict["property"]
                property_group = prop_dict["property_group"]
                for property_option in prop.options.all():
                    # check if option exists in any variant
                    option_used = ProductPropertyValue.objects.filter(
                        parent_id=self.pk,
                        product__active=True,
                        property=prop,
                        property_group=property_group,
                        type=PROPERTY_VALUE_TYPE_VARIANT,
                        value=property_option.pk,
                    ).exists()
                    if option_used:
                        if variant and variant.has_option(property_group, prop, property_option):
                            selected = True
                            selected_option_value = property_option.pk
                        else:
                            selected = False
                        options.append(
                            {
                                "id": property_option.id,
                                "name": property_option.name,
                                "selected": selected,
                            }
                        )

                # check for variants that do not have such property and if such variants exists add empty option
                ppv_count = ProductPropertyValue.objects.filter(
                    parent_id=self.pk,
                    product__active=True,
                    type=PROPERTY_VALUE_TYPE_VARIANT,
                    property=prop,
                    property_group=property_group,
                ).count()
                if ppv_count != self.get_variants().count():
                    selected = False
                    if variant and selected_option_value == "":
                        selected = True
                    options.insert(0, {"id": "", "name": "", "selected": selected})
                if not (len(options) == 1 and options[0]["id"] == ""):
                    properties.append(
                        {
                            "id": prop.id,
                            "name": prop.name,
                            "title": prop.title,
                            "unit": prop.unit,
                            "options": options,
                            "property_group": property_group,
                            "property_group_id": property_group.id if property_group else 0,
                        }
                    )
        else:
            for prop_dict in self.get_variants_properties():
                selected_option_name = ""
                selected_option_value = ""
                prop = prop_dict["property"]
                property_group = prop_dict["property_group"]
                if variant:
                    try:
                        ppv = ProductPropertyValue.objects.get(
                            product=variant,
                            type=PROPERTY_VALUE_TYPE_VARIANT,
                            property=prop,
                            property_group=property_group,
                        )
                        selected_option_value = ppv.value
                        selected_option_name = prop.options.get(pk=ppv.value).name
                    except (ProductPropertyValue.DoesNotExist, PropertyOption.DoesNotExist):
                        pass
                properties.append(
                    {
                        "id": prop.id,
                        "name": prop.name,
                        "title": prop.title,
                        "unit": prop.unit,
                        "selected_option_name": selected_option_name,
                        "selected_option_value": selected_option_value,
                        "property_group": property_group,
                        "property_group_id": property_group.id if property_group else 0,
                    }
                )
        return properties

    def get_variant_properties_for_parent(self):
        """
        Returns the property value of a variant in the correct ordering of the
        properties. Traverses through all parent properties
        """
        from lfs.caching.utils import get_cache_group_id

        pid = self.get_parent().pk
        properties_version = get_cache_group_id("global-properties-version")
        group_id = "%s-%s" % (properties_version, get_cache_group_id("properties-%s" % pid))
        cache_key = "%s-variant-properties-for-parent-%s-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, group_id, self.id)

        properties = cache.get(cache_key)
        if properties:
            return properties

        properties = self.parent.get_all_properties(variant=self)
        cache.set(cache_key, properties)

        return properties

    def has_option(self, property_group, prop, option):
        """
        Returns True if the variant has the given property / option combination.
        """
        from lfs.caching.utils import get_cache_group_id

        pid = self.get_parent().pk
        properties_version = get_cache_group_id("global-properties-version")
        group_id = "%s-%s" % (properties_version, get_cache_group_id("properties-%s" % pid))
        options = cache.get("%s-%s-productpropertyvalue%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, group_id, self.id))
        if options is None:
            options = {}
            for pvo in self.property_values.filter(property_group=property_group):
                options[pvo.property_id] = pvo.value
            cache.set(
                "%s-%s-productpropertyvalue%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, group_id, self.id), options
            )

        try:
            return options[prop.id] == str(option.id)
        except KeyError:
            return False

    def get_default_properties_price(self):
        """
        Returns the total price of all default properties.
        """
        price = 0
        for property_dict in self.get_configurable_properties():
            prop = property_dict["property"]
            property_group = property_dict["property_group"]
            if prop.add_price:
                # Try to get the default value of the property
                try:
                    ppv = ProductPropertyValue.objects.get(
                        product=self, property_group=property_group, property=prop, type=PROPERTY_VALUE_TYPE_DEFAULT
                    )
                    po = PropertyOption.objects.get(pk=ppv.value)
                except (ObjectDoesNotExist, ValueError):
                    # If there is no explicit default value try to get the first
                    # option.
                    if prop.required:
                        try:
                            po = prop.options.all()[0]
                        except IndexError:
                            continue
                        else:
                            try:
                                price += po.price
                            except TypeError:
                                pass
                else:
                    try:
                        price += po.price
                    except TypeError:
                        pass

        return price

    def get_price_calculator(self, request):
        """
        Returns the price calculator class as defined in LFS_PRICE_CALCULATORS
        in settings.
        """
        if self.is_variant() and (self.price_calculator is None):
            obj = self.get_parent()
        else:
            obj = self

        if obj.price_calculator is not None:
            price_calculator = obj.price_calculator
        else:
            price_calculator = lfs.core.utils.get_default_shop(request).price_calculator

        price_calculator_class = lfs.core.utils.import_symbol(price_calculator)
        return price_calculator_class(request, self)

    def get_price(self, request, with_properties=True, amount=1):
        """
        See lfs.plugins.PriceCalculator
        """
        pc = self.get_price_calculator(request)
        return pc.get_price(with_properties, amount)

    def get_price_net(self, request, with_properties=True, amount=1):
        """
        See lfs.plugins.PriceCalculator
        """
        pc = self.get_price_calculator(request)
        return pc.get_price_net(with_properties, amount)

    def get_price_gross(self, request, with_properties=True, amount=1):
        """
        See lfs.plugins.PriceCalculator
        """
        pc = self.get_price_calculator(request)
        return pc.get_price_gross(with_properties, amount)

    def get_standard_price(self, request, with_properties=True, amount=1):
        """
        See lfs.plugins.PriceCalculator
        """
        pc = self.get_price_calculator(request)
        return pc.get_standard_price(with_properties, amount)

    def get_standard_price_net(self, request, with_properties=True, amount=1):
        """
        See lfs.plugins.PriceCalculator
        """
        pc = self.get_price_calculator(request)
        return pc.get_standard_price_net(with_properties, amount)

    def get_standard_price_gross(self, request, with_properties=True, amount=1):
        """
        See lfs.plugins.PriceCalculator
        """
        pc = self.get_price_calculator(request)
        return pc.get_standard_price_gross(with_properties, amount)

    def get_for_sale_price(self, request, with_properties=True, amount=1):
        """
        See lfs.plugins.PriceCalculator
        """
        pc = self.get_price_calculator(request)
        return pc.get_for_sale_price(with_properties, amount)

    def get_for_sale_price_net(self, request, with_properties=True, amount=1):
        """
        See lfs.plugins.PriceCalculator
        """
        pc = self.get_price_calculator(request)
        return pc.get_for_sale_price_net(with_properties, amount)

    def get_for_sale_price_gross(self, request, with_properties=True, amount=1):
        """
        See lfs.plugins.PriceCalculator
        """
        pc = self.get_price_calculator(request)
        return pc.get_for_sale_price_gross(with_properties, amount)

    def get_base_price(self, request, with_properties=True, amount=1):
        """
        See lfs.plugins.PriceCalculator
        """
        pc = self.get_price_calculator(request)
        return pc.get_base_price(with_properties, amount)

    def get_base_price_net(self, request, with_properties=True, amount=1):
        """
        See lfs.plugins.PriceCalculator
        """
        pc = self.get_price_calculator(request)
        return pc.get_base_price_net(with_properties, amount)

    def get_base_price_gross(self, request, with_properties=True, amount=1):
        """
        See lfs.plugins.PriceCalculator
        """
        pc = self.get_price_calculator(request)
        return pc.get_base_price_gross(with_properties, amount)

    def get_product_tax_rate(self, request=None):
        """
        See lfs.plugins.PriceCalculator
        """
        pc = self.get_price_calculator(request)
        return pc.get_product_tax_rate()

    def get_product_tax(self, request=None):
        """
        See lfs.plugins.PriceCalculator
        """
        # TODO: Do we need this method at all?
        pc = self.get_price_calculator(request)
        return pc.get_product_tax()

    def get_tax_rate(self, request):
        """
        See lfs.plugins.PriceCalculator
        """
        pc = self.get_price_calculator(request)
        return pc.get_customer_tax_rate()

    def get_tax(self, request):
        """
        See lfs.plugins.PriceCalculator
        """
        pc = self.get_price_calculator(request)
        return pc.get_customer_tax()

    def price_includes_tax(self, request=None):
        """
        See lfs.plugins.PriceCalculator
        """
        pc = self.get_price_calculator(request)
        return pc.price_includes_tax()

    def get_price_unit(self):
        """
        Returns the price_unit of the product. Takes care whether the product is
        a variant or not.
        """
        if self.is_variant():
            return self.parent.price_unit
        else:
            return self.price_unit

    def get_unit(self):
        """
        Returns the unit of the product. Takes care whether the product is a
        variant or not.
        """
        if self.is_variant():
            return self.parent.unit
        else:
            return self.unit

    def get_global_properties(self):
        """
        Returns all global properties for the product.
        """
        properties = []
        for property_group in self.property_groups.all():
            for prop in property_group.properties.order_by("groupspropertiesrelation"):
                properties.append({"property_group": property_group, "property": prop})

        return properties

    def get_local_properties(self):
        """
        Returns local properties of the product
        """
        return [
            {"property_group": None, "property": prop}
            for prop in self.properties.order_by("productspropertiesrelation")
        ]

    def get_properties(self):
        """
        Returns local and global properties
        """
        properties = self.get_global_properties()
        properties.extend(self.get_local_properties())

        properties.sort(key=lambda a: a["property"].position)

        return properties

    def get_variants_properties(self):
        """
        Returns all properties which are `select types`.
        """
        # global
        properties = []
        for property_group in self.property_groups.all():
            for prop in property_group.properties.filter(type=PROPERTY_SELECT_FIELD, variants=True).order_by(
                "groupspropertiesrelation"
            ):
                properties.append({"property_group": property_group, "property": prop})

        # local
        for prop in self.properties.filter(type=PROPERTY_SELECT_FIELD).order_by("productspropertiesrelation"):
            properties.append({"property_group": None, "property": prop})

        return properties

    def get_configurable_properties(self):
        """
        Returns all properties which are configurable.
        """
        # global
        properties = []
        for property_group in self.property_groups.all():
            for prop in property_group.properties.filter(configurable=True).order_by("groupspropertiesrelation"):
                properties.append({"property_group": property_group, "property": prop})

        # local
        for prop in self.properties.filter(configurable=True).order_by("productspropertiesrelation"):
            properties.append(prop)

        return properties

    def get_sku(self):
        """
        Returns the sku of the product. Takes care whether the product is a
        variant and sku is active or not.
        """
        if self.is_variant() and not self.active_sku:
            return self.parent.sku
        else:
            return self.sku

    def get_manufacturer(self):
        """
        Always return parent manufacturer for variants.
        """
        if self.is_variant():
            return self.parent.manufacturer
        else:
            return self.manufacturer

    def has_related_products(self):
        """
        Returns True if the product has related products.
        """
        return len(self.get_related_products()) > 0

    def get_related_products(self):
        """
        Returns the related products of the product.
        """
        cache_key = "%s-related-products-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, self.id)
        related_products = cache.get(cache_key)

        if related_products is None:
            if self.is_variant() and not self.active_related_products:
                related_products = self.parent.related_products.filter(active=True)
            else:
                related_products = self.related_products.filter(active=True)

            cache.set(cache_key, related_products)

        return related_products

    def get_default_variant(self):
        """
        Returns the default variant, which is supposed to be displayed within
        the product view.

        This is either a selected variant or the first added variant. If the
        product has no variants it is None.
        """
        cache_key = "%s-default-variant-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, self.id)
        default_variant = cache.get(cache_key)

        if default_variant is not None:
            return default_variant

        if self.default_variant is not None:
            default_variant = self.default_variant
        elif self.is_product_with_variants():
            try:
                default_variant = self.variants.filter(active=True)[0]
            except IndexError:
                return None

        cache.set(cache_key, default_variant)
        return default_variant

    def get_variant_for_category(self, request):
        """
        Returns the variant which is supposed to be displayed within category
        view.

        This is either the cheapest variant, the default variant, an explicitly
        selected one or None.
        """
        if self.category_variant == CATEGORY_VARIANT_CHEAPEST_PRICE:
            return self.get_cheapest_variant(request)
        elif self.category_variant == CATEGORY_VARIANT_CHEAPEST_BASE_PRICE:
            return self.get_cheapest_variant_by_base_price(request)
        elif self.category_variant == CATEGORY_VARIANT_CHEAPEST_PRICES:
            return self.get_default_variant()
        elif self.category_variant == CATEGORY_VARIANT_DEFAULT:
            return self.get_default_variant()
        elif self.category_variant is None:
            return self.get_default_variant()
        else:
            try:
                return Product.objects.get(pk=self.category_variant)
            except Product.DoesNotExist:
                return self.get_default_variant()

    def get_cheapest_variant(self, request):
        """
        Returns the cheapest variant by gross price.
        """
        cheapest_variant = None
        min_price = None
        for variant in Product.objects.filter(parent=self):
            price = variant.get_price_gross(request)
            if price == 0:
                continue
            if (min_price is None) or (price < min_price):
                cheapest_variant = variant
                min_price = price

        return cheapest_variant

    def get_cheapest_variant_by_base_price(self, request):
        """
        Returns the cheapest variant by base gross price.
        """
        cheapest_variant = None
        min_price = None
        for variant in Product.objects.filter(parent=self):
            price = variant.get_base_price_gross(request, amount=sys.maxsize)
            if price == 0:
                continue
            if (min_price is None) or (price < min_price):
                cheapest_variant = variant
                min_price = price

        return cheapest_variant

    def get_cheapest_for_sale_price_gross(self, request):
        """
        Returns the min price and min base price as dict.
        """
        product = self.get_parent()

        prices = []
        for variant in Product.objects.filter(parent=product, active=True):
            price = variant.get_for_sale_price_gross(request, amount=sys.maxsize)
            if price not in prices:
                prices.append(price)

        try:
            price = min(prices)
        except ValueError:
            price = 0

        return {
            "price": price,
            "starting_from": len(prices) > 1,
        }

    def get_cheapest_standard_price_gross(self, request):
        """
        Returns the min price and min base price as dict.
        """
        prices = []
        for variant in Product.objects.filter(parent=self, active=True):
            price = variant.get_standard_price_gross(request, amount=sys.maxsize)
            if price not in prices:
                prices.append(price)

        try:
            price = min(prices)
        except ValueError:
            price = 0

        return {
            "price": price,
            "starting_from": len(prices) > 1,
        }

    def get_cheapest_price_gross(self, request):
        """
        Returns the min price and min base price as dict.
        """
        prices = []
        for variant in Product.objects.filter(parent=self, active=True):
            price = variant.get_price_gross(request, amount=sys.maxsize)
            if price not in prices:
                prices.append(price)

        try:
            price = min(prices)
        except ValueError:
            price = 0

        return {
            "price": price,
            "starting_from": len(prices) > 1,
        }

    def get_cheapest_base_price_gross(self, request):
        """
        Returns the min price and min base price as dict.
        """
        prices = []
        for variant in Product.objects.filter(parent=self, active=True):
            price = float("%.2f" % variant.get_base_price_gross(request, amount=sys.maxsize))
            if price not in prices:
                prices.append(price)
        try:
            price = min(prices)
        except ValueError:
            price = 0

        return {
            "price": price,
            "starting_from": len(prices) > 1,
        }

    def get_static_block(self):
        """
        Returns the static block of the product. Takes care whether the product
        is a variant and meta description are active or not.
        """
        cache_key = "%s-product-static-block-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, self.id)
        block = cache.get(cache_key)
        if block is not None:
            return block

        if self.is_variant() and not self.active_static_block:
            block = self.parent.static_block
        else:
            block = self.static_block

        cache.set(cache_key, block)

        return block

    def get_variants(self):
        """
        Returns the variants of the product.
        """
        return self.variants.filter(active=True).order_by("variant_position")

    def has_variants(self):
        """
        Returns True if the product has variants.
        """
        return len(self.get_variants()) > 0

    def get_variant(self, options, only_active=True):
        """
        Returns the variant with the given options or None.

        The format of the passed properties/options must be tuple as following:

            [property.id|option.id]
            [property.id|option.id]
            ...

        NOTE: These are strings as we get the properties/options pairs out of
        the request and it wouldn't make a lot of sense to convert them to
        objects and back to strings.
        """
        options.sort()
        parsed_options = []
        # remove option with empty option_id (this means that variant doesn't have such property)
        for option in options:
            if option.find("|") == len(option) - 1:
                continue
            parsed_options.append(option)
        options = "".join(parsed_options)

        variants = self.variants.all()
        if only_active:
            variants = variants.filter(active=True)

        for variant in variants:
            temp = variant.property_values.filter(type=PROPERTY_VALUE_TYPE_VARIANT)
            temp = [
                "%s|%s|%s" % (x.property_group_id if x.property_group_id else 0, x.property_id, x.value) for x in temp
            ]
            temp.sort()
            temp = "".join(temp)

            if temp == options:
                return variant

        return None

    def has_variant(self, options, only_active=True):
        """
        Returns true if a variant with given options already exists.
        """
        if self.get_variant(options, only_active=only_active) is None:
            return False
        else:
            return True

    # Dimensions
    def get_weight(self):
        """
        Returns weight of the product. Takes care whether the product is a
        variant and meta description are active or not.
        """
        if self.is_variant() and not self.active_dimensions:
            return self.parent.weight
        else:
            return self.weight

    def get_width(self):
        """
        Returns width of the product. Takes care whether the product is a
        variant and meta description are active or not.
        """
        if self.is_variant() and not self.active_dimensions:
            return self.parent.width
        else:
            return self.width

    def get_length(self):
        """
        Returns length of the product. Takes care whether the product is a
        variant and meta description are active or not.
        """
        if self.is_variant() and not self.active_dimensions:
            return self.parent.length
        else:
            return self.length

    def get_height(self):
        """
        Returns height of the product. Takes care whether the product is a
        variant and meta description are active or not.
        """
        if self.is_variant() and not self.active_dimensions:
            return self.parent.height
        else:
            return self.height

    def get_active_packing_unit(self):
        """
        Returns True if the packing unit is active. Takes variant into accounts.
        """
        if self.is_variant():
            if self.active_packing_unit == CHOICES_STANDARD:
                return self.parent.get_active_packing_unit()
            else:
                return self.active_packing_unit == CHOICES_YES
        else:
            return self.active_packing_unit in (1, CHOICES_YES)

    def get_packing_info(self):
        """
        Returns the packing info of the product as list. Takes variants into
        account.
        """
        if self.is_variant() and self.active_packing_unit == CHOICES_STANDARD:
            obj = self.parent
        else:
            obj = self

        return (obj.packing_unit, obj.packing_unit_unit)

    def is_standard(self):
        """
        Returns True if product is standard product.
        """
        return self.sub_type == STANDARD_PRODUCT

    def is_configurable_product(self):
        """
        Returns True if product is configurable product.
        """
        return self.sub_type == CONFIGURABLE_PRODUCT

    def is_product_with_variants(self):
        """
        Returns True if product is product with variants.
        """
        return self.sub_type == PRODUCT_WITH_VARIANTS

    def get_parent(self):
        if self.is_variant():
            return self.parent
        return self

    def is_variant(self):
        """
        Returns True if product is variant.
        """
        return self.sub_type == VARIANT

    def is_active(self):
        """
        Returns the activity state of the product.
        """
        if self.is_variant():
            return self.active and self.parent.active
        else:
            return self.active

    def is_deliverable(self):
        """
        Returns the deliverable state of the product.
        """
        if self.manage_stock_amount and self.stock_amount <= 0 and not self.order_time:
            return False
        else:
            if self.is_variant():
                return self.deliverable and self.parent.deliverable
            else:
                return self.deliverable

    def get_manual_delivery_time(self):
        """
        Returns the manual delivery time of a product or None.
        """
        if self.manual_delivery_time:
            return self.delivery_time

        if self.is_variant() and self.parent.manual_delivery_time:
            return self.parent.delivery_time

        return None

    def get_clean_quantity_value(self, quantity=1, allow_zero=False):
        """
        Returns the valid quantity based on the product's type of
        quantity field.
        """
        try:
            quantity = abs(core_utils.atof(str(quantity)))
        except (TypeError, ValueError):
            quantity = 1.0

        if not allow_zero:
            quantity = 1 if quantity <= 0 else quantity

        type_of_quantity_field = self.get_type_of_quantity_field()
        if type_of_quantity_field == QUANTITY_FIELD_INTEGER or getattr(settings, "LFS_FORCE_INTEGER_QUANTITY", False):
            quantity = int(quantity)

        return quantity

    def get_clean_quantity(self, quantity=1):
        """
        Returns the correct formatted quantity based on the product's type of
        quantity field.
        """
        try:
            quantity = abs(core_utils.atof(str(quantity)))
        except (TypeError, ValueError):
            quantity = 1.0

        type_of_quantity_field = self.get_type_of_quantity_field()
        if type_of_quantity_field == QUANTITY_FIELD_INTEGER:
            quantity = int(quantity)
        elif type_of_quantity_field == QUANTITY_FIELD_DECIMAL_1:
            quantity = formats.localize(float("%.1f" % quantity))
        else:
            quantity = formats.localize(float("%.2f" % quantity))

        return quantity

    def get_type_of_quantity_field(self):
        """
        Returns the type of quantity field.
        """
        if self.is_variant():
            obj = self.parent
        else:
            obj = self

        if obj.type_of_quantity_field:
            return obj.type_of_quantity_field
        else:
            return QUANTITY_FIELD_INTEGER

    # 3rd party contracts
    def get_parent_for_portlets(self):
        """
        Returns the current category. This will add the portlets of the current
        category to the product portlets.
        """
        if self.is_variant():
            return self.parent
        else:
            # TODO Return the current category
            try:
                return self.categories.all()[0]
            except:
                return None

    def get_template_name(self):
        """
        Method to return the path of the product template
        """
        if self.template is not None:
            tmpl_id = int(self.template)
            return PRODUCT_TEMPLATES[tmpl_id]["file"]
        return None


class ProductAccessories(models.Model):
    """
    Represents the relationship between products and accessories.

    An accessory is just another product which is displayed within a product and
    which can be added to the cart together with it.

    Using an explicit class here to store the position of an accessory within
    a product.

    **Attributes:**

    product
        The product of the relationship.

    accessory
        The accessory of the relationship (which is also a product)

    position
        The position of the accessory within the product.

    quantity
        The proposed amount of accessories for the product.
    """

    product = models.ForeignKey(
        "Product", models.CASCADE, verbose_name=_("Product"), related_name="productaccessories_product"
    )
    accessory = models.ForeignKey(
        "Product", models.CASCADE, verbose_name=_("Accessory"), related_name="productaccessories_accessory"
    )
    position = models.IntegerField(_("Position"), default=999)
    quantity = models.FloatField(_("Quantity"), default=1)

    class Meta:
        ordering = ("position",)
        verbose_name_plural = "Product accessories"
        app_label = "catalog"

    def __str__(self):
        return "%s -> %s" % (self.product.name, self.accessory.name)

    def get_price(self, request):
        """
        Returns the total price of the accessory based on the product price and
        the quantity in which the accessory is offered.
        """
        return self.accessory.get_price(request) * self.quantity


class PropertyGroup(models.Model):
    """
    Groups product properties together.

    Can belong to several products, products can have several groups.

    **Attributes:**

    name
        The name of the property group.

    products
          The assigned products of the property group.
    """

    name = models.CharField(_("Name"), blank=True, max_length=50)
    products = models.ManyToManyField(Product, verbose_name=_("Products"), related_name="property_groups")
    position = models.IntegerField(_("Position"), default=1000)
    uid = models.CharField(max_length=50, editable=False, unique=True, default=get_unique_id_str)

    class Meta:
        ordering = ("position",)
        app_label = "catalog"

    def __str__(self):
        return self.name

    def get_configurable_properties(self):
        """
        Returns all configurable properties of the property group.
        """
        return self.properties.filter(configurable=True)

    def get_filterable_properties(self):
        """
        Returns all filterable properties of the property group.
        """
        return self.properties.filter(filterable=True)


class Property(models.Model):
    """
    Represents a property of a product like color or size.

    A property has several ``PropertyOptions`` from which the user can choose
    (like red, green, blue).

    A property belongs to exactly one group xor product.

    **Parameters**:

    groups, product:
        The group or product it belongs to. A property can belong to several
        groups and/or to one product.

    name:
        Internal name of the property.

    title:
        Displayed to the customer.

    position:
        The position of the property within the management interface.

    variants
        if True the property is used to create variants

    filterable:
        If True the property is used for filtered navigation.

    configurable
        if True the property is used for configurable product.

    display_on_product
        If True the property is displayed as an attribute on the product.

    unit:
        Something like cm, mm, m, etc.

    local
        If True the property belongs to exactly one product

    type
       char field, number field or select field

    step
       manual step for filtering

    price
        The price of the property. Only used for configurable products.

    unit_min
        The minimal unit of the property the shop customer can enter.

    unit_max
        The maximal unit of the property the shop customer can enter.

    unit_step
        The step width the shop customer can edit.

    decimal_places
        The decimal places of a number field.

    required
        If True the field is required (for configurable properties).

    display_price
        If True the option price is displayed (for select field)

    add_price
        if True the option price is added to the product price (for select
        field)

    """

    name = models.CharField(_("Name"), max_length=100)
    title = models.CharField(_("Title"), max_length=100)
    groups = models.ManyToManyField(
        PropertyGroup,
        verbose_name=_("Group"),
        blank=True,
        through="GroupsPropertiesRelation",
        related_name="properties",
    )
    products = models.ManyToManyField(
        Product, verbose_name=_("Products"), blank=True, through="ProductsPropertiesRelation", related_name="properties"
    )
    position = models.IntegerField(_("Position"), blank=True, null=True)
    unit = models.CharField(_("Unit"), blank=True, max_length=15, default="")
    display_on_product = models.BooleanField(_("Display on product"), default=False)
    local = models.BooleanField(_("Local"), default=False)
    variants = models.BooleanField(_("For Variants"), default=False)
    filterable = models.BooleanField(_("Filterable"), default=False)
    configurable = models.BooleanField(_("Configurable"), default=False)
    type = models.PositiveSmallIntegerField(_("Type"), choices=PROPERTY_FIELD_CHOICES, default=PROPERTY_TEXT_FIELD)
    price = models.FloatField(_("Price"), blank=True, null=True)
    display_price = models.BooleanField(_("Display price"), default=True)
    add_price = models.BooleanField(_("Add price"), default=True)

    # Number input field
    unit_min = models.FloatField(_("Min"), blank=True, null=True)
    unit_max = models.FloatField(_("Max"), blank=True, null=True)
    unit_step = models.FloatField(_("Step"), blank=True, null=True)
    decimal_places = models.PositiveSmallIntegerField(_("Decimal places"), default=0)

    required = models.BooleanField(_("Required"), default=False)

    step_type = models.PositiveSmallIntegerField(
        _("Step type"), choices=PROPERTY_STEP_TYPE_CHOICES, default=PROPERTY_STEP_TYPE_AUTOMATIC
    )
    step = models.IntegerField(_("Step"), blank=True, null=True)

    uid = models.CharField(max_length=50, editable=False, unique=True, default=get_unique_id_str)

    class Meta:
        verbose_name_plural = _("Properties")
        ordering = ["position"]
        app_label = "catalog"

    def __str__(self):
        return self.name

    @property
    def is_select_field(self):
        return self.type == PROPERTY_SELECT_FIELD

    @property
    def is_text_field(self):
        return self.type == PROPERTY_TEXT_FIELD

    @property
    def is_number_field(self):
        return self.type == PROPERTY_NUMBER_FIELD

    @property
    def is_range_step_type(self):
        return self.step_type == PROPERTY_STEP_TYPE_FIXED_STEP

    @property
    def is_automatic_step_type(self):
        return self.step_type == PROPERTY_STEP_TYPE_AUTOMATIC

    @property
    def is_steps_step_type(self):
        return self.step_type == PROPERTY_STEP_TYPE_MANUAL_STEPS

    def is_valid_value(self, value):
        """
        Returns True if given value is valid for this property.
        """
        if self.is_number_field:
            try:
                float(value)
            except ValueError:
                return False
        return True


class FilterStep(models.Model):
    """
    A step to build filter ranges for a property.

    **Parameters:**

    property
        The property the Step belongs to

    start
        The start of the range. The end will be calculated from the start of the
        next step
    """

    property = models.ForeignKey(Property, models.CASCADE, verbose_name=_("Property"), related_name="steps")
    start = models.FloatField()

    class Meta:
        ordering = ["start"]
        app_label = "catalog"

    def __str__(self):
        return "%s %s" % (self.property.name, self.start)


class GroupsPropertiesRelation(models.Model):
    """
    Represents the m:n relationship between Groups and Properties.

    This is done via an explicit class to store the position of the property
    within the group.

    **Attributes:**

    group
        The property group the property belongs to.

    property
        The property of question of the relationship.

    position
        The position of the property within the group.
    """

    group = models.ForeignKey(PropertyGroup, models.CASCADE, verbose_name=_("Group"), related_name="groupproperties")
    property = models.ForeignKey(Property, models.CASCADE, verbose_name=_("Property"))
    position = models.IntegerField(_("Position"), default=999)

    class Meta:
        ordering = ("position",)
        unique_together = ("group", "property")
        app_label = "catalog"


class ProductsPropertiesRelation(models.Model):
    """
    Represents the m:n relationship between Products and Properties.

    This is done via an explicit class to store the position of the property
    within the product.

    **Attributes:**

    product
        The product of the relationship.

    property
        The property of the relationship.

    position
        The position of the property within the product.

    """

    product = models.ForeignKey(Product, models.CASCADE, verbose_name=_("Product"), related_name="productsproperties")
    property = models.ForeignKey(Property, models.CASCADE, verbose_name=_("Property"))
    position = models.IntegerField(_("Position"), default=999)

    class Meta:
        ordering = ("position",)
        unique_together = ("product", "property")
        app_label = "catalog"


class PropertyOption(models.Model):
    """
    Represents a choosable option of a ``Property`` like red, green, blue.

    A property option can have an optional price (which could change the total
    price of a product).

    **Attributes:**

    property
        The property to which the option belongs

    name
        The name of the option

    price (Not used at the moment)
        The price for the option. This might be used for ``configurable
        products``

    position
        The position of the option within the property

    """

    property = models.ForeignKey(Property, models.CASCADE, verbose_name=_("Property"), related_name="options")

    name = models.CharField(_("Name"), max_length=100)
    price = models.FloatField(_("Price"), blank=True, null=True, default=0.0)
    position = models.IntegerField(_("Position"), default=99)

    uid = models.CharField(max_length=50, editable=False, unique=True, default=get_unique_id_str)

    class Meta:
        ordering = ["position"]
        app_label = "catalog"

    def __str__(self):
        return self.name


class ProductPropertyValue(models.Model):
    """
    Stores the value resp. selected option of a product/property combination.
    This is some kind of EAV.

    **Attributes:**

    product
        The product for which the value is stored.

    parent_id
        If the product is an variant this stores the parent id of it, if the
        product is no variant it stores the id of the product itself. This is
        just used to calculate the filters properly.

    property
        The property for which the value is stored.

    property_group
        The property group for which the value is stored, if none then it's a local property

    value
        The value for the product/property pair. Dependent of the property
        type the value is either a number, a text or an id of an option.

    type
        The type of the product value, which is one of "filter value",
        "default value", "display value", "variant value".
    """

    product = models.ForeignKey(Product, models.CASCADE, verbose_name=_("Product"), related_name="property_values")
    parent_id = models.IntegerField(_("Parent"), blank=True, null=True)
    property = models.ForeignKey("Property", models.CASCADE, verbose_name=_("Property"), related_name="property_values")
    property_group = models.ForeignKey(
        "PropertyGroup",
        models.SET_NULL,
        verbose_name=_("Property group"),
        blank=True,
        null=True,
        related_name="property_values",
    )
    value = models.CharField(_("Value"), blank=True, max_length=100)
    value_as_float = models.FloatField(_("Value as float"), blank=True, null=True)
    type = models.PositiveSmallIntegerField(_("Type"))

    class Meta:
        unique_together = ("product", "property", "property_group", "value", "type")
        app_label = "catalog"

    def __str__(self):
        property_group_name = self.property_group.name if self.property_group_id else ""
        return "%s/%s/%s: %s" % (self.product.get_name(), property_group_name, self.property.name, self.value)

    def save(self, *args, **kwargs):
        """
        Overwritten to save the parent id for variants. This is used to count
        the entries per filter. See catalog/utils/get_product_filters for more.
        """
        if self.product.is_variant():
            self.parent_id = self.product.parent.id
        else:
            self.parent_id = self.product.id

        try:
            float(self.value)
        except ValueError:
            pass
        else:
            self.value_as_float = self.value

        super(ProductPropertyValue, self).save(*args, **kwargs)


class Image(models.Model):
    """
    An image with a title and several sizes. Can be part of a product or
    category.

    **Attributes:**

    content
        The content object it belongs to.

    title
        The title of the image.

    alt
        The alt tag of the image

    image
        The image file.

    position
        The position of the image within the content object it belongs to.

    """

    content_type = models.ForeignKey(
        ContentType, models.CASCADE, verbose_name=_("Content type"), related_name="image", blank=True, null=True
    )
    content_id = models.PositiveIntegerField(_("Content id"), blank=True, null=True)
    content = GenericForeignKey(ct_field="content_type", fk_field="content_id")

    title = models.CharField(_("Title"), blank=True, max_length=100)
    alt = models.CharField(_("Alt"), blank=True, max_length=255)
    image = ImageWithThumbsField(
        _("Image"), upload_to="images", blank=True, null=True, max_length=120, sizes=THUMBNAIL_SIZES
    )
    position = models.PositiveSmallIntegerField(_("Position"), default=999)

    class Meta:
        ordering = ("position",)
        app_label = "catalog"

    def __str__(self):
        return self.title

    def get_alt(self):
        if self.alt:
            return self.alt
        return self.title


class File(models.Model):
    """
    A downloadable file.

    **Attributes:**

    title
        The title of the image. Used within the title tag of the file.

    slug
        The URL of the file.

    content
        The content object the file belongs to (optional).

    position
        The ordinal number within the content object. Used to order the files.

    description
        A long description of the file. Can be used within the content
        (optional).

    file
        The binary file.
    """

    title = models.CharField(blank=True, max_length=100)
    slug = models.SlugField()

    content_type = models.ForeignKey(
        ContentType, models.SET_NULL, verbose_name=_("Content type"), related_name="files", blank=True, null=True
    )
    content_id = models.PositiveIntegerField(_("Content id"), blank=True, null=True)
    content = GenericForeignKey(ct_field="content_type", fk_field="content_id")

    position = models.SmallIntegerField(default=999)
    description = models.CharField(blank=True, max_length=100)
    file = models.FileField(upload_to="files")

    class Meta:
        ordering = ("position",)
        app_label = "catalog"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("lfs_file", kwargs={"file_id": self.id})


class StaticBlock(models.Model):
    """
    A block of static HTML which can be assigned to content objects.

    **Attributes**:

    name
        The name of the static block.

    html
        The static HTML of the block.

    display_files
        If True the files are displayed for download within the static block.

    files
        The files of the static block.

    position
        Position to sort the static blocks
    """

    name = models.CharField(_("Name"), max_length=30)
    display_files = models.BooleanField(_("Display files"), default=True)
    html = models.TextField(_("HTML"), blank=True)
    files = GenericRelation(
        File, verbose_name=_("Files"), object_id_field="content_id", content_type_field="content_type"
    )
    position = models.SmallIntegerField(_("Position"), default=1000)

    class Meta:
        ordering = ("position",)
        app_label = "catalog"

    def __str__(self):
        return self.name


class DeliveryTimeBase(models.Model):
    """
    Selectable delivery times.

    **Attributes:**

    min
        The minimal lasting of the delivery date.

    max
        The maximal lasting of the delivery date.

    unit
        The unit of the delivery date, e.g. days, months.

    description
        A short description for internal uses.

    """

    min = models.FloatField(_("Min"))
    max = models.FloatField(_("Max"))
    unit = models.PositiveSmallIntegerField(
        _("Unit"), choices=DELIVERY_TIME_UNIT_CHOICES, default=DELIVERY_TIME_UNIT_DAYS
    )
    description = models.TextField(_("Description"), blank=True)

    class Meta:
        ordering = ("min",)
        abstract = True

    def __str__(self):
        return self.round().as_string()

    def _get_instance(self, min, max, unit):
        return self.__class__(min=min, max=max, unit=unit)

    def __gt__(self, other):
        if self.max > other.max:
            return True
        return False

    def __add__(self, other):
        """
        Adds to delivery times.
        """
        # If necessary we transform both delivery times to the same base (hours)
        if self.unit != other.unit:
            a = self.as_hours()
            b = other.as_hours()
            unit_new = DELIVERY_TIME_UNIT_HOURS
        else:
            a = self
            b = other
            unit_new = self.unit

        # Now we can add both
        min_new = a.min + b.min
        max_new = a.max + b.max
        unit_new = a.unit

        return self._get_instance(min=min_new, max=max_new, unit=unit_new)

    @property
    def name(self):
        """
        Returns the name of the delivery time
        """
        return self.round().as_string()

    def subtract_days(self, days):
        """
        Substract the given days from delivery time's min and max. Takes the
        unit into account.
        """
        if self.unit == DELIVERY_TIME_UNIT_HOURS:
            max_new = self.max - (24 * days)
            min_new = self.min - (24 * days)
        elif self.unit == DELIVERY_TIME_UNIT_DAYS:
            max_new = self.max - days
            min_new = self.min - days
        elif self.unit == DELIVERY_TIME_UNIT_WEEKS:
            max_new = self.max - (days / 7.0)
            min_new = self.min - (days / 7.0)
        elif self.unit == DELIVERY_TIME_UNIT_MONTHS:
            max_new = self.max - (days / 30.0)
            min_new = self.min - (days / 30.0)

        if min_new < 0:
            min_new = 0
        if max_new < 0:
            max_new = 0

        return self._get_instance(min=min_new, max=max_new, unit=self.unit)

    def as_hours(self):
        """
        Returns the delivery time in hours.
        """
        if self.unit == DELIVERY_TIME_UNIT_HOURS:
            max = self.max
            min = self.min
        elif self.unit == DELIVERY_TIME_UNIT_DAYS:
            max = self.max * 24
            min = self.min * 24
        elif self.unit == DELIVERY_TIME_UNIT_WEEKS:
            max = self.max * 24 * 7
            min = self.min * 24 * 7
        elif self.unit == DELIVERY_TIME_UNIT_MONTHS:
            max = self.max * 24 * 30
            min = self.min * 24 * 30

        return self._get_instance(min=min, max=max, unit=DELIVERY_TIME_UNIT_HOURS)

    def as_days(self):
        """
        Returns the delivery time in days.
        """
        if self.unit == DELIVERY_TIME_UNIT_HOURS:
            min = self.min / 24
            max = self.max / 24
        elif self.unit == DELIVERY_TIME_UNIT_DAYS:
            max = self.max
            min = self.min
        elif self.unit == DELIVERY_TIME_UNIT_WEEKS:
            max = self.max * 7
            min = self.min * 7
        elif self.unit == DELIVERY_TIME_UNIT_MONTHS:
            max = self.max * 30
            min = self.min * 30

        return self._get_instance(min=min, max=max, unit=DELIVERY_TIME_UNIT_DAYS)

    def as_weeks(self):
        """
        Returns the delivery time in weeks.
        """
        if self.unit == DELIVERY_TIME_UNIT_HOURS:
            min = self.min / (24 * 7)
            max = self.max / (24 * 7)
        elif self.unit == DELIVERY_TIME_UNIT_DAYS:
            max = self.max / 7
            min = self.min / 7
        elif self.unit == DELIVERY_TIME_UNIT_WEEKS:
            max = self.max
            min = self.min
        elif self.unit == DELIVERY_TIME_UNIT_MONTHS:
            max = self.max * 4
            min = self.min * 4

        return self._get_instance(min=min, max=max, unit=DELIVERY_TIME_UNIT_WEEKS)

    def as_months(self):
        """
        Returns the delivery time in months.
        """
        if self.unit == DELIVERY_TIME_UNIT_HOURS:
            min = self.min / (24 * 30)
            max = self.max / (24 * 30)
        elif self.unit == DELIVERY_TIME_UNIT_DAYS:
            max = self.max / 30
            min = self.min / 30
        elif self.unit == DELIVERY_TIME_UNIT_WEEKS:
            max = self.max / 4
            min = self.min / 4
        elif self.unit == DELIVERY_TIME_UNIT_MONTHS:
            max = self.max
            min = self.min

        return self._get_instance(min=int(min), max=int(max), unit=DELIVERY_TIME_UNIT_MONTHS)

    def as_reasonable_unit(self):
        """
        Returns the delivery time as reasonable unit based on the max hours.

        This is used to show the delivery time to the shop customer.
        """
        delivery_time = self.as_hours()

        if delivery_time.max > 1440:  # > 2 months
            return delivery_time.as_months()
        elif delivery_time.max > 168:  # > 1 week
            return delivery_time.as_weeks()
        elif delivery_time.max > 48:  # > 2 days
            return delivery_time.as_days()
        else:
            return delivery_time

    def as_string(self):
        """
        Returns the delivery time as string.
        """
        if self.min == 0:
            self.min = self.max

        if self.min == self.max:
            if self.min == 1:
                unit = DELIVERY_TIME_UNIT_SINGULAR[self.unit]
            else:
                unit = self.get_unit_display()

            return "%s %s" % (self.min, unit)
        else:
            return "%s-%s %s" % (self.min, self.max, self.get_unit_display())

    def round(self):
        """
        Rounds the min/max of the delivery time to an integer and returns a new
        DeliveryTime object.
        """
        min = int("%.0f" % (self.min + 0.001))
        max = int("%.0f" % (self.max + 0.001))

        return self._get_instance(min=min, max=max, unit=self.unit)


class DeliveryTime(DeliveryTimeBase):
    class Meta:
        ordering = ("min",)
        app_label = "catalog"


class ProductAttachment(models.Model):
    """
    Represents a downloadable attachment of a product.

    **Attributes:**

    title
        The title of the attachment

    description
        The description of the attachment

    file
        The downloadable file of the attachment

    product
        The product the attachment belongs to

    position
        The position of the attachment within a product.
    """

    title = models.CharField(_("Title"), max_length=60)
    description = models.TextField(_("Description"), blank=True)
    file = models.FileField(upload_to="files", max_length=500)
    product = models.ForeignKey(
        Product, models.SET_NULL, verbose_name=_("Product"), related_name="attachments", null=True, blank=True
    )
    position = models.IntegerField(_("Position"), default=1)

    class Meta:
        ordering = ("position",)
        app_label = "catalog"

    def get_url(self):
        if self.file.url:
            return self.file.url
        return None
