from django.conf import settings

ADDRESS_MODEL = getattr(settings, "LFS_ADDRESS_MODEL", "lfs.addresses.models.Address")
SHIPPING_ADDRESS_FORM = getattr(settings, "LFS_SHIPPING_ADDRESS_FORM", "lfs.addresses.forms.ShippingAddressForm")
INVOICE_ADDRESS_FORM = getattr(settings, "LFS_INVOICE_ADDRESS_FORM", "lfs.addresses.forms.InvoiceAddressForm")

INVOICE_COMPANY_NAME_REQUIRED = getattr(settings, "LFS_INVOICE_COMPANY_NAME_REQUIRED", False)
INVOICE_EMAIL_REQUIRED = getattr(settings, "LFS_INVOICE_EMAIL_REQUIRED", True)
INVOICE_PHONE_REQUIRED = getattr(settings, "LFS_INVOICE_PHONE_REQUIRED", True)

SHIPPING_COMPANY_NAME_REQUIRED = getattr(settings, "LFS_SHIPPING_COMPANY_NAME_REQUIRED", False)
SHIPPING_EMAIL_REQUIRED = getattr(settings, "LFS_SHIPPING_EMAIL_REQUIRED", False)
SHIPPING_PHONE_REQUIRED = getattr(settings, "LFS_SHIPPING_PHONE_REQUIRED", False)

AUTO_UPDATE_DEFAULT_ADDRESSES = getattr(settings, "LFS_AUTO_UPDATE_DEFAULT_ADDRESSES", True)
CHECKOUT_NOT_REQUIRED_ADDRESS = getattr(settings, "LFS_CHECKOUT_NOT_REQUIRED_ADDRESS", 'shipping')
