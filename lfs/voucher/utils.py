# python imports
import random

# lfs imports
from .models import VoucherOptions
from .settings import MESSAGES


def create_voucher_number():
    """
    """
    try:
        options = VoucherOptions.objects.all()[0]
    except IndexError:
        letters = "ABCDEFGHIJKLMNOPQRSTUVXYZ"
        length = 5
        prefix = ""
        suffix = ""
    else:
        letters = options.number_letters
        length = options.number_length
        prefix = options.number_prefix
        suffix = options.number_suffix

    number = ""
    for i in range(0, length):
        number += random.choice(letters)

    return prefix + number + suffix


def get_current_voucher_number(request):
    """
    """
    return request.POST.get("voucher", request.session.get("voucher", ""))


def set_current_voucher_number(request, number):
    """
    """
    request.session["voucher"] = number


def get_voucher_data(request, cart):
    from .models import Voucher
    voucher_value = 0.0
    voucher_tax = 0.0
    sums_up = False
    voucher_number = get_current_voucher_number(request)
    try:
        voucher = Voucher.objects.get(number=voucher_number)
    except Voucher.DoesNotExist:
        voucher = None
        voucher_message = MESSAGES[6]
    else:
        set_current_voucher_number(request, voucher_number)
        is_voucher_effective, voucher_message = voucher.is_effective(request, cart)
        if is_voucher_effective:
            voucher_number = voucher.number
            voucher_value = voucher.get_price_gross(request, cart)
            voucher_tax = voucher.get_tax(request, cart)
            sums_up = voucher.sums_up
        else:
            voucher = None

    return {'voucher': voucher,
            'voucher_value': voucher_value,
            'voucher_tax': voucher_tax,
            'sums_up': sums_up,
            'voucher_number': voucher_number,
            'voucher_message': voucher_message}
