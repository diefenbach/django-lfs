# django imports
from django.core.exceptions import ObjectDoesNotExist

# lfs imports
from lfs.customer.models import Customer, Address
import lfs.core.utils


def get_or_create_customer(request):
    """Get or creates the customer object.
    """
    customer = get_customer(request)
    if customer is None:
        customer = create_customer(request)

    return customer


def create_customer(request):
    """Creates a customer for the given request (which means for the current
    logged in user/or the session user).

    This shouldn't be called directly. Instead get_or_create_customer should be
    called.
    """
    customer = Customer(session=request.session.session_key)
    if request.user.is_authenticated():
        customer.user = request.user
    shop = lfs.core.utils.get_default_shop()
    customer.selected_invoice_address = Address.objects.create(customer=customer, country=shop.default_country)
    customer.selected_shipping_address = Address.objects.create(customer=customer, country=shop.default_country)
    customer.save()
    return customer


def get_customer(request):
    """Returns the customer for the given request (which means for the current
    logged in user/or the session user).
    """
    session_key = request.session.session_key
    user = request.user

    if user.is_authenticated():
        try:
            return Customer.objects.get(user=user)
        except ObjectDoesNotExist:
            return None
    else:
        try:
            return Customer.objects.get(session=session_key)
        except ObjectDoesNotExist:
            return None


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
