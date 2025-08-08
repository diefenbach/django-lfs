# lfs imports
from lfs.cart.utils import get_cart
from lfs.checkout.settings import CHECKOUT_TYPE_ANON
from lfs.core.utils import get_default_shop
from django.conf import settings


def main(request):
    """context processor for lfs"""
    shop = get_default_shop(request)
    cart = get_cart(request)
    return {
        "SHOP": shop,
        "CART": cart,
        "ANON_ONLY": shop.checkout_type == CHECKOUT_TYPE_ANON,
        "LFS_DOCS": settings.LFS_DOCS,
    }
