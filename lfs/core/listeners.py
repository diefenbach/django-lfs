from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver


@receiver(user_logged_in)
def update_user(sender, user, request, **kwargs):
    pass
    # cart_utils.update_cart_after_login(request)
    # customer_utils.update_customer_after_login(request)
