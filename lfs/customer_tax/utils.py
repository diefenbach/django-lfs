# lfs imports
from django.core.cache import cache
from lfs.criteria.utils import get_first_valid
from lfs.customer_tax.models import CustomerTax


def get_customer_tax_rate(request, product):
    """Returns the specfic customer tax for the current customer and product.
    """
    cache_key = 'cached_customer_tax_rate_%s' % product.pk
    if request and hasattr(request, cache_key):
        return getattr(request, cache_key)

    all_cache_key = u'all_customer_taxes'
    customer_taxes = cache.get(all_cache_key)
    if customer_taxes is None:
        customer_taxes = CustomerTax.objects.all()
        cache.set(all_cache_key, customer_taxes)

    customer_tax = get_first_valid(request, customer_taxes, product)
    if customer_tax:
        taxrate = customer_tax.rate
    else:
        taxrate = _calc_product_tax_rate(request, product)
    if request:
        setattr(request, cache_key, taxrate)
    return taxrate


def _calc_product_tax_rate(request, product):
    try:
        return product.get_product_tax_rate(request)
    except AttributeError:
        return 0.0
