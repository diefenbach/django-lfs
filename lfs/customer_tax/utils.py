# lfs imports
from lfs.customer.utils import get_customer
from lfs.customer_tax.models import CustomerTax


def get_customer_tax_rate(request, product):
    """Returns the specfic customer tax for the current customer and product.
    """
    customer = get_customer(request)

    try:
        shipping_country = customer.selected_shipping_address.country
    except AttributeError:
        return _calc_product_tax_rate(request, product)

    try:
        customer_tax = CustomerTax.objects.get(countries=shipping_country)
    except CustomerTax.DoesNotExist:
        return _calc_product_tax_rate(request, product)

    return customer_tax.rate


def _calc_product_tax_rate(request, product):
    try:
        return product.get_product_tax_rate(request)
    except AttributeError:
        return 0.0
