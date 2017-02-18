# python imports
import json

# django imports
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _

# lfs imports
import lfs.cart.utils
import lfs.catalog.utils
from lfs.payment.models import PaymentMethod
from lfs.shipping.models import ShippingMethod
import lfs.voucher.utils
import lfs.discounts.utils
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.signals import cart_changed
from lfs.core import utils as core_utils
from lfs.catalog.models import Product, PropertyGroup
from lfs.catalog.models import Property
from lfs.cart import utils as cart_utils
from lfs.cart.models import CartItem
from lfs.core.models import Country
from lfs.core.utils import LazyEncoder
from lfs.shipping import utils as shipping_utils
from lfs.payment import utils as payment_utils
from lfs.customer import utils as customer_utils


def cart(request, template_name="lfs/cart/cart.html"):
    """
    The main view of the cart.
    """
    return render(request, template_name, {
        "voucher_number": lfs.voucher.utils.get_current_voucher_number(request),
        "cart_inline": cart_inline(request),
    })


def cart_inline(request, template_name="lfs/cart/cart_inline.html"):
    """
    The actual content of the cart.

    This is factored out to be reused within 'normal' and ajax requests.
    """
    cart = cart_utils.get_cart(request)
    shopping_url = lfs.cart.utils.get_go_on_shopping_url(request)
    if cart is None:
        return render_to_string(template_name, request=request, context={
            "shopping_url": shopping_url,
        })

    shop = core_utils.get_default_shop(request)
    countries = shop.shipping_countries.all()
    selected_country = shipping_utils.get_selected_shipping_country(request)

    # Get default shipping method, so that we have a one in any case.
    selected_shipping_method = shipping_utils.get_selected_shipping_method(request)
    selected_payment_method = payment_utils.get_selected_payment_method(request)

    shipping_costs = shipping_utils.get_shipping_costs(request, selected_shipping_method)

    # Payment
    payment_costs = payment_utils.get_payment_costs(request, selected_payment_method)

    # Cart costs
    cart_price = cart.get_price_gross(request) + shipping_costs["price_gross"] + payment_costs["price"]
    cart_tax = cart.get_tax(request) + shipping_costs["tax"] + payment_costs["tax"]

    # get voucher data (if voucher exists)
    voucher_data = lfs.voucher.utils.get_voucher_data(request, cart)

    # get discounts data
    discounts_data = lfs.discounts.utils.get_discounts_data(request)

    # calculate total value of discounts and voucher that sum up
    summed_up_value = discounts_data['summed_up_value']
    if voucher_data['sums_up']:
        summed_up_value += voucher_data['voucher_value']

    # initialize discounts with summed up discounts
    use_voucher = voucher_data['voucher'] is not None
    discounts = discounts_data['summed_up_discounts']
    if voucher_data['voucher_value'] > summed_up_value or discounts_data['max_value'] > summed_up_value:
        # use not summed up value
        if voucher_data['voucher_value'] > discounts_data['max_value']:
            # use voucher only
            discounts = []
        else:
            # use discount only
            discounts = discounts_data['max_discounts']
            use_voucher = False

    for discount in discounts:
        cart_price -= discount["price_gross"]
        cart_tax -= discount["tax"]

    if use_voucher:
        cart_price -= voucher_data['voucher_value']
        cart_tax -= voucher_data['voucher_tax']

    cart_price = max(0, cart_price)
    cart_tax = max(0, cart_tax)

    # Calc delivery time for cart (which is the maximum of all cart items)
    max_delivery_time = cart.get_delivery_time(request)

    cart_items = []
    for cart_item in cart.get_items():
        product = cart_item.product
        quantity = product.get_clean_quantity(cart_item.amount)
        cart_items.append({
            "obj": cart_item,
            "quantity": quantity,
            "product": product,
            "product_price_net": cart_item.get_price_net(request),
            "product_price_gross": cart_item.get_price_gross(request),
            "product_tax": cart_item.get_tax(request),
        })

    return render_to_string(template_name, request=request, context={
        "cart": cart,
        "cart_items": cart_items,
        "cart_price": cart_price,
        "cart_tax": cart_tax,
        "shipping_methods": shipping_utils.get_valid_shipping_methods(request),
        "selected_shipping_method": selected_shipping_method,
        "shipping_costs": shipping_costs,
        "payment_methods": payment_utils.get_valid_payment_methods(request),
        "selected_payment_method": selected_payment_method,
        "payment_price": payment_costs["price"],
        "countries": countries,
        "selected_country": selected_country,
        "max_delivery_time": max_delivery_time,
        "shopping_url": shopping_url,
        "discounts": discounts,
        "display_voucher": use_voucher,
        "voucher_number": voucher_data['voucher_number'],
        "voucher_value": voucher_data['voucher_value'],
        "voucher_tax": voucher_data['voucher_tax'],
        "voucher_message": voucher_data['voucher_message'],
    })


def added_to_cart(request, template_name="lfs/cart/added_to_cart.html"):
    """
    Displays the product that has been added to the cart along with the
    selected accessories.
    """
    cart_items = request.session.get("cart_items", [])
    try:
        accessories = cart_items[0].product.get_accessories()
    except IndexError:
        accessories = []

    cart_items_count = len(cart_items)
    return render(request, template_name, {
        "plural": cart_items_count > 1,
        "cart_items_count": cart_items_count,
        "shopping_url": request.META.get("HTTP_REFERER", "/"),
        "product_accessories": accessories,
        "product": cart_items[0].product if cart_items else None,
        "cart_items": added_to_cart_items(request),
    })


def added_to_cart_items(request, template_name="lfs/cart/added_to_cart_items.html"):
    """
    Displays the added items for the added-to-cart view.
    """
    total = 0
    cart_items = []
    for cart_item in request.session.get("cart_items", []):
        total += cart_item.get_price_gross(request)
        product = cart_item.product
        quantity = product.get_clean_quantity(cart_item.amount)

        cart_items.append({
            "product": product,
            "obj": cart_item,
            "quantity": quantity,
            "product_price_net": cart_item.get_price_net(request),
            "product_price_gross": cart_item.get_price_gross(request),
            "product_tax": cart_item.get_tax(request),
        })

    return render_to_string(template_name, request=request, context={
        "total": total,
        "cart_items": cart_items,
    })


# Actions
def add_accessory_to_cart(request, product_id):
    """
    Adds the product with passed product_id as an accessory to the cart and
    updates the added-to-cart view.
    """
    product = lfs_get_object_or_404(Product, pk=product_id)
    # for product with variants add default variant
    if product.is_product_with_variants():
        variant = product.get_default_variant()
        if variant:
            product = variant
        else:
            return HttpResponse(added_to_cart_items(request))

    quantity = product.get_clean_quantity_value(request.POST.get("quantity", 1))

    session_cart_items = request.session.get("cart_items", [])
    cart = cart_utils.get_cart(request)
    cart_item = cart.add(product=product, amount=quantity)

    # Update session
    if cart_item not in session_cart_items:
        session_cart_items.append(cart_item)
    else:
        for session_cart_item in session_cart_items:
            if cart_item.product == session_cart_item.product:
                session_cart_item.amount += quantity

    request.session["cart_items"] = session_cart_items

    cart_changed.send(cart, request=request)
    return HttpResponse(added_to_cart_items(request))


def add_to_cart(request, product_id=None):
    """
    Adds the passed product with passed product_id to the cart after
    some validations have been taken place. The amount is taken from the query
    string.
    """
    if product_id is None:
        product_id = (request.POST if request.method == 'POST' else request.GET).get("product_id")

    product = lfs_get_object_or_404(Product, pk=product_id)

    # Only active and deliverable products can be added to the cart.
    if not (product.is_active() and product.is_deliverable()):
        raise Http404()

    quantity = request.POST.get("quantity", "1.0")
    quantity = product.get_clean_quantity_value(quantity)

    # Validate properties (They are added below)
    properties_dict = {}
    if product.is_configurable_product():
        for key, value in request.POST.items():
            if key.startswith("property-"):
                try:
                    property_group_id, property_id = key.split("-")[1:]
                except IndexError:
                    continue

                try:
                    prop = Property.objects.get(pk=property_id)
                except Property.DoesNotExist:
                    continue

                if property_group_id != '0':
                    try:
                        PropertyGroup.objects.get(pk=property_group_id)
                    except PropertyGroup.DoesNotExist:
                        continue

                if prop.is_number_field:
                    try:
                        value = lfs.core.utils.atof(value)
                    except ValueError:
                        value = 0.0

                key = '{0}_{1}'.format(property_group_id, property_id)
                properties_dict[key] = {'value': unicode(value),
                                        'property_group_id': property_group_id,
                                        'property_id': property_id}

                # validate property's value
                if prop.is_number_field:

                    if (value < prop.unit_min) or (value > prop.unit_max):
                        msg = _(u"%(name)s must be between %(min)s and %(max)s %(unit)s.") % {"name": prop.title, "min": prop.unit_min, "max": prop.unit_max, "unit": prop.unit}
                        return lfs.core.utils.set_message_cookie(
                            product.get_absolute_url(), msg)

                    # calculate valid steps
                    steps = []
                    x = prop.unit_min
                    while x < prop.unit_max:
                        steps.append("%.2f" % x)
                        x += prop.unit_step
                    steps.append("%.2f" % prop.unit_max)

                    value = "%.2f" % value
                    if value not in steps:
                        msg = _(u"Your entered value for %(name)s (%(value)s) is not in valid step width, which is %(step)s.") % {"name": prop.title, "value": value, "step": prop.unit_step}
                        return lfs.core.utils.set_message_cookie(
                            product.get_absolute_url(), msg)

    if product.get_active_packing_unit():
        quantity = product.get_amount_by_packages(quantity)

    cart = cart_utils.get_or_create_cart(request)

    cart_item = cart.add(product, properties_dict, quantity)
    cart_items = [cart_item]

    # Check stock amount
    message = ""
    if product.manage_stock_amount and cart_item.amount > product.stock_amount and not product.order_time:
        if product.stock_amount == 0:
            message = _(u"Sorry, but '%(product)s' is not available anymore.") % {"product": product.name}
        elif product.stock_amount == 1:
            message = _(u"Sorry, but '%(product)s' is only one time available.") % {"product": product.name}
        else:
            message = _(u"Sorry, but '%(product)s' is only %(amount)s times available.") % {"product": product.name, "amount": product.stock_amount}
        cart_item.amount = product.stock_amount
        cart_item.save()

    # Add selected accessories to cart
    for key, value in request.POST.items():
        if key.startswith("accessory"):
            accessory_id = key.split("-")[1]
            try:
                accessory = Product.objects.get(pk=accessory_id)
            except ObjectDoesNotExist:
                continue

            # for product with variants add default variant
            if accessory.is_product_with_variants():
                accessory_variant = accessory.get_default_variant()
                if accessory_variant:
                    accessory = accessory_variant
                else:
                    continue

            # Get quantity
            quantity = request.POST.get("quantity-%s" % accessory_id, 0)
            quantity = accessory.get_clean_quantity_value(quantity)

            cart_item = cart.add(product=accessory, amount=quantity)
            cart_items.append(cart_item)

    # Store cart items for retrieval within added_to_cart.
    request.session["cart_items"] = cart_items
    cart_changed.send(cart, request=request)

    # Update the customer's shipping method (if appropriate)
    customer = customer_utils.get_or_create_customer(request)
    shipping_utils.update_to_valid_shipping_method(request, customer, save=True)

    # Update the customer's payment method (if appropriate)
    payment_utils.update_to_valid_payment_method(request, customer, save=True)

    # Save the cart to update modification date
    cart.save()

    try:
        url_name = settings.LFS_AFTER_ADD_TO_CART
    except AttributeError:
        url_name = "lfs_added_to_cart"

    if message:
        return lfs.core.utils.set_message_cookie(reverse(url_name), message)
    else:
        return HttpResponseRedirect(reverse(url_name))


def delete_cart_item(request, cart_item_id):
    """
    Deletes the cart item with the given id.
    """
    cart = cart_utils.get_cart(request)
    if not cart:
        raise Http404

    item = lfs_get_object_or_404(CartItem, pk=cart_item_id)
    if item.cart.id != cart.id:
        raise Http404
    item.delete()

    cart_changed.send(cart, request=request)

    return HttpResponse(cart_inline(request))


def refresh_cart(request):
    """
    Refreshes the cart after some changes has been taken place, e.g.: the
    amount of a product or shipping/payment method.
    """
    cart = cart_utils.get_cart(request)
    if not cart:
        raise Http404
    customer = customer_utils.get_or_create_customer(request)

    # Update country
    country_iso = request.POST.get("country")
    if country_iso:
        selected_country = Country.objects.get(code=country_iso.lower())
        customer.selected_country_id = selected_country.id
        if customer.selected_shipping_address:
            customer.selected_shipping_address.country = selected_country
            customer.selected_shipping_address.save()
            customer.selected_shipping_address.save()
        if customer.selected_invoice_address:
            customer.selected_invoice_address.country = selected_country
            customer.selected_invoice_address.save()
            customer.selected_invoice_address.save()
        # NOTE: The customer has to be saved already here in order to calculate
        # a possible new valid shippig method below, which coulb be triggered by
        # the changing of the shipping country.
        customer.save()

    # Update Amounts
    message = ""
    for item in cart.get_items():
        amount = request.POST.get("amount-cart-item_%s" % item.id, "0.0")
        amount = item.product.get_clean_quantity_value(amount, allow_zero=True)

        if item.product.manage_stock_amount and amount > item.product.stock_amount and not item.product.order_time:
            amount = item.product.stock_amount
            if amount < 0:
                amount = 0

            if amount == 0:
                message = _(u"Sorry, but '%(product)s' is not available anymore." % {"product": item.product.name})
            elif amount == 1:
                message = _(u"Sorry, but '%(product)s' is only one time available." % {"product": item.product.name})
            else:
                message = _(u"Sorry, but '%(product)s' is only %(amount)s times available.") % {"product": item.product.name, "amount": amount}

        if item.product.get_active_packing_unit():
            item.amount = item.product.get_amount_by_packages(float(amount))
        else:
            item.amount = amount

        if amount == 0:
            item.delete()
        else:
            item.save()

    # IMPORTANT: We have to send the signal already here, because the valid
    # shipping methods might be dependent on the price.
    cart_changed.send(cart, request=request)

    # Update shipping method
    shipping_method = get_object_or_404(ShippingMethod, pk=request.POST.get("shipping_method"))
    customer.selected_shipping_method = shipping_method

    valid_shipping_methods = shipping_utils.get_valid_shipping_methods(request)
    if customer.selected_shipping_method not in valid_shipping_methods:
        customer.selected_shipping_method = shipping_utils.get_default_shipping_method(request)

    # Update payment method
    payment_method = get_object_or_404(PaymentMethod, pk=request.POST.get("payment_method"))
    customer.selected_payment_method = payment_method

    # Last but not least we save the customer ...
    customer.save()

    result = json.dumps({
        "html": cart_inline(request),
        "message": message,
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


def check_voucher(request):
    """
    Updates the cart after the voucher number has been changed.
    """
    voucher_number = lfs.voucher.utils.get_current_voucher_number(request)
    lfs.voucher.utils.set_current_voucher_number(request, voucher_number)

    result = json.dumps({
        "html": (("#cart-inline", cart_inline(request)),)
    })

    return HttpResponse(result, content_type='application/json')
