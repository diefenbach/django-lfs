import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY, REDIRECT_FIELD_NAME
from django.contrib import auth

# TODO: Check whether signals can be used here.
from lfs.cart import utils as cart_utils
from lfs.customer import utils as customer_utils


def lfs_login(request, user):
    """
    Persist a user id and a backend in the request. This way a user doesn't
    have to reauthenticate on every request.
    """
    if user is None:
        user = request.user
    # TODO: It would be nice to support different login methods, like signed cookies.
    user.last_login = datetime.datetime.now()
    user.save()

    if SESSION_KEY in request.session:
        if request.session[SESSION_KEY] != user.id:
            # To avoid reusing another user's session, create a new, empty
            # session if the existing session corresponds to a different
            # authenticated user.
            request.session.flush()
    else:
        pass
        # request.session.cycle_key()
    request.session[SESSION_KEY] = user.id
    request.session[BACKEND_SESSION_KEY] = user.backend
    if hasattr(request, 'user'):
        request.user = user

    ### LFS stuff
    cart_utils.update_cart_after_login(request)
    customer_utils.update_customer_after_login(request)

auth.login = lfs_login
