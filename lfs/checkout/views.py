# python imports
from copy import deepcopy

# django imports
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

# lfs imports
import lfs.core.utils
import lfs.discounts.utils
import lfs.order.utils
import lfs.payment.settings
import lfs.payment.utils
import lfs.shipping.utils
import lfs.voucher.utils
from lfs.addresses.utils import AddressManagement
from lfs.cart import utils as cart_utils
from lfs.checkout.forms import OnePageCheckoutForm
from lfs.checkout.settings import CHECKOUT_TYPE_ANON
from lfs.checkout.settings import CHECKOUT_TYPE_AUTH
from lfs.customer import utils as customer_utils
from lfs.core.models import Country
from lfs.customer.forms import CreditCardForm
from lfs.customer.forms import BankAccountForm
from lfs.customer.forms import RegisterForm
from lfs.payment.models import PaymentMethod
from lfs.voucher.models import Voucher
from lfs.voucher.settings import MESSAGES


def login(request, template_name="lfs/checkout/login.html"):
    """Displays a form to login or register/login the user within the check out
    process.

    The form's post request goes to lfs.customer.views.login where all the logic
    happens - see there for more.
    """
    # If the user is already authenticate we don't want to show this view at all
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse("lfs_checkout"))

    shop = lfs.core.utils.get_default_shop(request)

    # If only anonymous checkout allowed we don't want to show this view at all.
    if shop.checkout_type == CHECKOUT_TYPE_ANON:
        return HttpResponseRedirect(reverse("lfs_checkout"))

    # Using Djangos default AuthenticationForm
    login_form = AuthenticationForm()
    login_form.fields["username"].label = _(u"E-Mail")
    register_form = RegisterForm()

    if request.POST.get("action") == "login":
        login_form = AuthenticationForm(data=request.POST)
        login_form.fields["username"].label = _(u"E-Mail")
        if login_form.is_valid():
            from django.contrib.auth import login
            login(request, login_form.get_user())

            return lfs.core.utils.set_message_cookie(reverse("lfs_checkout"),
                msg=_(u"You have been logged in."))

    elif request.POST.get("action") == "register":
        register_form = RegisterForm(data=request.POST)
        if register_form.is_valid():
            email = register_form.data.get("email")
            password = register_form.data.get("password_1")

            # Create user
            user = User.objects.create_user(
                username=email, email=email, password=password)

            # Notify
            lfs.core.signals.customer_added.send(user)

            # Log in user
            from django.contrib.auth import authenticate
            user = authenticate(username=email, password=password)

            from django.contrib.auth import login
            login(request, user)

            return lfs.core.utils.set_message_cookie(reverse("lfs_checkout"),
                msg=_(u"You have been registered and logged in."))

    return render_to_response(template_name, RequestContext(request, {
        "login_form": login_form,
        "register_form": register_form,
        "anonymous_checkout": shop.checkout_type != CHECKOUT_TYPE_AUTH,
    }))


def checkout_dispatcher(request):
    """Dispatcher to display the correct checkout form
    """
    shop = lfs.core.utils.get_default_shop(request)
    cart = cart_utils.get_cart(request)

    if cart is None or not cart.get_items():
        return empty_page_checkout(request)

    if request.user.is_authenticated() or \
       shop.checkout_type == CHECKOUT_TYPE_ANON:
        return HttpResponseRedirect(reverse("lfs_checkout"))
    else:
        return HttpResponseRedirect(reverse("lfs_checkout_login"))


def cart_inline(request, template_name="lfs/checkout/checkout_cart_inline.html"):
    """Displays the cart items of the checkout page.

    Factored out to be reusable for the starting request (which renders the
    whole checkout page and subsequent ajax requests which refresh the
    cart items.
    """
    cart = cart_utils.get_cart(request)

    # Shipping
    selected_shipping_method = lfs.shipping.utils.get_selected_shipping_method(request)
    shipping_costs = lfs.shipping.utils.get_shipping_costs(request, selected_shipping_method)

    # Payment
    selected_payment_method = lfs.payment.utils.get_selected_payment_method(request)
    payment_costs = lfs.payment.utils.get_payment_costs(request, selected_payment_method)

    # Cart costs
    cart_price = cart.get_price_gross(request) + shipping_costs["price"] + payment_costs["price"]
    cart_tax = cart.get_tax(request) + shipping_costs["tax"] + payment_costs["tax"]

    discounts = lfs.discounts.utils.get_valid_discounts(request)
    for discount in discounts:
        cart_price = cart_price - discount["price_gross"]
        cart_tax = cart_tax - discount["tax"]

    # Voucher
    try:
        voucher_number = lfs.voucher.utils.get_current_voucher_number(request)
        voucher = Voucher.objects.get(number=voucher_number)
    except Voucher.DoesNotExist:
        display_voucher = False
        voucher_value = 0
        voucher_tax = 0
        voucher_message = MESSAGES[6]
    else:
        lfs.voucher.utils.set_current_voucher_number(request, voucher_number)
        is_voucher_effective, voucher_message = voucher.is_effective(request, cart)
        if is_voucher_effective:
            display_voucher = True
            voucher_value = voucher.get_price_gross(request, cart)
            cart_price = cart_price - voucher_value
            voucher_tax = voucher.get_tax(request, cart)
        else:
            display_voucher = False
            voucher_value = 0
            voucher_tax = 0

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

    return render_to_string(template_name, RequestContext(request, {
        "cart": cart,
        "cart_items": cart_items,
        "cart_price": cart_price,
        "cart_tax": cart_tax,
        "display_voucher": display_voucher,
        "discounts": discounts,
        "voucher_value": voucher_value,
        "voucher_tax": voucher_tax,
        "shipping_price": shipping_costs["price"],
        "payment_price": payment_costs["price"],
        "selected_shipping_method": selected_shipping_method,
        "selected_payment_method": selected_payment_method,
        "voucher_number": voucher_number,
        "voucher_message": voucher_message,
    }))


def one_page_checkout(request, template_name="lfs/checkout/one_page_checkout.html"):
    """
    One page checkout form.
    """
    cart = lfs.cart.utils.get_cart(request)
    if cart is None:
        return HttpResponseRedirect(reverse('lfs_cart'))

    shop = lfs.core.utils.get_default_shop(request)
    if request.user.is_anonymous() and shop.checkout_type == CHECKOUT_TYPE_AUTH:
        return HttpResponseRedirect(reverse("lfs_checkout_login"))

    customer = lfs.customer.utils.get_or_create_customer(request)
    invoice_address = customer.selected_invoice_address
    shipping_address = customer.selected_shipping_address
    bank_account = customer.selected_bank_account
    credit_card = customer.selected_credit_card

    if request.method == "POST":
        checkout_form = OnePageCheckoutForm(data=request.POST)
        iam = AddressManagement(invoice_address, "invoice", request.POST)
        sam = AddressManagement(shipping_address, "shipping", request.POST)
        bank_account_form = BankAccountForm(instance=bank_account, data=request.POST)
        credit_card_form = CreditCardForm(instance=credit_card, data=request.POST)

        if shop.confirm_toc and ("confirm_toc" not in request.POST):
            toc = False
            if checkout_form.errors is None:
                checkout_form.errors = {}
            checkout_form.errors["confirm_toc"] = _(u"Please confirm our terms and conditions")
        else:
            toc = True

        if checkout_form.is_valid() and bank_account_form.is_valid() and iam.is_valid() and sam.is_valid() and toc:
            # Save addresses
            iam.save()

            # If there the shipping address is not given, the invoice address
            # is copied.
            if request.POST.get("no_shipping", "") == "":
                sam.save()
            else:
                shipping_address = deepcopy(customer.selected_invoice_address)
                shipping_address.id = None
                shipping_address.save()
                customer.selected_shipping_address = shipping_address

            # Save payment method
            customer.selected_payment_method_id = request.POST.get("payment_method")

            # Save bank account
            if customer.selected_payment_method_id and \
               int(customer.selected_payment_method_id) == lfs.payment.settings.PM_BANK:
                customer.selected_bank_account = bank_account_form.save()

            # Save credit card
            if customer.selected_payment_method_id and \
               int(customer.selected_payment_method_id) == lfs.payment.settings.PM_CREDIT_CARD:
                customer.selected_credit_card = credit_card_form.save()

            customer.save()

            # process the payment method
            result = lfs.payment.utils.process_payment(request)

            if result["accepted"]:
                return HttpResponseRedirect(result.get("next_url", reverse("lfs_thank_you")))
            else:
                if "message" in result:
                    checkout_form._errors[result.get("message_location")] = result.get("message")

    else:
        checkout_form = OnePageCheckoutForm()
        iam = AddressManagement(invoice_address, "invoice")
        sam = AddressManagement(shipping_address, "shipping")
        bank_account_form = BankAccountForm(instance=bank_account)
        credit_card_form = CreditCardForm(instance=credit_card)

    # Payment
    try:
        selected_payment_method_id = request.POST.get("payment_method")
        selected_payment_method = PaymentMethod.objects.get(pk=selected_payment_method_id)
    except PaymentMethod.DoesNotExist:
        selected_payment_method = lfs.payment.utils.get_selected_payment_method(request)

    valid_payment_methods = lfs.payment.utils.get_valid_payment_methods(request)
    display_bank_account = any([pm.type == lfs.payment.settings.PM_BANK for pm in valid_payment_methods])
    display_credit_card = any([pm.type == lfs.payment.settings.PM_CREDIT_CARD for pm in valid_payment_methods])

    return render_to_response(template_name, RequestContext(request, {
        "checkout_form": checkout_form,
        "bank_account_form": bank_account_form,
        "credit_card_form": credit_card_form,
        "invoice_address_inline": iam.render(request),
        "shipping_address_inline": sam.render(request),
        "shipping_inline": shipping_inline(request),
        "payment_inline": payment_inline(request, bank_account_form),
        "selected_payment_method": selected_payment_method,
        "display_bank_account": display_bank_account,
        "display_credit_card": display_credit_card,
        "voucher_number": lfs.voucher.utils.get_current_voucher_number(request),
        "cart_inline": cart_inline(request),
        "settings": settings,
    }))


def empty_page_checkout(request, template_name="lfs/checkout/empty_page_checkout.html"):
    """
    """
    return render_to_response(template_name, RequestContext(request, {
        "shopping_url": reverse("lfs_shop_view"),
    }))


def thank_you(request, template_name="lfs/checkout/thank_you_page.html"):
    """Displays a thank you page ot the customer
    """
    order = request.session.get("order")
    pay_link = order.get_pay_link(request) if order else None
    return render_to_response(template_name, RequestContext(request, {
        "order": order,
        "pay_link": pay_link,
    }))


def payment_inline(request, form, template_name="lfs/checkout/payment_inline.html"):
    """Displays the selectable payment methods of the checkout page.

    Factored out to be reusable for the starting request (which renders the
    whole checkout page and subsequent ajax requests which refresh the
    selectable payment methods.

    Passing the form to be able to display payment forms within the several
    payment methods, e.g. credit card form.
    """
    selected_payment_method = lfs.payment.utils.get_selected_payment_method(request)
    valid_payment_methods = lfs.payment.utils.get_valid_payment_methods(request)

    return render_to_string(template_name, RequestContext(request, {
        "payment_methods": valid_payment_methods,
        "selected_payment_method": selected_payment_method,
        "form": form,
    }))


def shipping_inline(request, template_name="lfs/checkout/shipping_inline.html"):
    """Displays the selectable shipping methods of the checkout page.

    Factored out to be reusable for the starting request (which renders the
    whole checkout page and subsequent ajax requests which refresh the
    selectable shipping methods.
    """
    selected_shipping_method = lfs.shipping.utils.get_selected_shipping_method(request)
    shipping_methods = lfs.shipping.utils.get_valid_shipping_methods(request)

    return render_to_string(template_name, RequestContext(request, {
        "shipping_methods": shipping_methods,
        "selected_shipping_method": selected_shipping_method,
    }))


def check_voucher(request):
    """
    """
    voucher_number = lfs.voucher.utils.get_current_voucher_number(request)
    lfs.voucher.utils.set_current_voucher_number(request, voucher_number)

    result = simplejson.dumps({
        "html": (("#cart-inline", cart_inline(request)),)
    })

    return HttpResponse(result)


def changed_checkout(request):
    """
    """
    form = OnePageCheckoutForm()
    customer = customer_utils.get_or_create_customer(request)
    _save_customer(request, customer)
    _save_country(request, customer)

    result = simplejson.dumps({
        "shipping": shipping_inline(request),
        "payment": payment_inline(request, form),
        "cart": cart_inline(request),
    })

    return HttpResponse(result)


def changed_invoice_country(request):
    """
    Refreshes the invoice address form, after the invoice country has been
    changed.
    """
    customer = lfs.customer.utils.get_or_create_customer(request)
    address = customer.selected_invoice_address
    country_iso = request.POST.get("invoice-country")
    if address:
        address.country = Country.objects.get(code=country_iso.lower())
        address.save()

    am = AddressManagement(address, "invoice")
    result = simplejson.dumps({
        "invoice_address": am.render(request, country_iso),
    })

    return HttpResponse(result)


def changed_shipping_country(request):
    """
    Refreshes the shipping address form, after the shipping country has been
    changed.
    """
    customer = lfs.customer.utils.get_or_create_customer(request)
    address = customer.selected_shipping_address
    country_iso = request.POST.get("shipping-country")
    if address:
        address.country = Country.objects.get(code=country_iso.lower())
        address.save()

    am = AddressManagement(address, "shipping")
    result = simplejson.dumps({
        "shipping_address": am.render(request, country_iso),
    })

    return HttpResponse(result)


def _save_country(request, customer):
    """
    """
    # Update shipping country
    country_iso = request.POST.get("shipping-country", None)
    if request.POST.get("no_shipping") == "on":
        country_iso = request.POST.get("invoice-country", None)

    if country_iso is not None:
        country = Country.objects.get(code=country_iso.lower())
        if customer.selected_shipping_address:
            customer.selected_shipping_address.country = country
            customer.selected_shipping_address.save()
        customer.selected_country = country
        customer.save()

        lfs.shipping.utils.update_to_valid_shipping_method(request, customer)
        lfs.payment.utils.update_to_valid_payment_method(request, customer)
        customer.save()


def _save_customer(request, customer):
    """
    """
    shipping_method = request.POST.get("shipping-method")
    customer.selected_shipping_method_id = shipping_method

    payment_method = request.POST.get("payment_method")
    customer.selected_payment_method_id = payment_method

    customer.save()

    lfs.shipping.utils.update_to_valid_shipping_method(request, customer)
    lfs.payment.utils.update_to_valid_payment_method(request, customer)
    customer.save()
