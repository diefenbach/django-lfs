# discounts imports
from lfs.discounts.models import Discount


def get_valid_discounts(request, product=None):
    """Returns all valid discounts as a list.
    """
    discounts = []
    for discount in Discount.objects.filter(active=True):
        if discount.is_valid(request, product):
            discounts.append({
                "id": discount.id,
                "name": discount.name,
                "sku": discount.sku,
                "price_net": discount.get_price_net(request, product),
                "price_gross": discount.get_price_gross(request, product),
                "tax": discount.get_tax(request, product),
                "sums_up": discount.sums_up
            })

    return discounts


def get_discounts_data(request, product=None):
    """ Calculate total value of discounts that sums up and find max discount that doesn't sum up
    """
    discounts = get_valid_discounts(request, product)

    summed_up_value = 0.0
    max_value = 0.0

    summed_up_discounts = []
    max_discount = None

    for discount in discounts:
        if discount['sums_up']:
            summed_up_value += discount['price_net']
            summed_up_discounts.append(discount)
        else:
            if max_value < discount['price_net']:
                max_value = discount['price_net']
                max_discount = discount

    return {'summed_up_discounts': summed_up_discounts,
            'max_discounts': [max_discount],
            'summed_up_value': summed_up_value,
            'max_value': max_value}
