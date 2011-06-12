# django imports
from django import template
from django.conf import settings
from django.core.cache import cache

# lfs imports
from lfs.caching.utils import lfs_get_object_or_404
from lfs.catalog.models import Product

from tagging.models import TaggedItem

register = template.Library()


@register.inclusion_tag('tagging/related_products_by_tags.html', takes_context=True)
def related_products_by_tags(context, product_id, num=None):
    """Inclusion tag for a list of related products by tags.
    """
    return _get_related_products_by_tags(product_id, num)


@register.inclusion_tag('tagging/related_products_by_tags_portlet.html', takes_context=True)
def related_products_by_tags_portlet(context, product_id, num=None):
    """Inclusion tag for a related products by tags portlet.
    """
    return _get_related_products_by_tags(product_id, num)


def _get_related_products_by_tags(product_id, num=None):
    """Returns a dict with related products by tags.

    This is just a thin wrapper for the get_related method of the
    TaggedItem manager of the tagging product in order to provide caching.
    From the tagging product's doc string (mutatis mutantis):

    Returns a list of products which share tags with the product with passed id
    ordered by the number of shared tags in descending order.

    See there for more.
    """
    # Try to get it out of cache
    cache_key = "%s-related-products-by-tags-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, product_id)
    related_products = cache.get(cache_key)
    if related_products is not None:
        return {"related_products": related_products}

    # Create related products
    product = lfs_get_object_or_404(Product, pk=product_id)
    related_products = TaggedItem.objects.get_related(product, Product, num)

    # Save related_products within cache
    cache.set(cache_key, related_products)

    return {"related_products": related_products}
