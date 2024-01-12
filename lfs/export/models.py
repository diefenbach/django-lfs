# django imports
from django.urls import reverse
from django.db import models
from django.utils.translation import gettext_lazy as _

# lfs imports
from lfs.catalog.models import Category
from lfs.catalog.models import Product
from lfs.export.settings import CATEGORY_VARIANTS_CHOICES
from lfs.export.settings import CATEGORY_VARIANTS_DEFAULT


class Export(models.Model):
    """An export of products."""

    name = models.CharField(_("Name"), max_length=100)
    slug = models.SlugField(_("Slug"), unique=True)
    products = models.ManyToManyField(Product, verbose_name=_("Products"), blank=True, related_name="exports")
    script = models.ForeignKey("Script", models.SET_NULL, verbose_name=_("Script"), blank=True, null=True)
    variants_option = models.PositiveSmallIntegerField(
        _("Variants"), choices=CATEGORY_VARIANTS_CHOICES[1:], default=CATEGORY_VARIANTS_DEFAULT
    )
    position = models.IntegerField(default=1)

    class Meta:
        ordering = ("position", "name")
        app_label = "export"

    def __str__(self):
        return "%s.%s" % (self.module, self.method)

    def get_absolute_url(self):
        """ """
        return reverse("lfs_export", kwargs={"export_id": self.id})

    def get_products(self):
        """Returns selected products. Takes variant options into account."""
        import lfs.export.utils

        products = []

        for product in self.products.all():
            products.append(product)
            if product.is_product_with_variants():
                variants = lfs.export.utils.get_variants(product, self)
                if variants:
                    products.extend(variants)

        return products


class Script(models.Model):
    """Represents an export script for an Export"""

    module = models.CharField(max_length=100, default="lfs.export.generic")
    method = models.CharField(max_length=100, default="export")
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("name",)
        unique_together = ("module", "method")
        app_label = "export"


class CategoryOption(models.Model):
    """Stores options for categories."""

    category = models.ForeignKey(Category, models.CASCADE, verbose_name=_("Category"))
    export = models.ForeignKey(Export, models.CASCADE, verbose_name=_("Export"))
    variants_option = models.PositiveSmallIntegerField(_("Variant"), choices=CATEGORY_VARIANTS_CHOICES)

    class Meta:
        app_label = "export"
