from django.core.management.base import BaseCommand


class Command(BaseCommand):
    args = ""

    def handle(self, *args, **options):
        """ """
        from lfs.customer.models import Customer

        for customer in Customer.objects.all():
            print(customer.id)
            if customer.selected_shipping_address is None:
                print("\tssa")
                if customer.selected_invoice_address is not None:
                    customer.selected_shipping_address = customer.selected_invoice_address
                elif customer.default_invoice_address is not None:
                    customer.selected_shipping_address = customer.default_invoice_address
                elif customer.default_shipping_address is not None:
                    customer.selected_shipping_address = customer.default_shipping_address

            if customer.selected_invoice_address is None:
                print("\tsia")
                if customer.selected_shipping_address is not None:
                    customer.selected_invoice_address = customer.selected_shipping_address
                elif customer.default_invoice_address is not None:
                    customer.selected_invoice_address = customer.default_invoice_address
                elif customer.default_shipping_address is not None:
                    customer.selected_invoice_address = customer.default_shipping_address

            if customer.default_invoice_address is None:
                print("\tdia")
                if customer.selected_invoice_address is not None:
                    customer.default_invoice_address = customer.selected_invoice_address
                elif customer.selected_shipping_address is not None:
                    customer.default_invoice_address = customer.selected_shipping_address
                elif customer.default_shipping_address is not None:
                    customer.default_invoice_address = customer.default_shipping_address

            if customer.default_shipping_address is None:
                print("\tsia")
                if customer.selected_shipping_address is not None:
                    customer.default_shipping_address = customer.selected_shipping_address
                elif customer.selected_invoice_address is not None:
                    customer.default_shipping_address = customer.selected_invoice_address
                elif customer.default_invoice_address is not None:
                    customer.default_shipping_address = customer.default_invoice_address

            customer.save()

        # from lfs.customer.models import Customer
        # for customer in Customer.objects.all():
        #     fs = False
        #     fi = False
        #     print customer.id
        #     if not customer.default_invoice_address:
        #         customer.default_invoice_address = customer.selected_invoice_address
        #         fi = True
        #     if not customer.default_shipping_address:
        #         customer.default_shipping_address = customer.selected_shipping_address
        #         fs = True

        #     if fs or fi:
        #         print "found", fi, fs
        #         customer.save()
