# django imports
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

# lfs imports
from lfs.addresses.settings import ADDRESS_MODEL
from lfs.customer.models import Customer
import lfs.core.utils


def get_or_create_customer(request):
    """Get or creates the customer object.
    """
    customer = get_customer(request)
    if customer is None:
        customer = request.customer = create_customer(request)

    return customer


def create_customer(request):
    """Creates a customer for the given request (which means for the current
    logged in user/or the session user).

    This shouldn't be called directly. Instead get_or_create_customer should be
    called.
    """
    if request.session.session_key is None:
        request.session.save()

    customer = Customer.objects.create(session=request.session.session_key)
    if request.user.is_authenticated():
        customer.user = request.user
    shop = lfs.core.utils.get_default_shop(request)

    address_model = lfs.core.utils.import_symbol(ADDRESS_MODEL)
    customer.default_invoice_address = address_model.objects.create(customer=customer, country=shop.default_country)
    customer.default_shipping_address = address_model.objects.create(customer=customer, country=shop.default_country)
    customer.selected_invoice_address = address_model.objects.create(customer=customer, country=shop.default_country)
    customer.selected_shipping_address = address_model.objects.create(customer=customer, country=shop.default_country)
    customer.save()

    customer.default_invoice_address.customer = customer
    customer.default_invoice_address.save()
    customer.default_shipping_address.customer = customer
    customer.default_shipping_address.save()

    customer.selected_invoice_address.customer = customer
    customer.selected_invoice_address.save()
    customer.selected_shipping_address.customer = customer
    customer.selected_shipping_address.save()

    return customer


def get_customer(request):
    """Returns the customer for the given request (which means for the current
    logged in user/or the session user).
    """
    try:
        return request.customer
    except AttributeError:
        customer = request.customer = _get_customer(request)
        return customer


def _get_customer(request):
    user = request.user
    if user.is_authenticated():
        try:
            return Customer.objects.get(user=user)
        except ObjectDoesNotExist:
            return None
    else:
        session_key = request.session.session_key
        try:
            return Customer.objects.get(session=session_key)
        except ObjectDoesNotExist:
            return None
        except MultipleObjectsReturned:
            customers = Customer.objects.filter(session=session_key, user__isnull=True)
            customer = customers[0]
            customers.exclude(pk=customer.pk).delete()
            return customer


def update_customer_after_login(request):
    """Updates the customer after login.

    1. If there is no session customer, nothing has to be done.
    2. If there is a session customer and no user customer we assign the session
       customer to the current user.
    3. If there is a session customer and a user customer we copy the session
       customer information to the user customer and delete the session customer
    """
    try:
        session_customer = Customer.objects.get(session=request.session.session_key)
        try:
            user_customer = Customer.objects.get(user=request.user)
        except ObjectDoesNotExist:
            session_customer.user = request.user
            session_customer.save()
        else:
            user_customer.selected_shipping_method = session_customer.selected_shipping_method
            user_customer.save()
            session_customer.delete()
    except ObjectDoesNotExist:
        pass


def create_unique_username(email):
    new_email = email[:30]
    cnt = 0
    while User.objects.filter(username=new_email).exists():
        cnt += 1
        new_email = '%s%.2d' % (new_email[:28], cnt)
    return new_email
