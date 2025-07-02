# python imports
from copy import deepcopy

# django imports
from django.conf import settings

# lfs imports
from lfs.cart import utils as cart_utils
from lfs.core.signals import order_created
from lfs.core.utils import import_symbol
from lfs.customer import utils as customer_utils
from lfs.order.models import Order, OrderDeliveryTime
from lfs.order.models import OrderItem
from lfs.order.models import OrderItemPropertyValue
from lfs.voucher.utils import delete_current_voucher_number


def add_order(request):
    """Adds an order based on current cart for the current customer.

    It assumes that the customer is prepared with all needed information. This
    is within the responsibility of the checkout form.
    """
    customer = customer_utils.get_customer(request)
    order = None

    not_required_address = getattr(settings, "LFS_CHECKOUT_NOT_REQUIRED_ADDRESS", "shipping")

    invoice_address = customer.selected_invoice_address
    shipping_address = customer.selected_shipping_address
    if not_required_address == "shipping":
        if request.POST.get("no_shipping"):
            shipping_address = customer.selected_invoice_address
        else:
            shipping_address = customer.selected_shipping_address
    else:
        if request.POST.get("no_invoice"):
            invoice_address = customer.selected_shipping_address
        else:
            invoice_address = customer.selected_invoice_address

    cart = cart_utils.get_cart(request)
    if cart is None:
        return order

    if request.user.is_authenticated:
        user = request.user
        customer_email = user.email
    else:
        user = None
        customer_email = customer.selected_invoice_address.email

    (
        price,
        tax,
        shipping_method,
        shipping_costs,
        payment_method,
        payment_costs,
        voucher_data,
        discounts_data,
        use_voucher,
        discounts,
    ) = cart.get_order_data(request)

    # Copy addresses
    invoice_address = deepcopy(invoice_address)
    invoice_address.id = None
    invoice_address.pk = None
    invoice_address.save()

    shipping_address = deepcopy(shipping_address)
    shipping_address.id = None
    shipping_address.pk = None
    shipping_address.save()

    order = Order.objects.create(
        user=user,
        session=request.session.session_key,
        price=price,
        tax=tax,
        customer_firstname=customer.selected_invoice_address.firstname,
        customer_lastname=customer.selected_invoice_address.lastname,
        customer_email=customer_email,
        shipping_method=shipping_method,
        shipping_price=shipping_costs["price_gross"],
        shipping_tax=shipping_costs["tax"],
        payment_method=payment_method,
        payment_price=payment_costs["price_gross"],
        payment_tax=payment_costs["tax"],
        invoice_address=invoice_address,
        shipping_address=shipping_address,
        message=request.POST.get("message", ""),
    )

    delivery_time = cart.get_delivery_time(request)
    if delivery_time:
        OrderDeliveryTime.objects.create(
            order=order, min=delivery_time.min, max=delivery_time.max, unit=delivery_time.unit
        )

    invoice_address.order = order
    invoice_address.save()

    shipping_address.order = order
    shipping_address.save()

    requested_delivery_date = request.POST.get("requested_delivery_date", None)
    if requested_delivery_date is not None:
        order.requested_delivery_date = requested_delivery_date
        order.save()

    if use_voucher:
        voucher_data["voucher"].mark_as_used()
        order.voucher_number = voucher_data["voucher_number"]
        order.voucher_price = voucher_data["voucher_value"]
        order.voucher_tax = voucher_data["voucher_tax"]
        order.save()

    # Copy bank account if one exists
    if customer.selected_bank_account:
        bank_account = customer.selected_bank_account
        order.account_number = bank_account.account_number
        order.bank_identification_code = bank_account.bank_identification_code
        order.bank_name = bank_account.bank_name
        order.depositor = bank_account.depositor

    order.save()

    # Copy cart items
    for cart_item in cart.get_items():
        if cart_item.amount == 0:
            continue
        order_item = OrderItem.objects.create(
            order=order,
            price_net=cart_item.get_price_net(request),
            price_gross=cart_item.get_price_gross(request),
            tax=cart_item.get_tax(request),
            product=cart_item.product,
            product_sku=cart_item.product.sku,
            product_name=cart_item.product.get_name(),
            product_amount=cart_item.amount,
            product_price_net=cart_item.product.get_price_net(request),
            product_price_gross=cart_item.get_product_price_gross(request),
            product_tax=cart_item.product.get_tax(request),
        )

        cart_item.product.decrease_stock_amount(cart_item.amount)

        # Copy properties to order
        if cart_item.product.is_configurable_product():
            for cpv in cart_item.properties.all():
                OrderItemPropertyValue.objects.create(order_item=order_item, property=cpv.property, value=cpv.value)

    for discount in discounts:
        OrderItem.objects.create(
            order=order,
            price_net=-discount["price_net"],
            price_gross=-discount["price_gross"],
            tax=-discount["tax"],
            product_sku=discount["sku"],
            product_name=discount["name"],
            product_amount=1,
            product_price_net=-discount["price_net"],
            product_price_gross=-discount["price_gross"],
            product_tax=-discount["tax"],
        )

    # Re-initialize selected addresses to be equal to default addresses for next order
    customer.sync_default_to_selected_addresses()
    customer.save()

    # Send signal before cart is deleted.
    order_created.send(order, cart=cart, request=request)

    cart.delete()
    delete_current_voucher_number(request)

    # Note: Save order for later use in thank you page. The order will be
    # removed from the session if the thank you page has been called.
    request.session["order"] = order

    ong = import_symbol(settings.LFS_ORDER_NUMBER_GENERATOR)
    try:
        order_numbers = ong.objects.get(id="order_number")
    except ong.DoesNotExist:
        order_numbers = ong.objects.create(id="order_number")

    try:
        order_numbers.init(request, order)
    except AttributeError:
        pass

    order.number = order_numbers.get_next()
    order.save()

    return order
