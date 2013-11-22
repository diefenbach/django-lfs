# django imports
from django import forms

# lfs imports
from lfs.addresses.models import Address
from lfs.addresses import settings


class AddressBaseForm(forms.ModelForm):
    """
    Base class for all address forms.

    **Attributes:**

    fields_before_postal
        List of field names which are supposed to be displayed before the postal
        form fields.

    fields_before_postal
        List of field names which are supposed to be displayed after the postal
        form fields.
    """
    fields_before_postal = None
    fields_after_postal = None

    class Meta:
        exclude = ("customer", "order", "line1", "line2", "zip_code", "city", "state", "country")

    def get_fields_before_postal(self):
        """
        Returns the fields which are supposed to be displayed before the postal
        form fields.
        """
        if self.fields_before_postal is None:
            return []

        fields = []
        for field in self.fields_before_postal:
            try:
                fields.append(self[field])
            except KeyError:
                continue
        return fields

    def get_fields_after_postal(self):
        """
        Returns the fields which are supposed to be displayed before the postal
        form fields.
        """
        fields = []
        for field in (self.fields_after_postal or self.fields):
            try:
                fields.append(self[field])
            except KeyError:
                continue
        return fields


class InvoiceAddressForm(AddressBaseForm):
    """
    Default form for LFS' invoice addresses.
    """
    fields_before_postal = ("firstname", "lastname", "company_name")
    fields_after_postal = ("phone", "email")

    class Meta(AddressBaseForm.Meta):
        model = Address

    def __init__(self, *args, **kwargs):
        super(InvoiceAddressForm, self).__init__(*args, **kwargs)
        self.fields["company_name"].required = settings.INVOICE_COMPANY_NAME_REQUIRED
        self.fields["phone"].required = settings.INVOICE_PHONE_REQUIRED
        self.fields["email"].required = settings.INVOICE_EMAIL_REQUIRED


class ShippingAddressForm(InvoiceAddressForm):
    """
    Default form for LFS' shipping addresses.
    """
    def __init__(self, *args, **kwargs):
        super(ShippingAddressForm, self).__init__(*args, **kwargs)
        self.fields["company_name"].required = settings.SHIPPING_COMPANY_NAME_REQUIRED
        self.fields["phone"].required = settings.SHIPPING_PHONE_REQUIRED
        self.fields["email"].required = settings.SHIPPING_EMAIL_REQUIRED
