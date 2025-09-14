"""
Form tests for CustomerTax management.

Tests form validation, saving behavior, and error handling.
CustomerTax views use Django's automatic ModelForm generation based on form_class.
"""

from django.forms import ModelForm

from lfs.customer_tax.models import CustomerTax


class TestCustomerTaxForm:
    """Test CustomerTax form behavior."""

    def test_form_initialization_with_customer_tax(self, customer_tax):
        """Should initialize form with customer tax data."""

        # Create form using Django's model form factory
        class CustomerTaxForm(ModelForm):
            class Meta:
                model = CustomerTax
                fields = ("rate", "description")

        form = CustomerTaxForm(instance=customer_tax)

        assert form.instance == customer_tax
        assert form.instance.rate == customer_tax.rate
        assert form.instance.description == customer_tax.description

    def test_valid_form_data(self):
        """Should accept valid form data."""

        class CustomerTaxForm(ModelForm):
            class Meta:
                model = CustomerTax
                fields = ("rate", "description")

        data = {
            "rate": 19.0,
            "description": "Standard VAT",
        }

        form = CustomerTaxForm(data=data)
        assert form.is_valid()

    def test_required_fields_validation(self):
        """Should require rate field but not description."""

        class CustomerTaxForm(ModelForm):
            class Meta:
                model = CustomerTax
                fields = ("rate", "description")

        # Test missing rate
        data = {"description": "Standard VAT"}
        form = CustomerTaxForm(data=data)
        assert not form.is_valid()
        assert "rate" in form.errors

        # Test missing description (should be valid since blank=True)
        data = {"rate": 19.0}
        form = CustomerTaxForm(data=data)
        assert form.is_valid()

    def test_rate_validation(self):
        """Should accept any rate value since model has no constraints."""

        class CustomerTaxForm(ModelForm):
            class Meta:
                model = CustomerTax
                fields = ("rate", "description")

        # Test negative rate (should be valid since no constraints)
        data = {"rate": -5.0, "description": "Negative Tax"}
        form = CustomerTaxForm(data=data)
        assert form.is_valid()

        # Test rate over 100% (should be valid since no constraints)
        data = {"rate": 150.0, "description": "High Tax"}
        form = CustomerTaxForm(data=data)
        assert form.is_valid()

    def test_valid_rate_values(self):
        """Should accept valid rate values."""

        class CustomerTaxForm(ModelForm):
            class Meta:
                model = CustomerTax
                fields = ("rate", "description")

        valid_rates = [0.0, 5.0, 19.0, 25.0, 100.0]

        for rate in valid_rates:
            data = {"rate": rate, "description": f"Tax {rate}%"}
            form = CustomerTaxForm(data=data)
            assert form.is_valid(), f"Rate {rate} should be valid"

    def test_description_accepts_long_text(self):
        """Should accept long descriptions since it's a TextField."""

        class CustomerTaxForm(ModelForm):
            class Meta:
                model = CustomerTax
                fields = ("rate", "description")

        # Create a very long description (TextField has no max_length)
        long_description = "A" * 1000
        data = {"rate": 19.0, "description": long_description}
        form = CustomerTaxForm(data=data)
        assert form.is_valid()

    def test_form_save_creates_customer_tax(self):
        """Should create new customer tax when saving form."""

        class CustomerTaxForm(ModelForm):
            class Meta:
                model = CustomerTax
                fields = ("rate", "description")

        data = {"rate": 7.0, "description": "Reduced VAT"}
        form = CustomerTaxForm(data=data)

        assert form.is_valid()
        customer_tax = form.save()

        assert customer_tax.rate == 7.0
        assert customer_tax.description == "Reduced VAT"
        assert CustomerTax.objects.filter(rate=7.0, description="Reduced VAT").exists()

    def test_form_save_updates_existing_customer_tax(self, customer_tax):
        """Should update existing customer tax when saving form."""

        class CustomerTaxForm(ModelForm):
            class Meta:
                model = CustomerTax
                fields = ("rate", "description")

        data = {"rate": 21.0, "description": "Updated VAT"}
        form = CustomerTaxForm(data=data, instance=customer_tax)

        assert form.is_valid()
        updated_customer_tax = form.save()

        assert updated_customer_tax == customer_tax
        assert updated_customer_tax.rate == 21.0
        assert updated_customer_tax.description == "Updated VAT"

    def test_form_fields_exist(self):
        """Should have correct form fields."""

        class CustomerTaxForm(ModelForm):
            class Meta:
                model = CustomerTax
                fields = ("rate", "description")

        form = CustomerTaxForm()
        assert "rate" in form.fields
        assert "description" in form.fields

    def test_form_field_types(self):
        """Should have correct field types."""

        class CustomerTaxForm(ModelForm):
            class Meta:
                model = CustomerTax
                fields = ("rate", "description")

        form = CustomerTaxForm()
        assert form.fields["rate"].__class__.__name__ == "FloatField"
        assert form.fields["description"].__class__.__name__ == "CharField"

    def test_form_clean_method_validation(self):
        """Should validate form data through clean methods."""

        class CustomerTaxForm(ModelForm):
            class Meta:
                model = CustomerTax
                fields = ("rate", "description")

            def clean_rate(self):
                rate = self.cleaned_data.get("rate")
                if rate is not None and (rate < 0 or rate > 100):
                    from django.core.exceptions import ValidationError

                    raise ValidationError("Rate must be between 0 and 100")
                return rate

        # Test valid rate
        data = {"rate": 19.0, "description": "Valid Tax"}
        form = CustomerTaxForm(data=data)
        assert form.is_valid()

        # Test invalid rate
        data = {"rate": 150.0, "description": "Invalid Tax"}
        form = CustomerTaxForm(data=data)
        assert not form.is_valid()
        assert "rate" in form.errors
