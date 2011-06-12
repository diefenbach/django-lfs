# python imports
import random

# lfs imports
from lfs.voucher.models import VoucherOptions


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
