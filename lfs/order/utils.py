# django imports
from django.core.urlresolvers import reverse

# lfs imports
from lfs.cart import utils as cart_utils
from lfs.core.signals import order_submitted
from lfs.customer import utils as customer_utils
from lfs.order.models import Order
from lfs.order.models import OrderItem
from lfs.payment import utils as payment_utils
from lfs.shipping import utils as shipping_utils

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
    cart_costs = cart_utils.get_cart_costs(request, cart, total=False)
    
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
        customer_email = invoice_address.email
        
    # Calculate the totals    
    price = cart_costs["price"] + shipping_costs["price"] + payment_costs["price"]
    tax = cart_costs["tax"] + shipping_costs["tax"] + payment_costs["tax"]
    
    order = Order.objects.create(
        user = user,
        session = request.session.session_key,
        price = price,
        tax = tax,

        customer_firstname = invoice_address.firstname,
        customer_lastname = invoice_address.lastname,
        customer_email = customer_email,
                
        shipping_method = shipping_method,
        shipping_price = shipping_costs["price"],
        shipping_tax = shipping_costs["tax"],
        payment_method = payment_method,
        payment_price = payment_costs["price"],
        payment_tax = payment_costs["tax"],

        invoice_firstname = invoice_address.firstname,
        invoice_lastname = invoice_address.lastname,
        invoice_company_name = invoice_address.company_name,
        invoice_street = invoice_address.street,
        invoice_zip_code = invoice_address.zip_code,
        invoice_city = invoice_address.city,
        invoice_country = invoice_address.country,
        invoice_phone = invoice_address.phone,

        shipping_firstname = shipping_address.firstname,
        shipping_lastname = shipping_address.lastname,
        shipping_company_name = shipping_address.company_name,
        shipping_street = shipping_address.street,
        shipping_zip_code = shipping_address.zip_code,
        shipping_city = shipping_address.city,
        shipping_country = shipping_address.country,
        shipping_phone = shipping_address.phone,

        message = request.POST.get("message", ""),
    )
        
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
        OrderItem.objects.create(
            order=order,
            
            price_net = cart_item.get_price_net(),
            price_gross = cart_item.get_price_gross(),
            tax = cart_item.get_tax(),

            product = cart_item.product,
            product_sku = cart_item.product.sku,
            product_name = cart_item.product.get_name(),
            product_amount=cart_item.amount,                        
            product_price_net = cart_item.product.get_price_net(),
            product_price_gross = cart_item.product.get_price_gross(),
            product_tax = cart_item.product.get_tax(),
        )
        
        cart_item.product.decrease_stock_amount(cart_item.amount)
        
    cart.delete()
    order_submitted.send(order)
    
    # Note: Save order for later use in thank you page. The order will be
    # removed from the session if the thank you page has been called.
    request.session["order"] = order
    
    return order

                               