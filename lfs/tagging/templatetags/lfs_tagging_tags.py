# django imports
from django import template
from django.conf import settings
from django.core.cache import cache

# lfs imports
from lfs.catalog.models import Product

register = template.Library()


@register.inclusion_tag('tagging/related_products_by_tags.html', takes_context=True)
def related_products_by_tags(context, product, num=None):
    """Inclusion tag for a list of related products by tags.
    """
    return _get_related_products_by_tags(product, num)


@register.inclusion_tag('tagging/related_products_by_tags_portlet.html', takes_context=True)
def related_products_by_tags_portlet(context, product, num=None):
    """Inclusion tag for a related products by tags portlet.
    """
    return _get_related_products_by_tags(product, num)


def _get_related_products_by_tags(product, num=None):
    """Returns a dict with related products by tags.
    """
    # Try to get it out of cache
    cache_key = "%s-related-products-by-tags-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, product.id)
    related_products = cache.get(cache_key)
    if related_products is not None:
        return {"related_products": related_products}

    # Create related products
    related_products = product.tags.similar_objects()

    # Save related_products within cache
    cache.set(cache_key, related_products)

    return {"related_products": related_products}
