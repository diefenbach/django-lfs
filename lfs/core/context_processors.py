# lfs imports
from lfs.checkout.settings import CHECKOUT_TYPE_ANON
from lfs.core.utils import get_default_shop
from django.conf import settings


def main(request):
    """context processor for lfs
    """
    shop = get_default_shop(request)

    return {
        "SHOP": shop,
        "ANON_ONLY": shop.checkout_type == CHECKOUT_TYPE_ANON,
        "LFS_DOCS": settings.LFS_DOCS,
    }
