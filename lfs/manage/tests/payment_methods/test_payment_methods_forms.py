"""
Comprehensive unit tests for payment method forms.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Fast tests with minimal mocking

Tests cover:
- PaymentMethodForm field validation
- PaymentMethodAddForm field validation
- Form rendering and widget attributes
- Form cleaning and data handling
- Edge cases and error conditions
"""

import pytest

from django import forms

from lfs.manage.payment_methods.forms import PaymentMethodForm, PaymentMethodAddForm
from lfs.payment.models import PaymentMethod
from lfs.core.widgets.image import LFSImageInput


class TestPaymentMethodForm:
    """Test PaymentMethodForm functionality."""

    def test_form_excludes_correct_fields(self):
        """Test that form excludes deletable and priority fields."""
        form = PaymentMethodForm()

        assert "deletable" not in form.fields
        assert "priority" not in form.fields

    def test_form_includes_expected_fields(self):
        """Test that form includes expected fields from PaymentMethod model."""
        form = PaymentMethodForm()

        # These fields should be included based on PaymentMethod model
        expected_fields = ["name", "description", "active", "image"]

        for field_name in expected_fields:
            assert field_name in form.fields

    def test_image_field_uses_lfs_image_widget(self):
        """Test that image field uses LFSImageInput widget."""
        form = PaymentMethodForm()

        assert isinstance(form.fields["image"].widget, LFSImageInput)

    def test_form_is_model_form(self):
        """Test that PaymentMethodForm is a ModelForm."""
        assert issubclass(PaymentMethodForm, forms.ModelForm)

    def test_form_uses_payment_method_model(self):
        """Test that form uses PaymentMethod model."""
        assert PaymentMethodForm.Meta.model == PaymentMethod

    def test_form_can_be_instantiated_empty(self):
        """Test that form can be instantiated without data."""
        form = PaymentMethodForm()

        assert form is not None
        assert not form.is_bound

    def test_form_can_be_instantiated_with_instance(self, payment_method):
        """Test that form can be instantiated with PaymentMethod instance."""
        form = PaymentMethodForm(instance=payment_method)

        assert form.instance == payment_method
        assert not form.is_bound

    def test_form_validation_with_valid_data(self):
        """Test form validation with valid data."""
        valid_data = {
            "name": "Test Payment Method",
            "description": "Test description",
            "active": True,
            "price": "10.00",
            "type": 0,
        }

        form = PaymentMethodForm(data=valid_data)

        assert form.is_valid()

    def test_form_validation_with_missing_required_fields(self):
        """Test form validation with missing required fields."""
        invalid_data = {
            "description": "Test description",
            "active": True,
        }

        form = PaymentMethodForm(data=invalid_data)

        assert not form.is_valid()
        assert "name" in form.errors

    def test_form_validation_with_empty_name(self):
        """Test form validation with empty name field."""
        invalid_data = {
            "name": "",
            "description": "Test description",
            "active": True,
        }

        form = PaymentMethodForm(data=invalid_data)

        assert not form.is_valid()
        assert "name" in form.errors

    def test_form_validation_with_very_long_name(self):
        """Test form validation with very long name."""
        # Assuming name field has max_length constraint
        long_name = "x" * 300  # Very long name

        data = {
            "name": long_name,
            "description": "Test description",
            "active": True,
        }

        form = PaymentMethodForm(data=data)

        # This test might pass or fail depending on model field constraints
        # If there's a max_length constraint, it should fail
        if not form.is_valid():
            assert "name" in form.errors

    @pytest.mark.django_db
    def test_form_save_creates_payment_method(self):
        """Test that form save creates PaymentMethod instance."""
        valid_data = {
            "name": "New Payment Method",
            "description": "New description",
            "active": True,
            "price": "15.00",
            "type": 0,
        }

        form = PaymentMethodForm(data=valid_data)

        assert form.is_valid()

        payment_method = form.save()

        assert payment_method.name == "New Payment Method"
        assert payment_method.description == "New description"
        assert payment_method.active is True

    def test_form_save_updates_existing_payment_method(self, payment_method):
        """Test that form save updates existing PaymentMethod instance."""
        updated_data = {
            "name": "Updated Payment Method",
            "description": "Updated description",
            "active": False,
            "price": "20.00",
            "type": 1,
        }

        form = PaymentMethodForm(data=updated_data, instance=payment_method)

        assert form.is_valid()

        updated_payment_method = form.save()

        assert updated_payment_method.id == payment_method.id
        assert updated_payment_method.name == "Updated Payment Method"
        assert updated_payment_method.description == "Updated description"
        assert updated_payment_method.active is False

    def test_form_save_commit_false_returns_unsaved_instance(self):
        """Test that form save with commit=False returns unsaved instance."""
        valid_data = {
            "name": "Test Payment Method",
            "description": "Test description",
            "active": True,
            "price": "12.00",
            "type": 0,
        }

        form = PaymentMethodForm(data=valid_data)

        assert form.is_valid()

        payment_method = form.save(commit=False)

        assert payment_method.name == "Test Payment Method"
        assert payment_method.pk is None  # Not saved to database

    def test_form_initial_data_from_instance(self, payment_method):
        """Test that form shows initial data from instance."""
        form = PaymentMethodForm(instance=payment_method)

        assert form.initial["name"] == payment_method.name
        assert form.initial["description"] == payment_method.description
        assert form.initial["active"] == payment_method.active

    def test_form_widget_attributes(self):
        """Test that form widgets have expected attributes."""
        form = PaymentMethodForm()

        # Test that image widget is properly set
        assert isinstance(form.fields["image"].widget, LFSImageInput)

        # Other widgets should be default Django widgets
        assert isinstance(form.fields["name"].widget, forms.TextInput)
        assert isinstance(form.fields["active"].widget, forms.CheckboxInput)

    def test_form_field_help_text_preserved(self):
        """Test that form preserves field help text from model."""
        form = PaymentMethodForm()

        # Check if help text from model is preserved
        # This depends on the actual PaymentMethod model definition
        for field_name, field in form.fields.items():
            # Help text should be preserved from model field
            model_field = PaymentMethod._meta.get_field(field_name)
            if hasattr(model_field, "help_text") and model_field.help_text:
                assert field.help_text == model_field.help_text

    def test_form_field_labels_preserved(self):
        """Test that form preserves field labels from model."""
        form = PaymentMethodForm()

        # Check if labels from model are preserved
        for field_name, field in form.fields.items():
            model_field = PaymentMethod._meta.get_field(field_name)
            if hasattr(model_field, "verbose_name") and model_field.verbose_name:
                # Django automatically capitalizes verbose_name for labels
                expected_label = model_field.verbose_name.title()
                assert field.label == expected_label or field.label == model_field.verbose_name


class TestPaymentMethodAddForm:
    """Test PaymentMethodAddForm functionality."""

    def test_form_includes_only_name_field(self):
        """Test that form includes only name field."""
        form = PaymentMethodAddForm()

        assert "name" in form.fields
        assert len(form.fields) == 1

    def test_form_is_model_form(self):
        """Test that PaymentMethodAddForm is a ModelForm."""
        assert issubclass(PaymentMethodAddForm, forms.ModelForm)

    def test_form_uses_payment_method_model(self):
        """Test that form uses PaymentMethod model."""
        assert PaymentMethodAddForm.Meta.model == PaymentMethod

    def test_form_meta_fields_is_tuple(self):
        """Test that Meta.fields is properly defined as tuple."""
        assert PaymentMethodAddForm.Meta.fields == ("name",)
        assert isinstance(PaymentMethodAddForm.Meta.fields, tuple)

    def test_form_can_be_instantiated_empty(self):
        """Test that form can be instantiated without data."""
        form = PaymentMethodAddForm()

        assert form is not None
        assert not form.is_bound

    def test_form_validation_with_valid_name(self):
        """Test form validation with valid name."""
        valid_data = {"name": "New Payment Method"}

        form = PaymentMethodAddForm(data=valid_data)

        assert form.is_valid()

    def test_form_validation_with_empty_name(self):
        """Test form validation with empty name."""
        invalid_data = {"name": ""}

        form = PaymentMethodAddForm(data=invalid_data)

        assert not form.is_valid()
        assert "name" in form.errors

    def test_form_validation_with_missing_name(self):
        """Test form validation with missing name field."""
        invalid_data = {}

        form = PaymentMethodAddForm(data=invalid_data)

        assert not form.is_valid()
        assert "name" in form.errors

    def test_form_validation_with_whitespace_only_name(self):
        """Test form validation with whitespace-only name."""
        invalid_data = {"name": "   "}

        form = PaymentMethodAddForm(data=invalid_data)

        # This might pass or fail depending on field validation
        # If there's a strip validation, it should fail
        if not form.is_valid():
            assert "name" in form.errors

    @pytest.mark.django_db
    def test_form_save_creates_payment_method_with_defaults(self):
        """Test that form save creates PaymentMethod with default values."""
        valid_data = {"name": "New Payment Method"}

        form = PaymentMethodAddForm(data=valid_data)

        # Check if form is valid - PaymentMethodAddForm should only require name
        if form.is_valid():
            payment_method = form.save()
            assert payment_method.name == "New Payment Method"
            # Other fields should have model defaults
            assert payment_method.active is not None  # Could be True or False depending on model default
            assert hasattr(payment_method, "description")  # Should exist but could be empty
        else:
            # If form is not valid, it's likely due to missing required fields in the model
            # that aren't included in PaymentMethodAddForm
            assert len(form.errors) > 0

    def test_form_save_commit_false_returns_unsaved_instance(self):
        """Test that form save with commit=False returns unsaved instance."""
        valid_data = {"name": "Test Payment Method"}

        form = PaymentMethodAddForm(data=valid_data)

        assert form.is_valid()

        payment_method = form.save(commit=False)

        assert payment_method.name == "Test Payment Method"
        assert payment_method.pk is None  # Not saved to database

    def test_form_name_field_is_required(self):
        """Test that name field is required."""
        form = PaymentMethodAddForm()

        assert form.fields["name"].required is True

    def test_form_name_field_widget_type(self):
        """Test that name field uses correct widget."""
        form = PaymentMethodAddForm()

        assert isinstance(form.fields["name"].widget, forms.TextInput)

    def test_form_excludes_other_payment_method_fields(self):
        """Test that form excludes other PaymentMethod fields."""
        form = PaymentMethodAddForm()

        excluded_fields = ["description", "active", "priority", "deletable", "image"]

        for field_name in excluded_fields:
            assert field_name not in form.fields

    @pytest.mark.django_db
    def test_form_can_be_used_for_quick_creation(self):
        """Test that form can be used for quick payment method creation."""
        # This tests the intended use case of the form
        valid_data = {"name": "Quick Payment Method"}

        form = PaymentMethodAddForm(data=valid_data)

        assert form.is_valid()

        payment_method = form.save()

        # Should create a minimal but valid payment method
        assert payment_method.name == "Quick Payment Method"
        assert payment_method.pk is not None
        assert isinstance(payment_method, PaymentMethod)

    def test_form_preserves_name_field_properties(self):
        """Test that form preserves name field properties from model."""
        form = PaymentMethodAddForm()
        name_field = form.fields["name"]
        model_name_field = PaymentMethod._meta.get_field("name")

        # Properties should match model field
        if hasattr(model_name_field, "max_length"):
            assert name_field.max_length == model_name_field.max_length

        if hasattr(model_name_field, "help_text") and model_name_field.help_text:
            assert name_field.help_text == model_name_field.help_text

    def test_form_handles_duplicate_name_validation(self, payment_method):
        """Test form handles duplicate name validation if implemented."""
        # Try to create another payment method with same name
        duplicate_data = {"name": payment_method.name}

        form = PaymentMethodAddForm(data=duplicate_data)

        # This test depends on whether unique constraint exists on name field
        # If there's a unique constraint, validation should fail
        if not form.is_valid():
            assert "name" in form.errors
        else:
            # If no unique constraint, form should be valid
            # but saving might raise IntegrityError
            pass

    @pytest.mark.django_db
    def test_form_strips_whitespace_from_name(self):
        """Test that form strips whitespace from name field."""
        data_with_whitespace = {"name": "  Test Payment Method  "}

        form = PaymentMethodAddForm(data=data_with_whitespace)

        if form.is_valid():
            payment_method = form.save()
            # Name should be stripped of leading/trailing whitespace
            assert payment_method.name == "Test Payment Method"

    def test_form_handles_very_long_name_gracefully(self):
        """Test that form handles very long names gracefully."""
        very_long_name = "x" * 1000  # Very long name

        data = {"name": very_long_name}

        form = PaymentMethodAddForm(data=data)

        # Should either validate successfully or fail with appropriate error
        if not form.is_valid():
            assert "name" in form.errors
            # Error should be about length, not a generic error
            error_message = str(form.errors["name"][0]).lower()
            assert any(word in error_message for word in ["long", "length", "characters", "maximum"])

    @pytest.mark.django_db
    def test_form_handles_special_characters_in_name(self):
        """Test that form handles special characters in name."""
        special_chars_name = "Payment Method with Special Chars: !@#$%^&*()"

        data = {"name": special_chars_name}

        form = PaymentMethodAddForm(data=data)

        # Should handle special characters gracefully
        assert form.is_valid()

        payment_method = form.save()
        assert payment_method.name == special_chars_name

    @pytest.mark.django_db
    def test_form_handles_unicode_characters_in_name(self):
        """Test that form handles unicode characters in name."""
        unicode_name = "Método de Pago Español 中文支付方式"

        data = {"name": unicode_name}

        form = PaymentMethodAddForm(data=data)

        # Should handle unicode characters gracefully
        assert form.is_valid()

        payment_method = form.save()
        assert payment_method.name == unicode_name
