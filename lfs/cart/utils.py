# django imports
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.core.urlresolvers import reverse

# lfs imports
from lfs.cart.models import CartItem
from lfs.cart.models import Cart
from lfs.payment import utils as payment_utils
from lfs.shipping import utils as shipping_utils
from lfs.voucher.models import Voucher

def get_cart_max_delivery_time(request, cart):
    """Returns the delivery time object with the maximal delivery time of all
    products within the cart. Takes the selected shipping method into account.

    This is used within the cart to display the maximal delivery time.
    """
    max_delivery_time = None
    for item in cart.items():
        # Calculate the delivery time of the product. Takes the selected
        # shipping method into account.
        delivery_time = shipping_utils.get_product_delivery_time(
            request, item.product.slug, for_cart=True)
        if (max_delivery_time is None) or \
           (delivery_time.as_hours() > max_delivery_time.as_hours()):
            max_delivery_time = delivery_time
    return max_delivery_time

# TODO: Remove cart from signature?
def get_cart_price(request, cart, total=False, cached=True):
    """Returns price of the given cart.
    """
    return get_cart_costs(request, cart, total, cached)["price"]

def get_cart_costs(request, cart, total=False, cached=True):
    """Returns a dictionary with price and tax of the given cart:

        returns {
            "price" : the cart's price,
            "tax" : the cart's tax,
        }
    """
    if cart is None:
        return {"price" : 0, "tax" : 0}

    cache_key = "cart-costs-%s-%s" % (total, cart.id)

    if cached:
        cart_costs = cache.get(cache_key)
    else:
        cart_costs = None

    if cart_costs is None:

        items = cart.items()

        cart_price = 0
        cart_tax = 0
        for item in items:
            cart_price += item.get_price()
            cart_tax += item.get_tax()

        if len(items) > 0 and total:
            # Shipping
            shipping_method = shipping_utils.get_selected_shipping_method(request)
            shipping_costs = shipping_utils.get_shipping_costs(request, shipping_method)
            cart_price += shipping_costs["price"]
            cart_tax += shipping_costs["tax"]

            # Payment
            payment_method = payment_utils.get_selected_payment_method(request)
            payment_costs = payment_utils.get_payment_costs(request, payment_method)
            cart_price += payment_costs["price"]
            cart_tax += payment_costs["tax"]

            # Discounts
            import lfs.discounts.utils
            discounts = lfs.discounts.utils.get_valid_discounts(request)
            for discount in discounts:
                cart_price = cart_price - discount["price"]

            # Vouchers
            try:
                voucher_number = lfs.voucher.utils.get_current_voucher_number(request)
                voucher = Voucher.objects.get(number=voucher_number)
            except Voucher.DoesNotExist:
                pass
            else:
                voucher_value = voucher.get_price_gross(cart)
                cart_price = cart_price - voucher_value

        cart_costs = {"price" : cart_price, "tax" : cart_tax}
        cache.set(cache_key, cart_costs)

    return cart_costs

def get_or_create_cart(request):
    """Returns the cart of the current user. If no cart exists it creates a new
    one first.
    """
    cart = get_cart(request)
    if cart is None:
        cart = create_cart(request)

    return cart

def create_cart(request):
    """Creates a cart for the current session and/or user.
    """
    cart = Cart(session = request.session.session_key)
    if request.user.is_authenticated():
        cart.user = request.user

    cart.save()
    return cart

def get_cart(request):
    """Returns the cart of the current customer or None.
    """
    session_key = request.session.session_key
    user = request.user

    if user.is_authenticated():
        try:
            cart = cache.get("cart-%s" % user)
            if cart is None:
                cart = Cart.objects.get(user = user)
                cache.set("cart-%s" % user, cart)
            return cart
        except ObjectDoesNotExist:
            return None
    else:
        try:
            cart = cache.get("cart-%s" % session_key)
            if cart is None:
                cart = Cart.objects.get(session = session_key)
                cache.set("cart-%s" % session_key, cart)
            return cart
        except ObjectDoesNotExist:
            return None

def get_go_on_shopping_url(request):
    """Calculates the go on shopping url.
    """
    lc = request.session.get("last_category")
    if lc:
        return lc.get_absolute_url()
    else:
        return reverse("lfs_shop_view")

def update_cart_after_login(request):
    """Updates the cart after login.

    1. if there is no session cart, nothing has to be done.
    2. if there is a session cart and no user cart we assign the session cart
       to the current user.
    3. if there is a session cart and a user cart we add the session cart items
       to the user cart.
    """
    try:
        session_cart = Cart.objects.get(session = request.session.session_key)
        try:
            user_cart = Cart.objects.get(user = request.user)
        except ObjectDoesNotExist:
            session_cart.user = request.user
            session_cart.save()
        else:
            for session_cart_item in session_cart.items():
                try:
                    user_cart_item = CartItem.objects.get(cart = user_cart, product = session_cart_item.product)
                except ObjectDoesNotExist:
                    session_cart_item.cart = user_cart
                    session_cart_item.save()
                else:
                    user_cart_item.amount += session_cart_item.amount
                    user_cart_item.save()
            session_cart.delete()
    except ObjectDoesNotExist:
        pass