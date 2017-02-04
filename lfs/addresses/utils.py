# django imports
from django.template.loader import select_template
from django.template import RequestContext

# lfs imports
import lfs.core.utils
from lfs.addresses.settings import INVOICE_ADDRESS_FORM, SHIPPING_ADDRESS_FORM, CHECKOUT_NOT_REQUIRED_ADDRESS
from lfs.core.models import Country

# django-postal imports
from postal.library import form_factory


class AddressManagement(object):
    """
    Wrapper to manage the postal and the additional address.

    **Attributes:**

    address
        The address, which is managed.

    data
        Data, which is passed to the forms. This is similar to Django's forms
        data parameter.

    initial
        Initial data, which is passed to the forms. This is similar to Django's
        forms initial parameter.

    type
        The type of the address. This is one of ``invoice`` or ``shipping``.
        Based on that different forms can be rendered.

    """
    def __init__(self, customer, address, type, data=None, initial=None):
        self.customer = customer
        self.address = address
        self.data = data
        self.type = type
        self.initial = initial or self.get_address_as_dict()

    def get_address_as_dict(self):
        """
        Returns the postal address as dictionary.
        """
        if self.address is None:
            return {}
        else:
            return {
                "line1": self.address.line1,
                "line2": self.address.line2,
                "city": self.address.city,
                "state": self.address.state,
                "code": self.address.zip_code,
                "country": self.address.country.code.upper(),
            }

    def get_form_model(self):
        """
        Returns the form for the address based on the type of the address.
        """
        if self.type == "invoice":
            return lfs.core.utils.import_symbol(INVOICE_ADDRESS_FORM)
        else:
            return lfs.core.utils.import_symbol(SHIPPING_ADDRESS_FORM)

    def get_countries(self, request):
        """
        Returns available countries for the address based on the type of the
        address.
        """
        shop = lfs.core.utils.get_default_shop(request)
        if self.type == "invoice":
            return shop.invoice_countries.all()
        else:
            return shop.shipping_countries.all()

    def render(self, request, country_iso=None):
        """
        Renders the postal and the additional address form.
        """
        if country_iso is None:
            country_iso = self.address.country.code.upper()

        form_model = form_factory(country_iso)
        postal_form = form_model(initial=self.get_address_as_dict(), data=self.data, prefix=self.type)

        countries = self.get_countries(request)
        postal_form.fields["country"].choices = [(c.code.upper(), c.name) for c in countries]

        address_form_model = self.get_form_model()
        address_form = address_form_model(instance=self.address, data=self.data, prefix=self.type, initial=self.initial)

        templates = ["lfs/addresses/address_form.html"]
        templates.insert(0, "lfs/addresses/%s_address_form.html" % self.type)
        template = select_template(templates)
        return template.render(RequestContext(request, {
            "postal_form": postal_form,
            "address_form": address_form,
        }))

    def is_valid(self):
        """
        Returns True if the postal and the additional form is valid.
        """
        if self.type == CHECKOUT_NOT_REQUIRED_ADDRESS and self.data.get("no_%s" % CHECKOUT_NOT_REQUIRED_ADDRESS):
            return True

        if self.data:
            form_model = form_factory(self.data.get("%s-country" % self.type, self.address.country.code.upper()))
        else:
            form_model = form_factory(self.address.country.code.upper())
        postal_form = form_model(data=self.data, initial=self.get_address_as_dict(), prefix=self.type)

        address_form_model = self.get_form_model()
        address_form = address_form_model(data=self.data, instance=self.address, prefix=self.type)

        return postal_form.is_valid() and address_form.is_valid()

    def save(self):
        """
        Saves the postal and the additional form.
        """
        if self.type == CHECKOUT_NOT_REQUIRED_ADDRESS and self.data.get("no_%s" % CHECKOUT_NOT_REQUIRED_ADDRESS):
            return
        else:
            self.address.line1 = self.data.get("%s-line1" % self.type)
            self.address.line2 = self.data.get("%s-line2" % self.type)
            self.address.city = self.data.get("%s-city" % self.type)
            self.address.state = self.data.get("%s-state" % self.type)
            self.address.zip_code = self.data.get("%s-code" % self.type)

            try:
                country = Country.objects.get(code__iexact=self.data.get("%s-country" % self.type))
                self.address.country = country
            except Country.DoesNotExist:
                pass

            self.address.customer = self.customer
            self.address.save()

            address_form_model = self.get_form_model()
            address_form = address_form_model(data=self.data, instance=self.address, initial=self.initial,
                                              prefix=self.type)
            address_form.save()
