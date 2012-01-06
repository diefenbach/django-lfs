# django imports
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.catalog.models import Category
from lfs.catalog.models import Product
from lfs.export.settings import CATEGORY_VARIANTS_CHOICES
from lfs.export.settings import CATEGORY_VARIANTS_DEFAULT


class Export(models.Model):
    """An export of products.
    """
    name = models.CharField(_(u"Name"), max_length=100)
    slug = models.SlugField(_(u"Slug"), unique=True)
    products = models.ManyToManyField(Product, verbose_name=_(u"Products"), blank=True, related_name="exports")
    script = models.ForeignKey("Script", verbose_name=_(u"Script"))
    variants_option = models.PositiveSmallIntegerField(_(u"Variants"), choices=CATEGORY_VARIANTS_CHOICES[1:], default=CATEGORY_VARIANTS_DEFAULT)
    position = models.IntegerField(default=1)

    class Meta:
        ordering = ("position", "name")

    def __unicode__(self):
        return "%s.%s" % (self.module, self.method)

    def get_absolute_url(self):
        """
        """
        return reverse(
            "lfs_export", kwargs={"export_id": self.id})

    def get_products(self):
        """Returns selected products. Takes variant options into account.
        """
        import lfs.export.utils
        products = []

        for product in self.products.all():
            if product.is_product_with_variants():
                variants = lfs.export.utils.get_variants(product, self)
                if variants:
                    products.extend(variants)
            else:
                products.append(product)

        return products


class Script(models.Model):
    """Represents an export script for an Export
    """
    module = models.CharField(max_length=100, default="lfs.export.generic")
    method = models.CharField(max_length=100, default="export")
    name = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ("name", )
        unique_together = ("module", "method")


class CategoryOption(models.Model):
    """Stores options for categories.
    """
    category = models.ForeignKey(Category, verbose_name=_(u"Category"))
    export = models.ForeignKey(Export, verbose_name=_(u"Export"))
    variants_option = models.PositiveSmallIntegerField(_(u"Variant"), choices=CATEGORY_VARIANTS_CHOICES)
