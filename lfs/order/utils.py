# lfs imports
import lfs.discounts.utils
import lfs.voucher.utils
from lfs.cart import utils as cart_utils
from lfs.core.models import Country
from lfs.customer import utils as customer_utils
from lfs.order.models import Order
from lfs.order.models import OrderItem
from lfs.order.models import OrderItemPropertyValue
from lfs.payment import utils as payment_utils
from lfs.shipping import utils as shipping_utils
from lfs.voucher.models import Voucher


def add_order(request):
    """Adds an order based on current cart for the current customer.

    It assumes that the customer is prepared with all needed information. This
    is within the responsibility of the checkout form.
    """
    customer = customer_utils.get_customer(request)
    order = None

    invoice_address = customer.selected_invoice_address
    if customer.selected_shipping_address:
        shipping_address = customer.selected_shipping_address
    else:
        shipping_address = customer.selected_invoice_address

    cart = cart_utils.get_cart(request)
    if cart is None:
        return order

    shipping_method = shipping_utils.get_selected_shipping_method(request)
    shipping_costs = shipping_utils.get_shipping_costs(request, shipping_method)

    payment_method = payment_utils.get_selected_payment_method(request)
    payment_costs = payment_utils.get_payment_costs(request, payment_method)

    # Set email dependend on login state. An anonymous customer doesn't  have a
    # django user account, so we set the name of the invoice address to the
    # customer name.

    # Note: After this has been processed the order's customer email has an
    # email in any case. That means you can use it to send emails to the
    # customer.
    if request.user.is_authenticated():
        user = request.user
        customer_email = user.email
    else:
        user = None
        customer_email = customer.selected_invoice_address.email

    # Calculate the totals
    price = cart.get_price_gross(request) + shipping_costs["price"] + payment_costs["price"]
    tax = cart.get_tax(request) + shipping_costs["tax"] + payment_costs["tax"]

    # Discounts
    discounts = lfs.discounts.utils.get_valid_discounts(request)
    for discount in discounts:
        price = price - discount["price"]
        tax = tax - discount["tax"]

    # Add voucher if one exists
    try:
        voucher_number = lfs.voucher.utils.get_current_voucher_number(request)
        voucher = Voucher.objects.get(number=voucher_number)
    except Voucher.DoesNotExist:
        voucher = None
    else:
        is_voucher_effective, voucher_message = voucher.is_effective(cart)
        if is_voucher_effective:
            voucher_number = voucher.number
            voucher_price = voucher.get_price_gross(cart)
            voucher_tax = voucher.get_tax(cart)

            price -= voucher_price
            tax -= voucher_tax
        else:
            voucher = None

    order = Order.objects.create(
        user=user,
        session=request.session.session_key,
        price=price,
        tax=tax,

        customer_firstname=customer.selected_invoice_address.firstname,
        customer_lastname=customer.selected_invoice_address.lastname,
        customer_email=customer_email,

        shipping_method=shipping_method,
        shipping_price=shipping_costs["price"],
        shipping_tax=shipping_costs["tax"],
        payment_method=payment_method,
        payment_price=payment_costs["price"],
        payment_tax=payment_costs["tax"],

        invoice_firstname=customer.selected_invoice_address.firstname,
        invoice_lastname=customer.selected_invoice_address.lastname,
        invoice_line1=invoice_address.company_name,
        invoice_line2=invoice_address.street,
        invoice_city=invoice_address.city,
        invoice_state=invoice_address.state,
        invoice_code=invoice_address.zip_code,
        invoice_country=Country.objects.get(code=invoice_address.country.code),
        invoice_phone=customer.selected_invoice_address.phone,

        shipping_firstname=shipping_address.firstname,
        shipping_lastname=shipping_address.lastname,
        shipping_line1=shipping_address.company_name,
        shipping_line2=shipping_address.street,
        shipping_city=shipping_address.city,
        shipping_state=shipping_address.state,
        shipping_code=shipping_address.zip_code,
        shipping_country=Country.objects.get(code=shipping_address.country.code),
        shipping_phone=shipping_address.phone,

        message=request.POST.get("message", ""),
    )

    requested_delivery_date = request.POST.get("requested_delivery_date", None)
    if requested_delivery_date is not None:
        order.requested_delivery_date = requested_delivery_date
        order.save()

    if voucher:
        voucher.mark_as_used()
        order.voucher_number = voucher_number
        order.voucher_price = voucher_price
        order.voucher_tax = voucher_tax
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
    for cart_item in cart.cartitem_set.all():
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
                OrderItemPropertyValue.objects.create(
                    order_item=order_item, property=cpv.property, value=cpv.value)

    for discount in discounts:
        OrderItem.objects.create(
            order=order,
            price_net=-(discount["price"] - discount["tax"]),
            price_gross=-discount["price"],
            tax=-discount["tax"],

            product_sku=discount["sku"],
            product_name=discount["name"],
            product_amount=1,
            product_price_net=-(discount["price"] - discount["tax"]),
            product_price_gross=-discount["price"],
            product_tax=-discount["tax"],
        )

    cart.delete()

    # Note: Save order for later use in thank you page. The order will be
    # removed from the session if the thank you page has been called.
    request.session["order"] = order

    return order
