from django.contrib.auth.signals import user_logged_in

from lfs.cart import utils as cart_utils
from lfs.customer import utils as customer_utils


def update_user(sender, user, request, **kwargs):
    cart_utils.update_cart_after_login(request)
    customer_utils.update_customer_after_login(request)

user_logged_in.connect(update_user)
