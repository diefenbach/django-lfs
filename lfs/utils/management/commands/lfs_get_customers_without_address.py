# django imports
from django.core.management.base import BaseCommand

import lfs.core.utils
from lfs.addresses.settings import ADDRESS_MODEL
from lfs.core.models import Shop
from lfs.customer.models import Customer


class Command(BaseCommand):
    args = ""

    def handle(self, *args, **options):
        address_model = lfs.core.utils.import_symbol(ADDRESS_MODEL)
        shop = Shop.objects.all()[0]

        for i, customer in enumerate(Customer.objects.filter(id=1)):
            if not customer.selected_invoice_address:
                customer.default_invoice_address = address_model.objects.create(
                    customer=customer, country=shop.default_country
                )
                customer.selected_invoice_address = address_model.objects.create(
                    customer=customer, country=shop.default_country
                )

                customer.save()

                customer.selected_invoice_address.customer = customer
                customer.selected_invoice_address.save()

                customer.default_invoice_address.customer = customer
                customer.default_invoice_address.save()

            if not customer.selected_shipping_address:
                customer.default_shipping_address = address_model.objects.create(
                    customer=customer, country=shop.default_country
                )
                customer.selected_shipping_address = address_model.objects.create(
                    customer=customer, country=shop.default_country
                )

                customer.save()

                customer.default_shipping_address.customer = customer
                customer.default_shipping_address.save()

                customer.selected_shipping_address.customer = customer
                customer.selected_shipping_address.save()

            if i % 1000 == 0:
                print(i)
