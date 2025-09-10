from django import forms
from django.forms import ModelForm, ChoiceField
from django.forms.utils import ErrorList
from django.forms.widgets import Select, HiddenInput
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field, Div

import lfs.core.utils
from lfs.catalog.models import Product
from lfs.catalog.models import Property
from lfs.catalog.models import PropertyOption
from lfs.catalog.settings import CHOICES
from lfs.catalog.settings import CHOICES_YES
from lfs.catalog.settings import CATEGORY_VARIANT_CHOICES
from lfs.catalog.settings import PRODUCT_TEMPLATES
from lfs.catalog.settings import PRODUCT_TYPE_FORM_CHOICES
from lfs.core.widgets.checkbox import LFSCheckboxInput
from lfs.utils.widgets import SelectImage


class PropertyOptionForm(ModelForm):
    """Form to add/edit property options."""

    class Meta:
        model = PropertyOption
        fields = ("name",)


class PropertyForm(ModelForm):
    """Form to add/edit properties."""

    class Meta:
        model = Property
        fields = ("name",)


class ProductVariantSimpleForm(ModelForm):
    """Variants add form."""

    def __init__(self, all_properties, *args, **kwargs):
        super(ProductVariantSimpleForm, self).__init__(*args, **kwargs)
        self.fields["slug"].required = False
        for prop_dict in all_properties:
            prop = prop_dict["property"]
            property_group = prop_dict["property_group"]
            property_group_id = property_group.pk if property_group else 0
            property_group_name = property_group.name if property_group else _("Local")
            field_label = '<span class="property-group-label">[%s]</span> %s' % (property_group_name, prop.name)
            choices = [("all", _("All")), ("", "---")]
            choices.extend(list(prop.options.values_list("pk", "name")))
            self.fields["property_%s_%s" % (property_group_id, prop.id)] = ChoiceField(
                label=field_label, choices=choices, required=False
            )
            self.initial["property_%s_%s" % (property_group_id, prop.id)] = "all"

    class Meta:
        model = Product
        fields = (
            "slug",
            "name",
            "price",
        )


class ProductVariantCreateForm(ModelForm):
    """Form used to create product variant for specific set of options"""

    def __init__(self, options=None, product=None, *args, **kwargs):
        super(ProductVariantCreateForm, self).__init__(*args, **kwargs)
        self.fields["slug"].required = False
        self.options = options
        self.product = product

    def prepare_slug(self, slug):
        for option in self.options:
            property_group_id, property_id, option_id = option.split("|")
            o = PropertyOption.objects.get(pk=option_id)
            if slug:
                slug += "-"
            slug += slugify(o.name)

        product_slug = self.product.slug
        if product_slug is None:
            product_slug = ""
        if product_slug + slug.replace("-", "") == "":
            slug = ""
        else:
            slug = "%s-%s" % (product_slug, slug)
            slug = slug.rstrip("-")

        # create unique slug
        slug = slug[:80]
        new_slug = slug
        counter = 1
        while Product.objects.filter(slug=new_slug).exists():
            new_slug = "%s-%s" % (slug[: (79 - len(str(counter)))], counter)
            counter += 1
        slug = new_slug

        return slug

    def clean(self):
        cleaned_data = super(ProductVariantCreateForm, self).clean()
        slug = self.prepare_slug(cleaned_data.get("slug", ""))
        cleaned_data["slug"] = slug

        return cleaned_data

    class Meta:
        model = Product
        fields = (
            "slug",
            "name",
            "price",
        )


class CategoryVariantForm(ModelForm):
    """ """

    def __init__(self, *args, **kwargs):
        super(CategoryVariantForm, self).__init__(*args, **kwargs)
        product = kwargs.get("instance")

        choices = []
        for cv in CATEGORY_VARIANT_CHOICES:
            choices.append(cv)

        for variant in Product.objects.filter(parent=product):
            choices.append([variant.id, "%s (%s)" % (variant.get_name(), variant.variant_position)])

        self.fields["category_variant"].widget = Select(choices=choices)

    class Meta:
        model = Product
        fields = ("category_variant",)


class DisplayTypeForm(ModelForm):
    """Form to add/edit product's sub types."""

    class Meta:
        model = Product
        fields = ("variants_display_type",)


class DefaultVariantForm(ModelForm):
    """Form to edit the default variant."""

    def __init__(self, *args, **kwargs):
        super(DefaultVariantForm, self).__init__(*args, **kwargs)
        instance = kwargs.get("instance")

        choices = [("", "------")]
        choices.extend([(v.id, "%s (%s)" % (v.get_name(), v.variant_position)) for v in instance.variants.all()])

        self.fields["default_variant"].choices = choices

    class Meta:
        model = Product
        fields = ("default_variant",)


class ProductAddForm(forms.ModelForm):
    """
    Form to add a new product.
    """

    class Meta:
        model = Product
        fields = ("name", "slug")


class ProductSubTypeForm(forms.ModelForm):
    """
    Form to change the sub type.
    """

    class Meta:
        model = Product
        fields = ("sub_type",)

    def __init__(self, *args, **kwargs):
        super(ProductSubTypeForm, self).__init__(*args, **kwargs)
        self.fields["sub_type"].choices = PRODUCT_TYPE_FORM_CHOICES


class ProductDataForm(forms.ModelForm):
    """
    Form to add and edit master data of a product.
    """

    class Meta:
        model = Product
        fields = (
            "active",
            "name",
            "slug",
            "manufacturer",
            "sku",
            "sku_manufacturer",
            "price",
            "tax",
            "price_calculator",
            "short_description",
            "description",
            "for_sale",
            "for_sale_price",
            "static_block",
            "template",
            "active_price_calculation",
            "price_calculation",
            "price_unit",
            "unit",
            "type_of_quantity_field",
            "active_base_price",
            "base_price_unit",
            "base_price_amount",
        )

    active_base_price = forms.IntegerField(required=False)

    def __init__(self, *args, **kwargs):
        super(ProductDataForm, self).__init__(*args, **kwargs)

        choices = [(ord, d["name"]) for (ord, d) in enumerate(PRODUCT_TEMPLATES)]
        self.fields["template"].widget = SelectImage(choices=choices)
        self.fields["active_base_price"].widget = LFSCheckboxInput(check_test=lambda v: v != 0)

        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            if hasattr(field.widget, "attrs"):
                widget_class = field.widget.__class__.__name__
                if widget_class in [
                    "TextInput",
                    "EmailInput",
                    "URLInput",
                    "NumberInput",
                    "Textarea",
                    "DateInput",
                    "DateTimeInput",
                ]:
                    field.widget.attrs["class"] = field.widget.attrs.get("class", "") + " form-control"
                elif widget_class in ["Select"]:
                    field.widget.attrs["class"] = field.widget.attrs.get("class", "") + " form-select"
                elif widget_class in ["CheckboxInput", "LFSCheckboxInput"]:
                    field.widget.attrs["class"] = field.widget.attrs.get("class", "") + " form-check-input"

    def clean(self):
        super(ProductDataForm, self).clean()
        if self.instance:
            redirect_to = self.data.get("redirect_to", "")
            if redirect_to != "":
                lfs.core.utils.set_redirect_for(self.instance.get_absolute_url(), redirect_to)
            else:
                lfs.core.utils.remove_redirect_for(self.instance.get_absolute_url())

        if self.data.get("active_base_price", 0):
            if self.data.get("base_price_amount", "") == "":
                self.errors["base_price_amount"] = ErrorList([_("This field is required.")])

        return self.cleaned_data


class VariantDataForm(forms.ModelForm):
    """
    Form to add and edit master data of a variant.
    """

    class Meta:
        model = Product
        fields = (
            "active",
            "active_name",
            "name",
            "slug",
            "manufacturer",
            "active_sku",
            "sku",
            "sku_manufacturer",
            "active_price",
            "price",
            "price_calculator",
            "active_short_description",
            "short_description",
            "active_description",
            "description",
            "for_sale_price",
            "active_for_sale",
            "active_for_sale_price",
            "active_related_products",
            "active_static_block",
            "static_block",
            "template",
            "active_base_price",
            "base_price_unit",
            "base_price_amount",
        )

    active_base_price = forms.IntegerField(required=False)

    def __init__(self, *args, **kwargs):
        super(VariantDataForm, self).__init__(*args, **kwargs)
        self.fields["active_base_price"].widget = Select(choices=CHOICES)
        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            if hasattr(field.widget, "attrs"):
                widget_class = field.widget.__class__.__name__
                if widget_class in [
                    "TextInput",
                    "EmailInput",
                    "URLInput",
                    "NumberInput",
                    "Textarea",
                    "DateInput",
                    "DateTimeInput",
                ]:
                    field.widget.attrs["class"] = field.widget.attrs.get("class", "") + " form-control"
                elif widget_class in ["Select"]:
                    field.widget.attrs["class"] = field.widget.attrs.get("class", "") + " form-select"
                elif widget_class in ["CheckboxInput"]:
                    field.widget.attrs["class"] = field.widget.attrs.get("class", "") + " form-check-input"
        choices = [(ord, d["name"]) for (ord, d) in enumerate(PRODUCT_TEMPLATES)]

    def clean(self):
        if self.instance:
            redirect_to = self.data.get("redirect_to", "")
            if redirect_to != "":
                lfs.core.utils.set_redirect_for(self.instance.get_absolute_url(), redirect_to)
            else:
                lfs.core.utils.remove_redirect_for(self.instance.get_absolute_url())

        if self.data.get("active_base_price") == str(CHOICES_YES):
            if self.data.get("base_price_amount", "") == "":
                self.errors["base_price_amount"] = ErrorList([_("This field is required.")])

        return self.cleaned_data


class PaginationDataForm(forms.Form):
    page = forms.IntegerField(label=_("Page"), widget=HiddenInput)


class ProductStockForm(forms.ModelForm):
    """
    Form to add and edit stock data of a product.
    """

    def __init__(self, *args, **kwargs):
        super(ProductStockForm, self).__init__(*args, **kwargs)

        if kwargs.get("instance").is_variant():
            self.fields["active_packing_unit"].widget = Select(choices=CHOICES)
        else:
            self.fields["active_packing_unit"].widget = LFSCheckboxInput(check_test=lambda v: v != 0)

        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            if hasattr(field.widget, "attrs"):
                widget_class = field.widget.__class__.__name__
                if widget_class in [
                    "TextInput",
                    "EmailInput",
                    "URLInput",
                    "NumberInput",
                    "Textarea",
                    "DateInput",
                    "DateTimeInput",
                ]:
                    field.widget.attrs["class"] = field.widget.attrs.get("class", "") + " form-control"
                elif widget_class in ["Select"]:
                    field.widget.attrs["class"] = field.widget.attrs.get("class", "") + " form-select"
                elif widget_class in ["CheckboxInput", "LFSCheckboxInput"]:
                    field.widget.attrs["class"] = field.widget.attrs.get("class", "") + " form-check-input"

    class Meta:
        model = Product
        fields = (
            "weight",
            "width",
            "height",
            "length",
            "manage_stock_amount",
            "stock_amount",
            "manual_delivery_time",
            "delivery_time",
            "deliverable",
            "order_time",
            "ordered_at",
            "active_dimensions",
            "packing_unit",
            "packing_unit_unit",
            "active_packing_unit",
        )


class SEOForm(ModelForm):
    """Form to add/edit seo properties of a product."""

    def __init__(self, *args, **kwargs):
        super(SEOForm, self).__init__(*args, **kwargs)

        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            if hasattr(field.widget, "attrs"):
                widget_class = field.widget.__class__.__name__
                if widget_class in [
                    "TextInput",
                    "EmailInput",
                    "URLInput",
                    "NumberInput",
                    "Textarea",
                    "DateInput",
                    "DateTimeInput",
                ]:
                    field.widget.attrs["class"] = field.widget.attrs.get("class", "") + " form-control"
                elif widget_class in ["Select"]:
                    field.widget.attrs["class"] = field.widget.attrs.get("class", "") + " form-select"
                elif widget_class in ["CheckboxInput", "LFSCheckboxInput"]:
                    field.widget.attrs["class"] = field.widget.attrs.get("class", "") + " form-check-input"

        # Crispy forms helper for SEO data
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_tag = False  # Don't render form tag, template handles it
        self.helper.layout = Layout(
            Fieldset(
                _("Meta Title"),
                Div(
                    Field("active_meta_title", wrapper_class="col-md-2"),
                    Field("meta_title", wrapper_class="col-md-10"),
                    css_class="row",
                ),
                css_class="mb-4 border border-dark rounded-2 px-3 py-1",
            ),
            Fieldset(
                _("Meta Keywords"),
                Div(
                    Field("active_meta_keywords", wrapper_class="col-md-2"),
                    Field("meta_keywords", wrapper_class="col-md-10"),
                    css_class="row",
                ),
                css_class="mb-4 border border-dark rounded-2 px-3 py-1",
            ),
            Fieldset(
                _("Meta Description"),
                Div(
                    Field("active_meta_description", wrapper_class="col-md-2"),
                    Field("meta_description", wrapper_class="col-md-10"),
                    css_class="row",
                ),
                css_class="mb-4 border border-dark rounded-2 px-3 py-1",
            ),
        )

    class Meta:
        model = Product
        fields = (
            "active_meta_title",
            "meta_title",
            "active_meta_keywords",
            "meta_keywords",
            "active_meta_description",
            "meta_description",
        )
