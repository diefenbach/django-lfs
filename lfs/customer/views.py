# python imports
import datetime
from urlparse import urlparse

# django imports
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

# lfs imports
import lfs
from lfs.addresses.utils import AddressManagement
from lfs.customer import utils as customer_utils
from lfs.customer.forms import EmailForm, CustomerAuthenticationForm
from lfs.customer.forms import RegisterForm
from lfs.customer.utils import create_unique_username
from lfs.order.models import Order


def login(request, template_name="lfs/customer/login.html"):
    """Custom view to login or register/login a user.

    The reason to use a custom login method are:

      * validate checkout type
      * integration of register and login form

    It uses Django's standard AuthenticationForm, though.
    """
    # shop = lfs.core.utils.get_default_shop(request)

    # If only anonymous checkout is allowed this view doesn't exists :)
    # if shop.checkout_type == CHECKOUT_TYPE_ANON:
    #     raise Http404()

    login_form = CustomerAuthenticationForm()
    login_form.fields["username"].label = _(u"E-Mail")
    register_form = RegisterForm()

    if request.POST.get("action") == "login":
        login_form = CustomerAuthenticationForm(data=request.POST)
        login_form.fields["username"].label = _(u"E-Mail")

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
                username=create_unique_username(email), email=email, password=password)

            # Create customer
            customer = customer_utils.get_or_create_customer(request)
            customer.user = user
            customer.save()

            # Notify
            lfs.core.signals.customer_added.send(sender=user)

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
    next_url = (request.POST if request.method == 'POST' else request.GET).get("next")
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

    return render(request, template_name, {
        "login_form": login_form,
        "login_form_errors": login_form_errors,
        "register_form": register_form,
        "next_url": next_url,
    })


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

    if request.method == "GET":
        date_filter = request.session.get("my-orders-date-filter")
    else:
        date_filter = request.POST.get("date-filter")
        if date_filter:
            request.session["my-orders-date-filter"] = date_filter
        else:
            try:
                del request.session["my-orders-date-filter"]
            except KeyError:
                pass
    try:
        date_filter = int(date_filter)
    except (ValueError, TypeError):
        date_filter = None
    else:
        now = datetime.datetime.now()
        start = now - datetime.timedelta(days=date_filter * 30)
        orders = orders.filter(created__gte=start)

    options = []
    for value in [1, 3, 6, 12]:
        selected = True if value == date_filter else False
        options.append({
            "value": value,
            "selected": selected,
        })

    return render(request, template_name, {
        "orders": orders,
        "options": options,
        "date_filter": date_filter,
        "current": "orders"
    })


@login_required
def order(request, id, template_name="lfs/customer/order.html"):
    """
    """
    orders = Order.objects.filter(user=request.user)
    order = get_object_or_404(Order, pk=id, user=request.user)

    return render(request, template_name, {
        "current_order": order,
        "orders": orders,
        "current": "orders"
    })


@login_required
def account(request, template_name="lfs/customer/account.html"):
    """Displays the main screen of the current user's account.
    """
    user = request.user

    return render(request, template_name, {
        "user": user,
        "current": "welcome"
    })


@login_required
def addresses(request, template_name="lfs/customer/addresses.html"):
    """
    Provides a form to edit addresses in my account.
    """
    customer = lfs.customer.utils.get_or_create_customer(request)

    if request.method == "POST":
        iam = AddressManagement(customer, customer.default_invoice_address, "invoice", request.POST)
        sam = AddressManagement(customer, customer.default_shipping_address, "shipping", request.POST)

        if iam.is_valid() and sam.is_valid():
            iam.save()
            sam.save()

            customer.sync_default_to_selected_addresses(force=True)

            return lfs.core.utils.MessageHttpResponseRedirect(
                redirect_to=reverse("lfs_my_addresses"),
                msg=_(u"Your addresses have been saved."),
            )
        else:
            msg = _(u"An error has occured.")
    else:
        msg = None
        iam = AddressManagement(customer, customer.default_invoice_address, "invoice")
        sam = AddressManagement(customer, customer.default_shipping_address, "shipping")

    return lfs.core.utils.render_to_message_response(
        request,
        template_name, {
            "shipping_address_inline": sam.render(request),
            "invoice_address_inline": iam.render(request),
            "current": "addresses"
        },
        msg=msg,
    )


@login_required
def email(request, template_name="lfs/customer/email.html"):
    """Saves the email address from the data form.
    """
    if request.method == "POST":
        email_form = EmailForm(initial={"email": request.user.email}, data=request.POST)
        if email_form.is_valid():
            request.user.username = email_form.cleaned_data.get("email")[:30]
            request.user.email = email_form.cleaned_data.get("email")
            request.user.save()
            return lfs.core.utils.set_message_cookie(reverse("lfs_my_email"),
                                                     msg=_(u"Your e-mail has been changed."))
    else:
        email_form = EmailForm(initial={"email": request.user.email})

    return render(request, template_name, {
        "email_form": email_form,
        "current": "email"
    })


@login_required
def password(request, template_name="lfs/customer/password.html"):
    """Changes the password of current user.
    """
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return lfs.core.utils.set_message_cookie(reverse("lfs_my_password"),
                                                     msg=_(u"Your password has been changed."))
    else:
        form = PasswordChangeForm(request.user)

    return render(request, template_name, {
        "form": form,
        "current": "password"
    })
