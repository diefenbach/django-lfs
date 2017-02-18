from django.conf import settings
from django.dispatch import receiver

from lfs.core.signals import customer_added
from lfs.core.signals import order_submitted
from lfs.core.signals import order_sent
from lfs.core.signals import order_paid
from lfs.mail import utils as mail_utils

from reviews.signals import review_added


@receiver(order_paid)
def order_paid_listener(sender, **kwargs):
    """Listen to order payed signal.
    """
    order = sender
    mail_utils.send_order_paid_mail(order)


@receiver(order_sent)
def order_sent_listener(sender, **kwargs):
    """Listen to order payed signal.
    """
    order = sender
    mail_utils.send_order_sent_mail(order)


@receiver(order_submitted)
def order_submitted_listener(sender, **kwargs):
    """Listen to order submitted signal.
    """
    request = kwargs.get("request")

    if getattr(settings, 'LFS_SEND_ORDER_MAIL_ON_CHECKOUT', True):
        mail_utils.send_order_received_mail(request, sender)


@receiver(customer_added)
def customer_added_listener(sender, **kwargs):
    """Listens to customer added signal.
    """
    mail_utils.send_customer_added(sender)


@receiver(review_added)
def review_added_listener(sender, **kwargs):
    """Listens to review added signal
    """
    mail_utils.send_review_added(sender)
