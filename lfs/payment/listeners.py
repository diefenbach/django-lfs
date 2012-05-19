# django imports
from django.conf import settings

# lfs imports
from lfs.order.models import Order
from lfs.order.settings import PAID, PAYMENT_FAILED, PAYMENT_FLAGGED
from lfs.mail import utils as mail_utils
from models import PayPalOrderTransaction

# other imports
import logging
from paypal.standard.ipn.signals import payment_was_successful, payment_was_flagged
from paypal.standard.pdt.signals import pdt_failed, pdt_successful
from paypal.standard.models import ST_PP_COMPLETED


def mark_payment(pp_obj, order_state=PAID):
    order = None
    try:
        logging.info("getting order for uuid %s" % pp_obj.custom)
        order_uuid = pp_obj.custom
        order = Order.objects.get(uuid=order_uuid)
        if order is not None:
            if order.state != PAID and order_state == PAID:
                if getattr(settings, 'LFS_SEND_ORDER_MAIL_ON_PAYMENT', False):
                    mail_utils.send_order_received_mail(order)
            order.state = order_state
            order.save()
    except Order.DoesNotExist, e:
        logging.error(e)
    return order


def successful_payment(sender, **kwargs):
    logging.info("successful ipn payment")
    ipn_obj = sender
    order = mark_payment(ipn_obj, PAID)
    if order is not None:
        transaction, created = PayPalOrderTransaction.objects.get_or_create(order=order)
        transaction.ipn.add(ipn_obj)
        transaction.save()
    else:
        logging.warning("successful ipn payment, no order found for uuid %s" % ipn_obj.custom)


def unsuccessful_payment(sender, **kwargs):
    logging.info("unsuccessful ipn payment")
    ipn_obj = sender
    if ipn_obj:
        order = None
        if ipn_obj.payment_status == ST_PP_COMPLETED:
            order = mark_payment(ipn_obj, PAYMENT_FLAGGED)
        else:
            order = mark_payment(ipn_obj, PAYMENT_FAILED)
        if order is not None:
            transaction, created = PayPalOrderTransaction.objects.get_or_create(order=order)
            transaction.ipn.add(ipn_obj)
            transaction.save()
        else:
            logging.warning("unsuccessful ipn payment, no order found for uuid %s" % ipn_obj.custom)
    else:
        logging.warning("unsuccessful ipn payment signal with no ipn object")


def successful_pdt(sender, **kwargs):
    logging.info("successful pdt payment")
    pdt_obj = sender
    order = mark_payment(pdt_obj, True)


def unsuccesful_pdt(sender, **kwargs):
    logging.info("unsuccessful pdt payment")
    pdt_obj = sender
    order = mark_payment(pdt_obj, False)


payment_was_successful.connect(successful_payment, dispatch_uid="Order.ipn_successful")
payment_was_flagged.connect(unsuccessful_payment, dispatch_uid="Order.ipn_unsuccessful")
pdt_successful.connect(successful_pdt, dispatch_uid="Order.pdt_successful")
pdt_failed.connect(unsuccesful_pdt, dispatch_uid="Order.pdt_unsuccessful")
