from copy import deepcopy

from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse

import lfs
from lfs.addresses.utils import AddressManagement
from lfs.checkout.settings import CHECKOUT_TYPE_AUTH, ONE_PAGE_CHECKOUT_FORM
from lfs.checkout.views import cart_inline, payment_inline, shipping_inline, voucher_inline
from lfs.voucher.models import Voucher
from lfs.voucher.utils import set_current_voucher_number


def copy_address(address):
    """
    Copy an address object and return a new object with the same data.
    """
    shipping_address = deepcopy(address)
    shipping_address.id = None
    shipping_address.pk = None
    shipping_address.save()
    return shipping_address


def addresses(request, template_name="lfs/checkout/new_addresses.html"):
    """
    This is the first page of the checkout process, where the customer has to enter his invoice and shipping address.
    """
    customer = lfs.customer.utils.get_or_create_customer(request)
    invoice_address = customer.selected_invoice_address
    shipping_address = customer.selected_shipping_address
    shop = lfs.core.utils.get_default_shop(request)

    initial_address = {}

    if request.user.is_anonymous:
        if shop.checkout_type == CHECKOUT_TYPE_AUTH:
            return HttpResponseRedirect(reverse("lfs_checkout_login"))
    else:
        initial_address["email"] = request.user.email

    if request.method == "POST":
        iam = AddressManagement(customer, invoice_address, "invoice", request.POST, initial=initial_address)

        if request.POST.get("no_shipping", "") == "on":
            sam = AddressManagement(customer, shipping_address, "shipping", request.POST, initial=initial_address)
            if iam.is_valid() and sam.is_valid():
                iam.save()
                sam.save()
                customer.selected_invoice_address = iam.address
                customer.selected_shipping_address = sam.address
                customer.save()
                return HttpResponseRedirect(reverse("lfs_checkout_payment_and_shipping"))
        else:
            sam = AddressManagement(customer, shipping_address, "shipping", initial=initial_address)
            if iam.is_valid():
                iam.save()
                customer.selected_invoice_address = iam.address
                customer.selected_shipping_address = copy_address(iam.address)
                customer.save()
                return HttpResponseRedirect(reverse("lfs_checkout_payment_and_shipping"))

    else:
        cart = lfs.cart.utils.get_cart(request)
        if cart is None:
            return HttpResponseRedirect(reverse("lfs_cart"))

        if request.user.is_anonymous:
            if shop.checkout_type == CHECKOUT_TYPE_AUTH:
                return HttpResponseRedirect(reverse("lfs_checkout_login"))
        else:
            initial_address["email"] = request.user.email

        customer = lfs.customer.utils.get_or_create_customer(request)

        invoice_address = customer.selected_invoice_address
        shipping_address = customer.selected_shipping_address

        iam = AddressManagement(customer, invoice_address, "invoice", initial=initial_address)
        sam = AddressManagement(customer, shipping_address, "shipping", initial=initial_address)

    return render(
        request,
        template_name,
        {
            "invoice_address_inline": iam.render(request),
            "shipping_address_inline": sam.render(request),
            "no_shipping": request.POST.get("no_shipping", "") == "on",
        },
    )


def payment_and_delivery(request, template_name="lfs/checkout/new_payment_and_shipping.html"):
    """ """
    if request.method == "POST":
        return HttpResponseRedirect(reverse("lfs_checkout_check_and_pay"))
    else:
        return render(
            request,
            template_name,
            {
                "shipping_inline": shipping_inline(request),
                "payment_inline": payment_inline(request, form=None),
            },
        )


def check_and_pay(request, template_name="lfs/checkout/new_check_and_pay.html"):
    """ """
    customer = lfs.customer.utils.get_or_create_customer(request)
    invoice_address = customer.selected_invoice_address
    shipping_address = customer.selected_shipping_address
    CheckoutFormClass = lfs.core.utils.import_symbol(ONE_PAGE_CHECKOUT_FORM)

    if request.method == "POST":
        checkout_form = CheckoutFormClass(request.POST)
        if checkout_form.is_valid():
            return lfs.payment.utils.process_payment(request)
    else:
        checkout_form = CheckoutFormClass()

    return render(
        request,
        template_name,
        {
            "invoice_address": invoice_address,
            "shipping_address": shipping_address,
            "cart": lfs.cart.utils.get_cart(request),
            "customer": customer,
            "payment_method": customer.selected_payment_method,
            "shipping_method": customer.selected_shipping_method,
            "cart_inline": cart_inline(request),
            "voucher_inline": voucher_inline(request),
            "checkout_form": checkout_form,
        },
    )


def set_voucher(request):
    """ """
    voucher_number = request.POST.get("voucher")
    cart = lfs.cart.utils.get_cart(request)

    try:
        voucher = Voucher.objects.get(number=voucher_number)
    except Voucher.DoesNotExist:
        is_valid_voucher = False
        message = "Dieser Gutschein ist nicht gültig."
    else:
        is_valid_voucher, message = voucher.is_effective(request, cart)

    if is_valid_voucher:
        set_current_voucher_number(request, voucher_number)
        message = "Ihr Gutschein wurde erfolgreich eingelöst."

    return JsonResponse(
        {
            "cart": cart_inline(request),
            "voucher_inline": voucher_inline(request),
            "is_valid_voucher": is_valid_voucher,
            "message": message,
        }
    )


def delete_voucher(request):
    """ """
    set_current_voucher_number(request, "")

    return JsonResponse(
        {
            "cart": cart_inline(request),
            "voucher_inline": voucher_inline(request),
        }
    )
