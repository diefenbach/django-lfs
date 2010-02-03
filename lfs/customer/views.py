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
from django.template.loader import render_to_string
from django.utils import simplejson
from django.http import HttpResponse

# lfs imports
import lfs
from lfs.checkout.settings import INVOICE_PREFIX, SHIPPING_PREFIX
from lfs.core.settings import LFS_ADDRESS_L10N
from lfs.customer import utils as customer_utils
from lfs.customer.forms import EmailForm
from lfs.customer.forms import RegisterForm
from lfs.customer.forms import AddressForm
from lfs.order.models import Order

# other imports
from postal.library import get_postal_form_class
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
    customer = lfs.customer.utils.get_customer(request)
    shop = lfs.core.utils.get_default_shop()
    
    if request.method == "POST":
        extra_data = {}
        prefixes = [INVOICE_PREFIX, SHIPPING_PREFIX]
        for prefix in prefixes:
            for field_name in PostalAddressForm.base_fields.keys():
                field_value = request.POST.get(prefix + '-' + field_name, None)
                if field_value is not None:
                    extra_data.update({prefix + '_' + field_name:field_value})

        mutable_data = request.POST.copy()
        mutable_data.update(extra_data)
        
        form = AddressForm(mutable_data)
        if form.is_valid():
            save_address(request, customer, INVOICE_PREFIX)
            save_address(request, customer, SHIPPING_PREFIX)
            customer.selected_invoice_phone = form.cleaned_data['invoice_phone']
            customer.selected_invoice_email = form.cleaned_data['invoice_email']
            customer.selected_shipping_phone = form.cleaned_data['shipping_phone']
            customer.selected_shipping_email = form.cleaned_data['shipping_email']
            customer.save()
            return HttpResponseRedirect(reverse("lfs_my_addresses"))
    else:
        initial = {"invoice_phone": customer.selected_invoice_phone,
                   "invoice_email": customer.selected_invoice_email,
                   "shipping_email": customer.selected_shipping_email,
                   "shipping_phone": customer.selected_shipping_phone}
        form = AddressForm(initial=initial)
    return render_to_response(template_name, RequestContext(request, {
        "form": form,
        "shipping_address_inline" : address_inline(request, "shipping", form),
        "invoice_address_inline" : address_inline(request, "invoice", form),
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
                    country_code = customer.selected_invoice_address.country.iso
        elif prefix == SHIPPING_PREFIX:
            if customer.selected_shipping_address is not None:
                if customer.selected_shipping_address.country is not None:
                    country_code = customer.selected_shipping_address.country.iso

    # get country code from shop
    if country_code == '':
        shop = lfs.core.utils.get_default_shop()
        if shop.default_country is not None:
            country_code = shop.default_country.iso
    return country_code


def address_inline(request, prefix, form):
    """displays the invoice address with localized fields
    """
    template_name="lfs/checkout/" + prefix + "_address_inline.html"
    country_code = get_country_code(request, prefix)
    if country_code != '':
        shop = lfs.core.utils.get_default_shop()
        countries = shop.countries.all()
        customer = customer_utils.get_or_create_customer(request)
        address_form_class = get_postal_form_class(country_code)

        if request.method == 'POST':
            if LFS_ADDRESS_L10N == True:
                address_form = address_form_class(prefix=prefix, data=request.POST,)
            else:
                address_form = PostalAddressForm(prefix=prefix, data=request.POST,)
            address_form.fields["country"].choices = [(c.iso, c.name) for c in countries]
            save_address(request, customer, prefix)
        else:
             # If there are addresses intialize the form.
            initial = {}
            customer_selected_address = None
            if hasattr(customer, 'selected_' + prefix + '_address'):
                customer_selected_address = getattr(customer, 'selected_' + prefix + '_address')
            if customer_selected_address is not None:
                initial.update({
                    "firstname" : customer_selected_address.firstname,
                    "lastname" : customer_selected_address.lastname,
                    "line1" : customer_selected_address.line1,
                    "line2" : customer_selected_address.line2,
                    "line3" : customer_selected_address.line3,
                    "line4" : customer_selected_address.line4,
                    "line5" : customer_selected_address.line5,
                    "country" : customer_selected_address.country.iso,
                })
            else:
                initial.update({prefix + "-country" : country_code,})
            address_form = address_form_class(prefix=prefix, initial=initial)
            address_form.fields["country"].choices = [(c.iso, c.name) for c in countries]

    return render_to_string(template_name, RequestContext(request, {
        "address_form": address_form,
        "form": form,
    }))

def save_address(request, customer, prefix):
    shop = lfs.core.utils.get_default_shop()
    customer_selected_address = None
    address_attribute = 'selected_' + prefix + '_address'
    if hasattr(customer, address_attribute):
        customer_selected_address = getattr(customer, address_attribute)

    if customer_selected_address is None:
        postal_address_form = PostalAddressForm(prefix=prefix,data=request.POST)
        setattr(customer, address_attribute, postal_address_form.save())
    else:
        customer_selected_address.firstname = request.POST.get(prefix + "-firstname")
        customer_selected_address.lastname = request.POST.get(prefix + "-lastname")
        customer_selected_address.line1 = request.POST.get(prefix + "-line1")
        customer_selected_address.line2 = request.POST.get(prefix + "-line2")
        customer_selected_address.line3 = request.POST.get(prefix + "-line3")
        customer_selected_address.line4 = request.POST.get(prefix + "-line4")
        customer_selected_address.line5 = request.POST.get(prefix + "-line5")
        customer_selected_address.country_iso = request.POST.get(prefix + "-country", shop.default_country.iso)
        customer_selected_address.save()
    customer.save()


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
    
