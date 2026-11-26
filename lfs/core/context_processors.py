# lfs imports
from lfs.cart.utils import get_cart
from lfs.checkout.settings import CHECKOUT_TYPE_ANON
from lfs.core.utils import get_default_shop
from django.urls import reverse
from lfs.settings import lfs_setting


def main(request):
    """context processor for lfs"""
    shop = get_default_shop(request)
    cart = get_cart(request)
    context = {
        "SHOP": shop,
        "CART": cart,
        "ANON_ONLY": shop.checkout_type == CHECKOUT_TYPE_ANON,
        "LFS_DOCS": lfs_setting("LFS_DOCS"),
    }
    match = request.resolver_match
    if match and match.url_name in {"lfs_shop_view", "lfs_page_view", "lfs_pages", "lfs_contact_form"}:
        context["canonical_url"] = request.build_absolute_uri(reverse(match.view_name, kwargs=match.kwargs))
    return context
