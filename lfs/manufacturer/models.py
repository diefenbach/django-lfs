from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.core.cache import cache
from django.db import connection

from lfs.core.fields.thumbs import ImageWithThumbsField


class Manufacturer(models.Model):
    """The manufacturer is the unique creator of a product.
    """
    name = models.CharField(_(u"Name"), max_length=50)
    slug = models.SlugField(_(u"Slug"), unique=True)

    short_description = models.TextField(_(u"Short description"), blank=True)
    description = models.TextField(_(u"Description"), blank=True)
    image = ImageWithThumbsField(_(u"Image"), upload_to="images", blank=True, null=True, sizes=((60, 60), (100, 100), (200, 200), (400, 400)))
    position = models.IntegerField(_(u"Position"), default=1000)

    active_formats = models.BooleanField(_(u"Active formats"), default=False)

    product_rows = models.IntegerField(_(u"Product rows"), default=3)
    product_cols = models.IntegerField(_(u"Product cols"), default=3)

    meta_title = models.CharField(_(u"Meta title"), max_length=100, default="<name>")
    meta_keywords = models.TextField(_(u"Meta keywords"), blank=True)
    meta_description = models.TextField(_(u"Meta description"), blank=True)

    class Meta:
        ordering = ("name", )
        app_label = 'manufacturer'

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        """Returns the absolute url of the manufacturer
        """
        return reverse("lfs_manufacturer", kwargs={"slug": self.slug})

    def get_format_info(self):
        """Returns format information.
        """
        if self.active_formats is True:
            return {
                "product_cols": self.product_cols,
                "product_rows": self.product_rows
            }
        else:
            try:
                # TODO: Use cache here. Maybe we need a lfs_get_object,
                # which raise a ObjectDoesNotExist if the object does not
                # exist
                from lfs.core.models import Shop
                shop = Shop.objects.get(pk=1)
            except ObjectDoesNotExist:
                return {
                    "product_cols": 3,
                    "product_rows": 3
                }
            else:
                return {
                    "product_cols": shop.product_cols,
                    "product_rows": shop.product_rows
                }

    def get_meta_title(self):
        """Returns the meta keywords of the catgory.
        """
        mt = self.meta_title.replace("<name>", self.name)
        return mt

    def get_meta_keywords(self):
        """Returns the meta keywords of the catgory.
        """
        mk = self.meta_keywords.replace("<name>", self.name)
        mk = mk.replace("<short-description>", self.short_description)
        return mk

    def get_meta_description(self):
        """Returns the meta description of the product.
        """
        md = self.meta_description.replace("<name>", self.name)
        md = md.replace("<short-description>", self.short_description)
        return md

    def get_image(self):
        """Returns the image of the category if it has none it inherits that
        from the parent category.
        """
        if self.image:
            return self.image
        return None

    def get_all_products(self):
        """Returns all products for manufacturer
        """
        from lfs.catalog.settings import VARIANT

        cache_key = "%s-manufacturer-all-products-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, self.id)
        products = cache.get(cache_key)
        if products is not None:
            return products

        products = self.products.filter(active=True).exclude(sub_type=VARIANT).distinct()

        cache.set(cache_key, products)
        return products

    def get_filtered_products(self, filters, price_filter, sorting):
        """Returns products for given categories and current filters sorted by
        current sorting.
        """
        from lfs.catalog.models import Product
        from lfs.catalog.settings import PROPERTY_VALUE_TYPE_FILTER

        products = self.get_all_products()
        if filters:
            # Generate ids for collected products
            product_ids = products.values_list('pk', flat=True)
            product_ids = ", ".join(product_ids)

            # Generate filter
            temp = []
            for f in filters:
                if not isinstance(f[1], (list, tuple)):
                    temp.append("property_id='%s' AND value='%s'" % (f[0], f[1]))
                else:
                    temp.append("property_id='%s' AND value_as_float BETWEEN '%s' AND '%s'" % (f[0], f[1][0], f[1][1]))

            fstr = " OR ".join(temp)

            # TODO: Will this work with every DB?

            # Get all product ids with matching filters. The idea behind this SQL
            # query is: If for every filter (property=value) for a product id exists
            # a "product property value" the product matches.
            cursor = connection.cursor()
            cursor.execute("""
                SELECT product_id, count(*)
                FROM catalog_productpropertyvalue
                WHERE product_id IN (%s) and (%s) and type=%s
                GROUP BY product_id
                HAVING count(*)=%s""" % (product_ids, fstr, PROPERTY_VALUE_TYPE_FILTER, len(filters)))

            matched_product_ids = [row[0] for row in cursor.fetchall()]

            # All variants of category products
            all_variants = Product.objects.filter(parent__in=products)

            if all_variants:
                all_variant_ids = [str(p.id) for p in all_variants]
                all_variant_ids = ", ".join(all_variant_ids)

                # Variants with matching filters
                cursor.execute("""
                    SELECT product_id, count(*)
                    FROM catalog_productpropertyvalue
                    WHERE product_id IN (%s) and %s and type=%s
                    GROUP BY product_id
                    HAVING count(*)=%s""" % (all_variant_ids, fstr, PROPERTY_VALUE_TYPE_FILTER, len(filters)))

                # Get the parent ids of the variants as the "product with variants"
                # should be displayed and not the variants.
                variant_ids = [str(row[0]) for row in cursor.fetchall()]
                if variant_ids:
                    variant_ids = ", ".join(variant_ids)

                    cursor.execute("""
                        SELECT parent_id
                        FROM catalog_product
                        WHERE id IN (%s)""" % variant_ids)

                    parent_ids = [str(row[0]) for row in cursor.fetchall()]
                    matched_product_ids.extend(parent_ids)

            # As we factored out the ids of all matching products now, we get the
            # product instances in the correct order
            products = Product.objects.filter(pk__in=matched_product_ids).distinct()

        if price_filter:
            matched_product_ids = []

            # Get all variants of the products
            variants = Product.objects.filter(parent__in=products)

            # Filter the variants by price
            variants = variants.filter(effective_price__range=[price_filter["min"], price_filter["max"]])

            # Get the parent ids of the variants as the "product with variants"
            # should be displayed and not the variants.
            if variants:
                variant_ids = [str(r.id) for r in variants]
                variant_ids = ", ".join(variant_ids)

                cursor = connection.cursor()
                cursor.execute("""
                    SELECT parent_id
                    FROM catalog_product
                    WHERE id IN (%s)""" % variant_ids)

                parent_ids = [str(row[0]) for row in cursor.fetchall()]
                matched_product_ids.extend(parent_ids)

            # Filter the products
            products = products.filter(effective_price__range=[price_filter["min"], price_filter["max"]])

            # Merge the results
            matched_product_ids.extend(products.values_list('pk', flat=True))

            # And get a new query set of all products
            products = Product.objects.filter(pk__in=matched_product_ids)

        if sorting:
            products = products.order_by(sorting)

        return products
