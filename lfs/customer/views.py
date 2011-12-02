# python imports
from urlparse import urlparse

# django imports
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.utils import simplejson
from django.http import HttpResponse

# lfs imports
import lfs
from lfs.checkout.settings import INVOICE_PREFIX, SHIPPING_PREFIX
from lfs.core.settings import POSTAL_ADDRESS_L10N
from lfs.core.models import Country
from lfs.customer import utils as customer_utils
from lfs.customer.forms import EmailForm
from lfs.customer.forms import RegisterForm
from lfs.customer.forms import AddressForm
from lfs.customer.models import Address
from lfs.order.models import Order

# other imports
from postal.library import form_factory
from postal.forms import PostalAddressForm


def login(request, template_name="lfs/customer/login.html"):
    """Custom view to login or register/login a user.

    The reason to use a custom login method are:

      * validate checkout type
      * integration of register and login form

    It uses Django's standard AuthenticationForm, though.
    """
    shop = lfs.core.utils.get_default_shop()

    # If only anonymous checkout is allowed this view doesn't exists :)
    # if shop.checkout_type == CHECKOUT_TYPE_ANON:
    #     raise Http404()

    # Using Djangos default AuthenticationForm
    login_form = AuthenticationForm()
    login_form.fields["username"].label = _(u"E-Mail")
    register_form = RegisterForm()

    if request.POST.get("action") == "login":
        login_form = AuthenticationForm(data=request.POST)

        if login_form.is_valid():
            redirect_to = request.POST.get("next")
            # Light security check -- make sure redirect_to isn't garbage.
            if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
                redirect_to = reverse("lfs_shop_view")

            from django.contrib.auth import login
            login(request, login_form.get_user())

            return lfs.core.utils.set_message_cookie(
                redirect_to, msg=_(u"You have been logged in."))

    elif request.POST.get("action") == "register":
        register_form = RegisterForm(data=request.POST)
        if register_form.is_valid():

            email = register_form.data.get("email")
            password = register_form.data.get("password_1")

            # Create user
            user = User.objects.create_user(
                username=email, email=email, password=password)

            # Create customer
            customer = customer_utils.get_or_create_customer(request)
            customer.user = user

            # Notify
            lfs.core.signals.customer_added.send(user)

            # Log in user
            from django.contrib.auth import authenticate
            user = authenticate(username=email, password=password)

            from django.contrib.auth import login
            login(request, user)

            redirect_to = request.POST.get("next")
            if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
                redirect_to = reverse("lfs_shop_view")

            return lfs.core.utils.set_message_cookie(
                redirect_to, msg=_(u"You have been registered and logged in."))

    # Get next_url
    next_url = request.REQUEST.get("next")
    if next_url is None:
        next_url = request.META.get("HTTP_REFERER")
    if next_url is None:
        next_url = reverse("lfs_shop_view")

    # Get just the path of the url. See django.contrib.auth.views.login for more
    next_url = urlparse(next_url)
    next_url = next_url[2]

    try:
        login_form_errors = login_form.errors["__all__"]
    except KeyError:
        login_form_errors = None

    return render_to_response(template_name, RequestContext(request, {
        "login_form": login_form,
        "login_form_errors": login_form_errors,
        "register_form": register_form,
        "next_url": next_url,
    }))


def logout(request):
    """Custom method to logout a user.

    The reason to use a custom logout method is just to provide a login and a
    logoutmethod on one place.
    """
    from django.contrib.auth import logout
    logout(request)

    return lfs.core.utils.set_message_cookie(reverse("lfs_shop_view"),
        msg=_(u"You have been logged out."))


@login_required
def orders(request, template_name="lfs/customer/orders.html"):
    """Displays the orders of the current user
    """
    orders = Order.objects.filter(user=request.user)

    return render_to_response(template_name, RequestContext(request, {
        "orders": orders,
    }))


@login_required
def order(request, id, template_name="lfs/customer/order.html"):
    """
    """
    orders = Order.objects.filter(user=request.user)
    order = get_object_or_404(Order, pk=id, user=request.user)

    return render_to_response(template_name, RequestContext(request, {
        "current_order": order,
        "orders": orders,
    }))


@login_required
def account(request, template_name="lfs/customer/account.html"):
    """Displays the main screen of the current user's account.
    """
    user = request.user

    return render_to_response(template_name, RequestContext(request, {
        "user": user,
    }))


@login_required
def addresses(request, template_name="lfs/customer/addresses.html"):
    """Provides a form to edit addresses and bank account.
    """
    customer = lfs.customer.utils.get_customer(request)
    shop = lfs.core.utils.get_default_shop()

    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            save_address(request, customer, INVOICE_PREFIX)
            save_address(request, customer, SHIPPING_PREFIX)
            customer.selected_invoice_address.customer = customer
            customer.selected_invoice_address.firstname = form.cleaned_data['invoice_firstname']
            customer.selected_invoice_address.lastname = form.cleaned_data['invoice_lastname']
            customer.selected_invoice_address.phone = form.cleaned_data['invoice_phone']
            customer.selected_invoice_address.email = form.cleaned_data['invoice_email']
            customer.selected_invoice_address.save()
            customer.selected_shipping_address.customer = customer
            customer.selected_shipping_address.firstname = form.cleaned_data['shipping_firstname']
            customer.selected_shipping_address.lastname = form.cleaned_data['shipping_lastname']
            customer.selected_shipping_address.phone = form.cleaned_data['shipping_phone']
            customer.selected_shipping_address.email = form.cleaned_data['shipping_email']
            customer.selected_shipping_address.save()
            return HttpResponseRedirect(reverse("lfs_my_addresses"))
    else:
        initial = {}
        if customer:
            if customer.selected_invoice_address is not None:
                initial.update({"invoice_firstname": customer.selected_invoice_address.firstname,
                                "invoice_lastname": customer.selected_invoice_address.lastname,
                                "invoice_phone": customer.selected_invoice_address.phone,
                                "invoice_email": customer.selected_invoice_address.email,
                                })
            if customer.selected_shipping_address is not None:
                initial.update({"shipping_firstname": customer.selected_shipping_address.firstname,
                                "shipping_lastname": customer.selected_shipping_address.lastname,
                                "shipping_phone": customer.selected_shipping_address.phone,
                                "shipping_email": customer.selected_shipping_address.email,
                                })

        form = AddressForm(initial=initial)
    return render_to_response(template_name, RequestContext(request, {
        "form": form,
        "shipping_address_inline": address_inline(request, "shipping", form),
        "invoice_address_inline": address_inline(request, "invoice", form),
    }))


def get_country_code(request, prefix):
    # get country_code from the request
    country_code = request.POST.get(prefix + '-country', '')

    # get country code from customer
    if country_code == '':
        customer = customer_utils.get_or_create_customer(request)
        if prefix == INVOICE_PREFIX:
            if customer.selected_invoice_address is not None:
                if customer.selected_invoice_address.country is not None:
                    country_code = customer.selected_invoice_address.country.code
        elif prefix == SHIPPING_PREFIX:
            if customer.selected_shipping_address is not None:
                if customer.selected_shipping_address.country is not None:
                    country_code = customer.selected_shipping_address.country.code

    # get country code from shop
    if country_code == '':
        shop = lfs.core.utils.get_default_shop()
        if shop.default_country is not None:
            country_code = shop.default_country.code
    return country_code


def address_inline(request, prefix, form):
    """displays the invoice address with localized fields
    """
    template_name = "lfs/customer/" + prefix + "_address_inline.html"
    country_code = get_country_code(request, prefix)
    if country_code != '':
        shop = lfs.core.utils.get_default_shop()
        countries = None
        if prefix == INVOICE_PREFIX:
            countries = shop.invoice_countries.all()
        else:
            countries = shop.shipping_countries.all()
        customer = customer_utils.get_or_create_customer(request)
        address_form_class = form_factory(country_code)
        if request.method == 'POST':
            if POSTAL_ADDRESS_L10N == True:
                address_form = address_form_class(prefix=prefix, data=request.POST,)
            else:
                address_form = PostalAddressForm(prefix=prefix, data=request.POST,)
            if countries is not None:
                address_form.fields["country"].choices = [(c.code.upper(), c.name) for c in countries]
            save_address(request, customer, prefix)
        else:
            # If there are addresses intialize the form.
            initial = {}
            customer_selected_address = None
            if hasattr(customer, 'selected_' + prefix + '_address'):
                customer_selected_address = getattr(customer, 'selected_' + prefix + '_address')
            if customer_selected_address is not None:
                initial.update({
                    "line1": customer_selected_address.company_name,
                    "line2": customer_selected_address.street,
                    "city": customer_selected_address.city,
                    "state": customer_selected_address.state,
                    "code": customer_selected_address.zip_code,
                    "country": customer_selected_address.country.code.upper(),
                })
                address_form = address_form_class(prefix=prefix, initial=initial)
            else:
                address_form = address_form_class(prefix=prefix)
                address_form.fields["country"].initial = country_code
            if countries is not None:
                address_form.fields["country"].choices = [(c.code.upper(), c.name) for c in countries]

    # Removes fields from address form if requested via settings.
    for i in range(1, 6):
        address_settings = getattr(settings, "POSTAL_ADDRESS_LINE%s" % i, None)
        try:
            if address_settings and address_settings[2] == False:
                del address_form.fields["line%s" % i]
        except IndexError:
            pass

    # if request via ajax don't display validity errors
    if request.is_ajax():
        address_form._errors = {}
    return render_to_string(template_name, RequestContext(request, {
        "address_form": address_form,
        "form": form,
    }))


def save_address(request, customer, prefix):
    # get the shop
    shop = lfs.core.utils.get_default_shop()

    # get the country for the address
    country_iso = request.POST.get(prefix + "-country", shop.default_country.code)

    # check have we a valid address
    form_class = form_factory(country_iso)
    valid_address = False
    form_obj = form_class(request.POST, prefix=prefix)
    if form_obj.is_valid():
        valid_address = True

    customer_selected_address = None
    address_attribute = 'selected_' + prefix + '_address'
    existing_address = False
    if hasattr(customer, address_attribute):
        customer_selected_address = getattr(customer, address_attribute)
        if customer_selected_address is not None:
            existing_address = True
            customer_selected_address.company_name = request.POST.get(prefix + "-line1", "")
            customer_selected_address.street = request.POST.get(prefix + "-line2", "")
            customer_selected_address.city = request.POST.get(prefix + "-city", "")
            customer_selected_address.state = request.POST.get(prefix + "-state", "")
            customer_selected_address.zip_code = request.POST.get(prefix + "-code", "")
            customer_selected_address.country = Country.objects.get(code=country_iso.lower())
            customer_selected_address.save()
    if not existing_address:
        # no address exists for customer so create one
        customer_selected_address = Address.objects.create(customer=customer,
                                                           company_name=request.POST.get(prefix + "-line1", ""),
                                                           street=request.POST.get(prefix + "-line2", ""),
                                                           city=request.POST.get(prefix + "-city", ""),
                                                           state=request.POST.get(prefix + "-state", ""),
                                                           zip_code=request.POST.get(prefix + "-code", ""),
                                                           country=Country.objects.get(code=country_iso.lower()))
    setattr(customer, address_attribute, customer_selected_address)
    customer.save()
    return valid_address


@login_required
def email(request, template_name="lfs/customer/email.html"):
    """Saves the email address from the data form.
    """
    if request.method == "POST":
        email_form = EmailForm(initial={"email": request.user.email}, data=request.POST)
        if email_form.is_valid():
            request.user.email = email_form.cleaned_data.get("email")
            request.user.save()
            return HttpResponseRedirect(reverse("lfs_my_email"))
    else:
        email_form = EmailForm(initial={"email": request.user.email})

    return render_to_response(template_name, RequestContext(request, {
        "email_form": email_form
    }))


@login_required
def password(request, template_name="lfs/customer/password.html"):
    """Changes the password of current user.
    """
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("lfs_my_password"))
    else:
        form = PasswordChangeForm(request.user)

    return render_to_response(template_name, RequestContext(request, {
        "form": form
    }))
