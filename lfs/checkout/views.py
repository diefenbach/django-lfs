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
from lfs.cart import utils as cart_utils
from lfs.checkout.forms import OnePageCheckoutForm
from lfs.checkout.settings import CHECKOUT_TYPE_ANON
from lfs.checkout.settings import CHECKOUT_TYPE_AUTH
from lfs.customer import utils as customer_utils
from lfs.customer.models import Address
from lfs.customer.models import BankAccount
from lfs.customer.forms import RegisterForm
from lfs.payment.models import PaymentMethod
from lfs.payment.settings import PAYPAL
from lfs.payment.settings import DIRECT_DEBIT
from lfs.payment.settings import CREDIT_CARD
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

    shop = lfs.core.utils.get_default_shop()

    # If only anonymous checkout allowed we don't want to show this view at all.
    if shop.checkout_type == CHECKOUT_TYPE_ANON:
        return HttpResponseRedirect(reverse("lfs_checkout"))

    # Using Djangos default AuthenticationForm
    login_form = AuthenticationForm()
    login_form.fields["username"].label = _(u"E-Mail")
    register_form = RegisterForm()

    if request.POST.get("action") == "login":
        login_form = AuthenticationForm(data=request.POST)
        if login_form.is_valid():
            from django.contrib.auth import login
            login(request, login_form.get_user())

            return lfs.core.utils.set_message_cookie(reverse("lfs_checkout"),
                msg = _(u"You have been logged in."))

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
                msg = _(u"You have been registered and logged in."))

    return render_to_response(template_name, RequestContext(request, {
        "login_form" : login_form,
        "register_form" : register_form,
        "anonymous_checkout" : shop.checkout_type != CHECKOUT_TYPE_AUTH,
    }))

def checkout_dispatcher(request):
    """Dispatcher to display the correct checkout form
    """
    shop = lfs.core.utils.get_default_shop()
    cart = cart_utils.get_cart(request)

    if cart is None or not cart.items():
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
    cart_costs = cart_utils.get_cart_costs(request, cart)
    cart_price = cart_costs["price"] + shipping_costs["price"] + payment_costs["price"]
    cart_tax = cart_costs["tax"] + shipping_costs["tax"] + payment_costs["tax"]

    discounts = lfs.discounts.utils.get_valid_discounts(request)
    for discount in discounts:
        cart_price = cart_price - discount["price"]
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
        is_voucher_effective, voucher_message = voucher.is_effective(cart)
        if is_voucher_effective:
            display_voucher = True
            voucher_value = voucher.get_price_gross(cart)
            cart_price = cart_price - voucher_value
            voucher_tax = voucher.get_tax(cart)
        else:
            display_voucher = False
            voucher_value = 0
            voucher_tax = 0

    return render_to_string(template_name, RequestContext(request, {
        "cart" : cart,
        "cart_price" : cart_price,
        "cart_tax" : cart_tax,
        "display_voucher" : display_voucher,
        "discounts" : discounts,
        "voucher_value" : voucher_value,
        "voucher_tax" : voucher_tax,
        "shipping_price" : shipping_costs["price"],
        "payment_price" : payment_costs["price"],
        "selected_shipping_method" : selected_shipping_method,
        "selected_payment_method" : selected_payment_method,
        "voucher_number" : voucher_number,
        "voucher_message" : voucher_message,
    }))

def one_page_checkout(request, checkout_form = OnePageCheckoutForm,
    template_name="lfs/checkout/one_page_checkout.html"):
    """One page checkout form.
    """
    # If the user is not authenticated and the if only authenticate checkout
    # allowed we rediret to authentication page.
    shop = lfs.core.utils.get_default_shop()
    if request.user.is_anonymous() and \
       shop.checkout_type == CHECKOUT_TYPE_AUTH:
        return HttpResponseRedirect(reverse("lfs_checkout_login"))

    customer = customer_utils.get_or_create_customer(request)
    if request.method == "POST":
        form = checkout_form(request.POST)

        toc = True

        if shop.confirm_toc:
            if not request.POST.has_key("confirm_toc"):
                toc = False
                if form._errors is None:
                    form._errors = {}
                form._errors["confirm_toc"] = _(u"Please confirm our terms and conditions")

        if toc and form.is_valid():
            # Create or update invoice address
            if customer.selected_invoice_address is None:
                invoice_address = Address.objects.create(
                    firstname = form.cleaned_data.get("invoice_firstname"),
                    lastname = form.cleaned_data.get("invoice_lastname"),
                    company_name = form.cleaned_data.get("invoice_company_name"),
                    street = form.cleaned_data.get("invoice_street"),
                    zip_code = form.cleaned_data.get("invoice_zip_code"),
                    city = form.cleaned_data.get("invoice_city"),
                    country_id = form.cleaned_data.get("invoice_country"),
                    phone = form.cleaned_data.get("invoice_phone"),
                    email = form.cleaned_data.get("invoice_email"),
                    customer = customer,
                )
                customer.selected_invoice_address = invoice_address
            else:
                selected_invoice_address = customer.selected_invoice_address
                selected_invoice_address.firstname = form.cleaned_data.get("invoice_firstname")
                selected_invoice_address.lastname = form.cleaned_data.get("invoice_lastname")
                selected_invoice_address.company_name = form.cleaned_data.get("invoice_company_name")
                selected_invoice_address.street = form.cleaned_data.get("invoice_street")
                selected_invoice_address.zip_code = form.cleaned_data.get("invoice_zip_code")
                selected_invoice_address.city = form.cleaned_data.get("invoice_city")
                selected_invoice_address.country_id = form.cleaned_data.get("invoice_country")
                selected_invoice_address.phone = form.cleaned_data.get("invoice_phone")
                selected_invoice_address.email = form.cleaned_data.get("invoice_email")
                selected_invoice_address.customer = customer
                selected_invoice_address.save()

            # If the shipping address differs from invoice firstname we create
            # or update the shipping address.
            if not form.cleaned_data.get("no_shipping"):
                if customer.selected_shipping_address is None:
                    shipping_address = Address.objects.create(
                        firstname = form.cleaned_data.get("shipping_firstname"),
                        lastname = form.cleaned_data.get("shipping_lastname"),
                        company_name = form.cleaned_data.get("shipping_company_name"),
                        street = form.cleaned_data.get("shipping_street"),
                        zip_code = form.cleaned_data.get("shipping_zip_code"),
                        city = form.cleaned_data.get("shipping_city"),
                        country_id = form.cleaned_data.get("shipping_country"),
                        phone = form.cleaned_data.get("shipping_phone"),
                        email = form.cleaned_data.get("shipping_email"),
                        customer = customer,
                    )
                    customer.selected_shipping_address = shipping_address
                else:
                    selected_shipping_address = customer.selected_shipping_address
                    selected_shipping_address.firstname = form.cleaned_data.get("shipping_firstname")
                    selected_shipping_address.lastname = form.cleaned_data.get("shipping_lastname")
                    selected_shipping_address.company_name = form.cleaned_data.get("shipping_company_name")
                    selected_shipping_address.street = form.cleaned_data.get("shipping_street")
                    selected_shipping_address.zip_code = form.cleaned_data.get("shipping_zip_code")
                    selected_shipping_address.city = form.cleaned_data.get("shipping_city")
                    selected_shipping_address.country_id = form.cleaned_data.get("shipping_country")
                    selected_shipping_address.phone = form.cleaned_data.get("shipping_phone")
                    selected_shipping_address.customer = customer
                    selected_shipping_address.save()

            # Payment method
            customer.selected_payment_method_id = request.POST.get("payment_method")

            if int(form.data.get("payment_method")) == DIRECT_DEBIT:
                bank_account = BankAccount.objects.create(
                    account_number = form.cleaned_data.get("account_number"),
                    bank_identification_code = form.cleaned_data.get("bank_identification_code"),
                    bank_name = form.cleaned_data.get("bank_name"),
                    depositor = form.cleaned_data.get("depositor"),
                )

                customer.selected_bank_account = bank_account

            # Save the selected information to the customer
            customer.save()

            # process the payment method ...
            result = lfs.payment.utils.process_payment(request)

            next_url = None
            if result["accepted"] == True:
                return HttpResponseRedirect(
                    result.get("next-url", reverse("lfs_thank_you")))
            else:
                if result.has_key("message"):
                    form._errors[result.get("message-position")] = result.get("message")

        else: # form is not valid
            # Create or update invoice address
            if customer.selected_invoice_address is None:
                invoice_address = Address.objects.create(
                    firstname = form.data.get("invoice_firstname", ""),
                    lastname = form.data.get("invoice_lastname", ""),
                    company_name = form.data.get("invoice_company_name", ""),
                    street = form.data.get("invoice_street", ""),
                    zip_code = form.data.get("invoice_zip_code", ""),
                    city = form.data.get("invoice_city", ""),
                    country_id = form.data.get("invoice_country", ""),
                    phone = form.data.get("invoice_phone", ""),
                    email = form.data.get("invoice_email", ""),
                )
                customer.selected_invoice_address = invoice_address
            else:
                selected_invoice_address = customer.selected_invoice_address
                selected_invoice_address.firstname = form.data.get("invoice_firstname", "")
                selected_invoice_address.lastname = form.data.get("invoice_lastname", "")
                selected_invoice_address.company_name = form.data.get("invoice_company_name", "")
                selected_invoice_address.street = form.data.get("invoice_street", "")
                selected_invoice_address.zip_code = form.data.get("invoice_zip_code", "")
                selected_invoice_address.city = form.data.get("invoice_city", "")
                selected_invoice_address.country_id = form.data.get("invoice_country", "")
                selected_invoice_address.phone = form.data.get("invoice_phone", "")
                selected_invoice_address.email = form.data.get("invoice_email", "")
                selected_invoice_address.save()

            # If the shipping address differs from invoice firstname we create
            # or update the shipping address.
            if not form.data.get("no_shipping"):
                if customer.selected_shipping_address is None:
                    shipping_address = Address.objects.create(
                        firstname = form.data.get("shipping_firstname"),
                        lastname = form.data.get("shipping_lastname"),
                        company_name = form.data.get("shipping_company_name"),
                        street = form.data.get("shipping_street"),
                        zip_code = form.data.get("shipping_zip_code"),
                        city = form.data.get("shipping_city"),
                        country_id = form.data.get("shipping_country"),
                        phone = form.data.get("shipping_phone"),
                        email = form.data.get("shipping_email"),
                    )
                    customer.selected_shipping_address = shipping_address
                else:
                    selected_shipping_address = customer.selected_shipping_address
                    selected_shipping_address.firstname = form.data.get("shipping_firstname")
                    selected_shipping_address.lastname = form.data.get("shipping_lastname")
                    selected_shipping_address.company_name = form.data.get("shipping_company_name")
                    selected_shipping_address.street = form.data.get("shipping_street")
                    selected_shipping_address.zip_code = form.data.get("shipping_zip_code")
                    selected_shipping_address.city = form.data.get("shipping_city")
                    selected_shipping_address.country_id = form.data.get("shipping_country")
                    selected_shipping_address.phone = form.data.get("shipping_phone")
                    selected_shipping_address.save()

            # Payment method
            customer.selected_payment_method_id = request.POST.get("payment_method")

            # 1 = Direct Debit
            if int(form.data.get("payment_method")) == DIRECT_DEBIT:
                bank_account = BankAccount.objects.create(
                    account_number = form.data.get("account_number"),
                    bank_identification_code = form.data.get("bank_identification_code"),
                    bank_name = form.data.get("bank_name"),
                    depositor = form.data.get("depositor"),
                )

                customer.selected_bank_account = bank_account

            # Save the selected information to the customer
            customer.save()

    else:
        # If there are addresses intialize the form.
        initial = {}
        if customer.selected_invoice_address is not None:
            invoice_address = customer.selected_invoice_address
            initial.update({
                "invoice_firstname" : invoice_address.firstname,
                "invoice_lastname" : invoice_address.lastname,
                "invoice_street" : invoice_address.street,
                "invoice_zip_code" : invoice_address.zip_code,
                "invoice_city" : invoice_address.city,
                "invoice_country" : invoice_address.country_id,
                "invoice_phone" : invoice_address.phone,
                "invoice_email" : invoice_address.email,
            })
        if customer.selected_shipping_address is not None:
            shipping_address = customer.selected_shipping_address
            initial.update({
                "shipping_firstname" : shipping_address.firstname,
                "shipping_lastname" : shipping_address.lastname,
                "shipping_street" : shipping_address.street,
                "shipping_zip_code" : shipping_address.zip_code,
                "shipping_city" : shipping_address.city,
                "shipping_phone" : shipping_address.phone,
                "shipping_email" : shipping_address.email,
                "no_shipping" : False,
            })

        # Set the addresses country to the current selected in any case.
        country = lfs.shipping.utils.get_selected_shipping_country(request)
        if country:
            initial["shipping_country"] = country.id
            initial["invoice_country"] = country.id
        form = checkout_form(initial=initial)

    cart = cart_utils.get_cart(request)
    if cart is None:
        return HttpResponseRedirect(reverse('lfs_cart'))

    # Payment
    try:
        selected_payment_method_id = request.POST.get("payment_method")
        selected_payment_method = PaymentMethod.objects.get(pk=selected_payment_method_id)
    except PaymentMethod.DoesNotExist:
        selected_payment_method = lfs.payment.utils.get_selected_payment_method(request)

    valid_payment_methods = lfs.payment.utils.get_valid_payment_methods(request)
    valid_payment_method_ids = [m.id for m in valid_payment_methods]

    display_bank_account = DIRECT_DEBIT in valid_payment_method_ids
    display_credit_card = CREDIT_CARD in valid_payment_method_ids

    response = render_to_response(template_name, RequestContext(request, {
        "form" : form,
        "cart_inline" : cart_inline(request),
        "shipping_inline" : shipping_inline(request),
        "payment_inline" : payment_inline(request, form),
        "selected_payment_method" : selected_payment_method,
        "display_bank_account" : display_bank_account,
        "display_credit_card" : display_credit_card,
        "voucher_number" : lfs.voucher.utils.get_current_voucher_number(request),
    }))

    if form._errors:
        return lfs.core.utils.set_message_to(response, _(u"An error has been occured."))
    else:
        return response

def empty_page_checkout(request, template_name="lfs/checkout/empty_page_checkout.html"):
    """
    """
    return render_to_response(template_name, RequestContext(request, {
        "shopping_url" : reverse("lfs.core.views.shop_view"),
    }))

def thank_you(request, template_name="lfs/checkout/thank_you_page.html"):
    """Displays a thank you page ot the customer
    """
    order = request.session.get("order")
    return render_to_response(template_name, RequestContext(request, {
        "order" : order,
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
        "payment_methods" : valid_payment_methods,
        "selected_payment_method" : selected_payment_method,
        "form" : form,
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
        "shipping_methods" : shipping_methods,
        "selected_shipping_method" : selected_shipping_method,
    }))

def check_voucher(request):
    """
    """
    voucher_number = lfs.voucher.utils.get_current_voucher_number(request)
    lfs.voucher.utils.set_current_voucher_number(request, voucher_number)

    result = simplejson.dumps({
        "html" : (("#cart-inline", cart_inline(request)),)
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
        "shipping" : shipping_inline(request),
        "payment" : payment_inline(request, form),
        "cart" : cart_inline(request),
    })

    return HttpResponse(result)

def _save_country(request, customer):
    """
    """
    # Update shipping country
    country = request.POST.get("shipping_country")
    if request.POST.get("no_shipping") == "on":
        country = request.POST.get("invoice_country")

    if customer.selected_shipping_address:
        customer.selected_shipping_address.country_id = country
        customer.selected_shipping_address.save()
    customer.selected_country_id = country
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
