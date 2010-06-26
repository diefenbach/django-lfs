# python imports
from urlparse import urlparse

# django imports
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

# lfs imports
import lfs
from lfs.customer.forms import AddressForm
from lfs.customer.forms import EmailForm
from lfs.customer.forms import RegisterForm
from lfs.order.models import Order
from lfs.customer import utils as customer_utils

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
                redirect_to, msg = _(u"You have been logged in."))

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
                redirect_to, msg = _(u"You have been registered and logged in."))

    # Get next_url
    next_url = request.REQUEST.get("next")
    if next_url is None:
        next_url = request.META.get("HTTP_REFERER")
    if next_url is None:
        next_url =  reverse("lfs_shop_view")

    # Get just the path of the url. See django.contrib.auth.views.login for more
    next_url = urlparse(next_url)
    next_url = next_url[2]

    try:
        login_form_errors = login_form.errors["__all__"]
    except KeyError:
        login_form_errors = None

    return render_to_response(template_name, RequestContext(request, {
        "login_form" : login_form,
        "login_form_errors" : login_form_errors,
        "register_form" : register_form,
        "next_url" : next_url,
    }))

def logout(request):
    """Custom method to logout a user.

    The reason to use a custom logout method is just to provide a login and a
    logoutmethod on one place.
    """
    from django.contrib.auth import logout
    logout(request)

    return lfs.core.utils.set_message_cookie(reverse("lfs_shop_view"),
        msg = _(u"You have been logged out."))

@login_required
def orders(request, template_name="lfs/customer/orders.html"):
    """Displays the orders of the current user
    """
    orders = Order.objects.filter(user=request.user)

    return render_to_response(template_name, RequestContext(request, {
        "orders" : orders,
    }))

@login_required
def order(request, id, template_name="lfs/customer/order.html"):
    """
    """
    orders = Order.objects.filter(user=request.user)
    order = get_object_or_404(Order, pk=id, user=request.user)

    return render_to_response(template_name, RequestContext(request, {
        "current_order" : order,
        "orders" : orders,
    }))

@login_required
def account(request, template_name="lfs/customer/account.html"):
    """Displays the main screen of the current user's account.
    """
    user = request.user

    return render_to_response(template_name, RequestContext(request, {
        "user" : user,
    }))

@login_required
def addresses(request, template_name="lfs/customer/addresses.html"):
    """Provides a form to edit addresses and bank account.
    """
    user = request.user
    customer = lfs.customer.utils.get_or_create_customer(request)

    show_shipping_address = customer.selected_shipping_address and \
                            customer.selected_invoice_address.id != \
                            customer.selected_shipping_address.id

    if request.method == "POST":
        shipping_form = AddressForm(prefix="shipping", data=request.POST,
            instance = customer.selected_shipping_address)

        invoice_form = AddressForm(prefix="invoice", data=request.POST,
            instance = customer.selected_invoice_address)

        if show_shipping_address:
            if shipping_form.is_valid() and invoice_form.is_valid():
                shipping_address = shipping_form.save()
                shipping_address.customer = customer
                shipping_address.save()

                invoice_address = invoice_form.save()
                invoice_address.customer = customer
                invoice_address.save()

                customer.selected_invoice_address = invoice_address
                customer.selected_shipping_address = invoice_address
                customer.save()

                return HttpResponseRedirect(reverse("lfs_my_addresses"))
        else:
            if invoice_form.is_valid():
                invoice_address = invoice_form.save()
                invoice_address.customer = customer
                invoice_address.save()

                customer.selected_invoice_address = invoice_address
                customer.save()

                return HttpResponseRedirect(reverse("lfs_my_addresses"))
    else:

        shipping_form = AddressForm(prefix="shipping",
            instance=customer.selected_shipping_address)

        invoice_form = AddressForm(prefix="invoice",
            instance=customer.selected_invoice_address)

    return render_to_response(template_name, RequestContext(request, {
        "show_shipping_address" : show_shipping_address,
        "shipping_address_form" : shipping_form,
        "invoice_address_form" : invoice_form,
    }))

def email(request, template_name="lfs/customer/email.html"):
    """Saves the email address from the data form.
    """
    if request.method == "POST":
        email_form = EmailForm(initial={"email" : request.user.email}, data=request.POST)
        if email_form.is_valid():
            request.user.email = email_form.cleaned_data.get("email")
            request.user.save()
            return HttpResponseRedirect(reverse("lfs_my_email"))
    else:
        email_form = EmailForm(initial={"email" : request.user.email})

    return render_to_response(template_name, RequestContext(request, {
        "email_form": email_form
    }))

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
        "form" : form
    }))

