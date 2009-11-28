# lfs imports
from lfs.core.signals import customer_added
from lfs.core.signals import order_submitted
from lfs.mail import utils as mail_utils

# reviews imports
from reviews.signals import review_added

def order_submitted_listener(sender, **kwargs):
    """Listen to order submitted signal
    """
    order = sender.get("order")
    mail_utils.send_order_received_mail(order)
order_submitted.connect(order_submitted_listener)

def customer_added_listener(sender, **kwargs):
    """Listens to customer added signal.
    """
    mail_utils.send_customer_added(sender)
customer_added.connect(customer_added_listener)

def review_added_listener(sender, **kwargs):
    """Listens to review added signal
    """
    mail_utils.send_review_added(sender)
review_added.connect(review_added_listener)