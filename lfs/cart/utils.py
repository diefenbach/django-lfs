# django imports
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.core.urlresolvers import reverse

# lfs imports
from lfs.cart.models import CartItem
from lfs.cart.models import Cart
from lfs.payment import utils as payment_utils
from lfs.shipping import utils as shipping_utils
from lfs.voucher.models import Voucher

# Load logger
import logging
logger = logging.getLogger("default")


def get_or_create_cart(request):
    """
    Returns the cart of the current user. If no cart exists yet it creates a
    new one first.
    """
    cart = get_cart(request)
    if cart is None:
        cart = create_cart(request)

    return cart


def create_cart(request):
    """
    Creates a cart for the current session and/or user.
    """
    if request.session.session_key is None:
        request.session.save()

    cart = Cart(session=request.session.session_key)
    if request.user.is_authenticated():
        cart.user = request.user

    cart.save()
    return cart


def get_cart(request):
    """
    Returns the cart of the current shop customer. if the customer has no cart
    yet it returns None.
    """
    session_key = request.session.session_key
    user = request.user

    if user.is_authenticated():
        try:
            cache_key = "%s-cart-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, user.pk)
            cart = cache.get(cache_key)
            if cart is None:
                cart = Cart.objects.get(user=user)
                cache.set(cache_key, cart)
            return cart
        except ObjectDoesNotExist:
            return None
    else:
        try:
            cache_key = "%s-cart-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, session_key)
            cart = cache.get(cache_key)
            if cart is None:
                cart = Cart.objects.get(session=session_key)
                cache.set(cache_key, cart)
            return cart
        except ObjectDoesNotExist:
            return None


def get_go_on_shopping_url(request):
    """
    Calculates the go on shopping url based on the last visited category or last visited manufacturer
    """
    # visiting category clears last_manufacturer so manufacturer has higher priority
    lc = request.session.get("last_manufacturer", request.session.get("last_category"))
    if lc:
        return lc.get_absolute_url()
    else:
        return reverse("lfs_shop_view")


def update_cart_after_login(request):
    """
    Updates the cart after login.

    1. if there is no session cart, nothing has to be done.
    2. if there is a session cart and no user cart we assign the session cart
       to the current user.
    3. if there is a session cart and a user cart we add the session cart items
       to the user cart.
    """
    try:
        session_cart = Cart.objects.get(session=request.session.session_key)
        try:
            user_cart = Cart.objects.get(user=request.user)
        except ObjectDoesNotExist:
            session_cart.user = request.user
            session_cart.save()
        else:
            for session_cart_item in session_cart.get_items():
                properties = {}
                for pv in session_cart_item.properties.all():
                    properties[unicode(pv.property.id)] = pv.value
                user_cart.add(session_cart_item.product, properties=properties, amount=session_cart_item.amount)
            session_cart.delete()
    except ObjectDoesNotExist:
        pass
