# discounts imports
from lfs.discounts.models import Discount


def get_valid_discounts(request, product=None):
    """Returns all valid discounts as a list.
    """
    discounts = []
    for discount in Discount.objects.all():
        if discount.is_valid(request, product):
            discounts.append({
                "id": discount.id,
                "name": discount.name,
                "sku": discount.sku,
                "price": discount.get_price_gross(request, product),
                "tax": discount.get_tax(request, product)
            })

    return discounts
