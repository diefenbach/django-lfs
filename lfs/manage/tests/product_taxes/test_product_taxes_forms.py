"""
Form tests for Product Taxes management.

Tests form validation, saving behavior, and error handling.
Product taxes views use Django's automatic ModelForm generation based on fields attribute.
"""

import pytest

from lfs.tax.models import Tax
from lfs.manage.product_taxes.forms import TaxForm, TaxAddForm


class TestTaxForm:
    """Test TaxForm form behavior."""

    def test_form_meta_model(self):
        """Should use Tax model."""
        assert TaxForm.Meta.model == Tax

    def test_form_meta_exclude(self):
        """Should not exclude any fields."""
        assert TaxForm.Meta.exclude == ()

    @pytest.mark.django_db
    def test_form_initialization_with_tax(self, tax):
        """Should initialize form with tax data."""
        form = TaxForm(instance=tax)

        assert form.instance == tax
        assert form.instance.rate == tax.rate
        assert form.instance.description == tax.description

    def test_valid_form_data(self):
        """Should accept valid form data."""
        data = {
            "rate": "19.0",
            "description": "VAT 19%",
        }

        form = TaxForm(data=data)
        assert form.is_valid()

    def test_required_fields_validation(self):
        """Should require rate field but not description."""
        # Test missing rate
        data = {"description": "VAT 19%"}
        form = TaxForm(data=data)
        assert not form.is_valid()
        assert "rate" in form.errors

        # Test with only rate (description is optional)
        data = {"rate": "19.0"}
        form = TaxForm(data=data)
        assert form.is_valid()

    def test_rate_validation(self):
        """Should validate rate field."""
        # Test invalid rate format
        data = {"rate": "invalid", "description": "VAT 19%"}
        form = TaxForm(data=data)
        assert not form.is_valid()
        assert "rate" in form.errors

        # Test negative rate (FloatField allows negative values)
        data = {"rate": "-5.0", "description": "VAT 19%"}
        form = TaxForm(data=data)
        assert form.is_valid()  # FloatField allows negative values

    def test_valid_rate_formats(self):
        """Should accept valid rate formats."""
        valid_rates = ["0.0", "7.0", "19.0", "25.0", "100.0"]

        for rate in valid_rates:
            data = {"rate": rate, "description": f"VAT {rate}%"}
            form = TaxForm(data=data)
            assert form.is_valid(), f"Rate '{rate}' should be valid"

    def test_description_max_length_validation(self):
        """Should validate description maximum length."""
        # TextField doesn't have max_length by default, so this test should pass
        long_description = "A" * 1000
        data = {"rate": "19.0", "description": long_description}
        form = TaxForm(data=data)
        assert form.is_valid()  # TextField allows long text

    @pytest.mark.django_db
    def test_form_save_creates_tax(self):
        """Should create new tax when saving form."""
        data = {"rate": "15.0", "description": "New VAT"}
        form = TaxForm(data=data)

        assert form.is_valid()
        tax = form.save()

        assert tax.rate == 15.0
        assert tax.description == "New VAT"
        assert Tax.objects.filter(rate=15.0).exists()

    @pytest.mark.django_db
    def test_form_save_updates_existing_tax(self, tax):
        """Should update existing tax when saving form."""
        data = {"rate": "20.0", "description": "Updated VAT"}
        form = TaxForm(data=data, instance=tax)

        assert form.is_valid()
        updated_tax = form.save()

        assert updated_tax == tax
        assert updated_tax.rate == 20.0
        assert updated_tax.description == "Updated VAT"

    def test_form_fields_exist(self):
        """Should have required form fields."""
        form = TaxForm()
        assert "rate" in form.fields
        assert "description" in form.fields

    def test_form_field_types(self):
        """Should have correct field types."""
        form = TaxForm()

        # Rate should be a float field
        from django.forms.fields import FloatField

        assert isinstance(form.fields["rate"], FloatField)

        # Description should be a text field
        from django.forms.fields import CharField

        assert isinstance(form.fields["description"], CharField)


class TestTaxAddForm:
    """Test TaxAddForm form behavior."""

    def test_form_meta_model(self):
        """Should use Tax model."""
        assert TaxAddForm.Meta.model == Tax

    def test_form_meta_fields(self):
        """Should include only rate field."""
        assert TaxAddForm.Meta.fields == ("rate",)

    def test_form_initialization(self):
        """Should initialize form with empty instance."""
        form = TaxAddForm()
        assert form.instance is not None  # ModelForm creates an instance
        assert form.instance.pk is None  # But it's not saved yet

    def test_valid_form_data(self):
        """Should accept valid form data."""
        data = {"rate": "19.0"}
        form = TaxAddForm(data=data)
        assert form.is_valid()

    def test_required_rate_field_validation(self):
        """Should require rate field."""
        data = {}
        form = TaxAddForm(data=data)
        assert not form.is_valid()
        assert "rate" in form.errors

    def test_rate_validation(self):
        """Should validate rate field."""
        # Test invalid rate format
        data = {"rate": "invalid"}
        form = TaxAddForm(data=data)
        assert not form.is_valid()
        assert "rate" in form.errors

        # Test negative rate (FloatField allows negative values)
        data = {"rate": "-5.0"}
        form = TaxAddForm(data=data)
        assert form.is_valid()  # FloatField allows negative values

    def test_valid_rate_formats(self):
        """Should accept valid rate formats."""
        valid_rates = ["0.0", "7.0", "19.0", "25.0", "100.0"]

        for rate in valid_rates:
            data = {"rate": rate}
            form = TaxAddForm(data=data)
            assert form.is_valid(), f"Rate '{rate}' should be valid"

    @pytest.mark.django_db
    def test_form_save_creates_tax(self):
        """Should create new tax when saving form."""
        data = {"rate": "15.0"}
        form = TaxAddForm(data=data)

        assert form.is_valid()
        tax = form.save()

        assert tax.rate == 15.0
        assert tax.description == ""  # Description should be empty by default
        assert Tax.objects.filter(rate=15.0).exists()

    def test_form_fields_exist(self):
        """Should have only rate field."""
        form = TaxAddForm()
        assert "rate" in form.fields
        assert "description" not in form.fields

    def test_form_field_type(self):
        """Should have correct field type for rate."""
        form = TaxAddForm()

        # Rate should be a float field
        from django.forms.fields import FloatField

        assert isinstance(form.fields["rate"], FloatField)

    @pytest.mark.django_db
    def test_form_save_with_commit_false(self):
        """Should create tax instance without saving to database when commit=False."""
        data = {"rate": "15.0"}
        form = TaxAddForm(data=data)

        assert form.is_valid()
        tax = form.save(commit=False)

        assert tax.rate == 15.0
        assert not Tax.objects.filter(rate=15.0).exists()  # Not saved to DB

    @pytest.mark.django_db
    def test_form_save_with_commit_true(self):
        """Should create and save tax to database when commit=True."""
        data = {"rate": "15.0"}
        form = TaxAddForm(data=data)

        assert form.is_valid()
        tax = form.save(commit=True)

        assert tax.rate == 15.0
        assert Tax.objects.filter(rate=15.0).exists()  # Saved to DB

    def test_form_validation_with_invalid_data(self):
        """Should not be valid with invalid data."""
        invalid_data_sets = [
            {"rate": ""},  # Empty rate
            {"rate": "not_a_number"},  # Non-numeric rate
            # Note: FloatField allows negative values and large values
        ]

        for invalid_data in invalid_data_sets:
            form = TaxAddForm(data=invalid_data)
            assert not form.is_valid(), f"Data {invalid_data} should be invalid"
            assert "rate" in form.errors

    def test_form_clean_method_validation(self):
        """Should validate data through clean methods."""
        # Test with valid data
        data = {"rate": "19.0"}
        form = TaxAddForm(data=data)
        assert form.is_valid()
        assert form.cleaned_data["rate"] == 19.0

        # Test with invalid data
        data = {"rate": "invalid"}
        form = TaxAddForm(data=data)
        assert not form.is_valid()
        assert "rate" in form.errors
