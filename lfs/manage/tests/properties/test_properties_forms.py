from django import forms
from django.utils.translation import gettext_lazy as _

from lfs.catalog.settings import (
    PROPERTY_NUMBER_FIELD,
    PROPERTY_TEXT_FIELD,
    PROPERTY_STEP_TYPE_FIXED_STEP,
    PROPERTY_STEP_TYPE_AUTOMATIC,
)
from lfs.manage.properties.forms import PropertyAddForm, PropertyDataForm


class TestPropertyAddForm:
    """Test PropertyAddForm functionality."""

    def test_form_has_correct_fields(self):
        """Test that form has the correct fields."""
        form = PropertyAddForm()

        assert "name" in form.fields
        assert len(form.fields) == 1

    def test_form_field_is_charfield(self):
        """Test that form field is CharField instance."""
        form = PropertyAddForm()

        assert isinstance(form.fields["name"], forms.CharField)

    def test_form_field_is_required(self):
        """Test that form field is required."""
        form = PropertyAddForm()

        assert form.fields["name"].required

    def test_form_field_has_correct_label(self):
        """Test that form field has correct label."""
        form = PropertyAddForm()

        assert form.fields["name"].label == _("Name")

    def test_form_validation_with_valid_data(self):
        """Test form validation with valid data."""
        form_data = {"name": "Test Property"}
        form = PropertyAddForm(data=form_data)

        assert form.is_valid()
        assert form.cleaned_data["name"] == "Test Property"

    def test_form_validation_with_empty_data(self):
        """Test form validation with empty data."""
        form_data = {}
        form = PropertyAddForm(data=form_data)

        assert not form.is_valid()
        assert "name" in form.errors

    def test_form_validation_with_whitespace_only(self):
        """Test form validation with whitespace-only data."""
        form_data = {"name": "   "}
        form = PropertyAddForm(data=form_data)

        assert not form.is_valid()
        assert "name" in form.errors


class TestPropertyDataForm:
    """Test PropertyDataForm functionality."""

    def test_form_has_correct_fields(self):
        """Test that form has the correct fields."""
        form = PropertyDataForm()

        expected_fields = [
            "name",
            "title",
            "unit",
            "type",
            "variants",
            "filterable",
            "configurable",
            "required",
            "display_on_product",
            "display_price",
            "add_price",
            "decimal_places",
            "unit_min",
            "unit_max",
            "unit_step",
            "step_type",
            "step",
        ]

        for field in expected_fields:
            assert field in form.fields

        assert len(form.fields) == len(expected_fields)

    def test_form_field_types(self):
        """Test that form fields have correct types."""
        form = PropertyDataForm()

        # CharField types
        assert isinstance(form.fields["name"], forms.CharField)
        assert isinstance(form.fields["title"], forms.CharField)
        assert isinstance(form.fields["unit"], forms.CharField)

        # ChoiceField types
        assert isinstance(form.fields["type"], forms.ChoiceField)
        assert isinstance(form.fields["step_type"], forms.ChoiceField)

        # BooleanField types
        assert isinstance(form.fields["variants"], forms.BooleanField)
        assert isinstance(form.fields["filterable"], forms.BooleanField)
        assert isinstance(form.fields["configurable"], forms.BooleanField)
        assert isinstance(form.fields["required"], forms.BooleanField)
        assert isinstance(form.fields["display_on_product"], forms.BooleanField)
        assert isinstance(form.fields["display_price"], forms.BooleanField)
        assert isinstance(form.fields["add_price"], forms.BooleanField)

        # IntegerField types
        assert isinstance(form.fields["decimal_places"], forms.IntegerField)
        assert isinstance(form.fields["unit_min"], forms.IntegerField)
        assert isinstance(form.fields["unit_max"], forms.IntegerField)
        assert isinstance(form.fields["unit_step"], forms.IntegerField)
        assert isinstance(form.fields["step"], forms.IntegerField)

    def test_required_fields(self):
        """Test that correct fields are required."""
        form = PropertyDataForm()

        # These fields should be required
        assert form.fields["name"].required
        assert form.fields["title"].required

        # These fields should not be required
        assert not form.fields["unit"].required
        assert not form.fields["variants"].required
        assert not form.fields["filterable"].required
        assert not form.fields["configurable"].required
        assert not form.fields["required"].required
        assert not form.fields["display_on_product"].required
        assert not form.fields["display_price"].required
        assert not form.fields["add_price"].required
        # decimal_places is required (PositiveSmallIntegerField without blank/null)
        assert form.fields["decimal_places"].required
        assert not form.fields["unit_min"].required
        assert not form.fields["unit_max"].required
        assert not form.fields["unit_step"].required
        # step_type is required (PositiveSmallIntegerField without blank/null)
        assert form.fields["step_type"].required
        assert not form.fields["step"].required

    def test_form_validation_with_valid_data(self):
        """Test form validation with valid data."""
        form_data = {
            "name": "Test Property",
            "title": "Test Title",
            "unit": "kg",
            "type": PROPERTY_NUMBER_FIELD,
            "variants": True,
            "filterable": True,
            "configurable": False,
            "required": True,
            "display_on_product": True,
            "display_price": False,
            "add_price": True,
            "decimal_places": 2,
            "unit_min": 0,
            "unit_max": 100,
            "unit_step": 1,
            "step_type": PROPERTY_STEP_TYPE_FIXED_STEP,
            "step": 5,
        }
        form = PropertyDataForm(data=form_data)

        assert form.is_valid()
        assert form.cleaned_data["name"] == "Test Property"
        assert form.cleaned_data["title"] == "Test Title"
        assert form.cleaned_data["unit"] == "kg"
        assert form.cleaned_data["type"] == PROPERTY_NUMBER_FIELD
        assert form.cleaned_data["variants"] is True
        assert form.cleaned_data["filterable"] is True
        assert form.cleaned_data["configurable"] is False
        assert form.cleaned_data["required"] is True
        assert form.cleaned_data["display_on_product"] is True
        assert form.cleaned_data["display_price"] is False
        assert form.cleaned_data["add_price"] is True
        assert form.cleaned_data["decimal_places"] == 2
        assert form.cleaned_data["unit_min"] == 0
        assert form.cleaned_data["unit_max"] == 100
        assert form.cleaned_data["unit_step"] == 1
        assert form.cleaned_data["step_type"] == PROPERTY_STEP_TYPE_FIXED_STEP
        assert form.cleaned_data["step"] == 5

    def test_form_validation_with_minimal_data(self):
        """Test form validation with minimal required data."""
        form_data = {
            "name": "Test Property",
            "title": "Test Title",
            "type": PROPERTY_TEXT_FIELD,  # May be required by form
            "decimal_places": 0,  # Required field
            "step_type": PROPERTY_STEP_TYPE_AUTOMATIC,  # Required field
        }
        form = PropertyDataForm(data=form_data)

        assert form.is_valid()
        assert form.cleaned_data["name"] == "Test Property"
        assert form.cleaned_data["title"] == "Test Title"
        assert form.cleaned_data["decimal_places"] == 0
        assert form.cleaned_data["step_type"] == PROPERTY_STEP_TYPE_AUTOMATIC

    def test_form_validation_with_empty_required_fields(self):
        """Test form validation with empty required fields."""
        form_data = {}
        form = PropertyDataForm(data=form_data)

        assert not form.is_valid()
        assert "name" in form.errors
        assert "title" in form.errors

    def test_form_validation_with_invalid_integer_values(self):
        """Test form validation with invalid integer values."""
        form_data = {
            "name": "Test Property",
            "title": "Test Title",
            "decimal_places": "invalid",
            "unit_min": "not_a_number",
            "unit_max": "text",
            "unit_step": "abc",
            "step": "xyz",
        }
        form = PropertyDataForm(data=form_data)

        assert not form.is_valid()
        assert "decimal_places" in form.errors
        assert "unit_min" in form.errors
        assert "unit_max" in form.errors
        assert "unit_step" in form.errors
        assert "step" in form.errors

    def test_form_validation_with_negative_values(self):
        """Test form validation with negative values for numeric fields."""
        form_data = {
            "name": "Test Property",
            "title": "Test Title",
            "decimal_places": -1,  # This should fail because decimal_places is PositiveSmallIntegerField
            "unit_min": -5,
            "unit_max": -10,
            "unit_step": -1,
            "step": -2,
        }
        form = PropertyDataForm(data=form_data)

        # decimal_places should fail validation due to PositiveSmallIntegerField constraint
        assert not form.is_valid()
        assert "decimal_places" in form.errors

    def test_form_choice_field_options(self):
        """Test that choice fields have correct options."""
        form = PropertyDataForm()

        # Check type field choices
        type_choices = form.fields["type"].choices
        assert len(type_choices) > 0

        # Check step_type field choices
        step_type_choices = form.fields["step_type"].choices
        assert len(step_type_choices) > 0
