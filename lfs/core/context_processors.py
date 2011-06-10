# lfs imports
from lfs.checkout.settings import CHECKOUT_TYPE_ANON
from lfs.core.utils import get_default_shop


def main(request):
    """context processor for lfs
    """
    shop = get_default_shop()

    return {
        "SHOP": shop,
        "ANON_ONLY": shop.checkout_type == CHECKOUT_TYPE_ANON,
    }
