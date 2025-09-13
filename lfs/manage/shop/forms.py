from django import forms
from django.forms import ClearableFileInput
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset

from lfs.core.models import Shop


class ShopDataForm(forms.ModelForm):
    """Form to edit shop data."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["image"].widget = ClearableFileInput()
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                _("General"),
                "name",
                "shop_owner",
            ),
            Fieldset(
                _("E-Mails"),
                "from_email",
                "notification_emails",
            ),
            Fieldset(
                _("Checkout"),
                "checkout_type",
                "confirm_toc",
            ),
            Fieldset(
                _("Google"),
                "google_analytics_id",
                "ga_site_tracking",
                "ga_ecommerce_tracking",
            ),
            Fieldset(
                _("Content"),
                "description",
                "image",
                "static_block",
            ),
        )

    class Meta:
        model = Shop
        fields = (
            "name",
            "shop_owner",
            "from_email",
            "notification_emails",
            "description",
            "image",
            "static_block",
            "checkout_type",
            "confirm_toc",
            "google_analytics_id",
            "ga_site_tracking",
            "ga_ecommerce_tracking",
        )


class ShopDefaultValuesForm(forms.ModelForm):
    """Form to edit shop default values."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                _("Price Calculator"),
                "price_calculator",
            ),
            Fieldset(
                _("Delivery Time"),
                "delivery_time",
            ),
            Fieldset(
                _("Countries"),
                "default_country",
                "invoice_countries",
                "shipping_countries",
            ),
        )

    class Meta:
        model = Shop
        fields = (
            "price_calculator",
            "default_country",
            "invoice_countries",
            "shipping_countries",
            "delivery_time",
        )
