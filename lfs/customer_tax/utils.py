# lfs imports
from lfs.criteria.utils import get_first_valid
from lfs.customer_tax.models import CustomerTax


def get_customer_tax_rate(request, product):
    """Returns the specfic customer tax for the current customer and product.
    """
    if hasattr(request, 'cached_customer_tax_rate'):
        return getattr(request, 'cached_customer_tax_rate')
    customer_tax = get_first_valid(request, CustomerTax.objects.all(), product)
    if customer_tax:
        taxrate = customer_tax.rate
    else:
        taxrate = _calc_product_tax_rate(request, product)
    setattr(request, 'cached_customer_tax_rate', taxrate)
    return taxrate


def _calc_product_tax_rate(request, product):
    try:
        return product.get_product_tax_rate(request)
    except AttributeError:
        return 0.0
