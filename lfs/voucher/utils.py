# python imports
import random
import datetime

# lfs imports
from lfs.voucher.models import Voucher

def create_voucher_number():
    """
    """
    letters = "ABCDEFGHIJKLMNOPQRSTUVXYZ"

    number = ""
    for i in range(0, 20):
        number += random.choice(letters)

    return number