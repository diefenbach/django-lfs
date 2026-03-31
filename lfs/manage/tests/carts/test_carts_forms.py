import pytest
from datetime import date

from django import forms
from django.test import RequestFactory
from django.utils.translation import gettext_lazy as _

from lfs.manage.carts.forms import CartFilterForm


@pytest.fixture
def request_factory():
    """Request factory for creating mock requests."""
    return RequestFactory()


class TestCartFilterForm:
    """Test CartFilterForm functionality."""

    def test_form_has_correct_fields(self):
        """Test that form has the correct fields."""
        form = CartFilterForm()

        assert "start" in form.fields
        assert "end" in form.fields
        assert len(form.fields) == 2

    def test_form_fields_are_date_fields(self):
        """Test that form fields are DateField instances."""
        form = CartFilterForm()

        assert isinstance(form.fields["start"], forms.DateField)
        assert isinstance(form.fields["end"], forms.DateField)

    def test_form_fields_are_not_required(self):
        """Test that form fields are not required."""
        form = CartFilterForm()

        assert not form.fields["start"].required
        assert not form.fields["end"].required

    def test_form_fields_have_correct_labels(self):
        """Test that form fields have correct labels."""
        form = CartFilterForm()

        assert form.fields["start"].label == _("Start Date")
        assert form.fields["end"].label == _("End Date")

    def test_form_fields_have_correct_widgets(self):
        """Test that form fields have correct widgets."""
        form = CartFilterForm()

        assert isinstance(form.fields["start"].widget, forms.DateInput)
        assert isinstance(form.fields["end"].widget, forms.DateInput)

    def test_form_widgets_have_correct_attributes(self):
        """Test that form widgets have correct CSS classes and attributes."""
        form = CartFilterForm()

        start_widget = form.fields["start"].widget
        end_widget = form.fields["end"].widget

        assert "form-control form-control-sm dateinput" in start_widget.attrs["class"]
        assert "form-control form-control-sm dateinput" in end_widget.attrs["class"]
        assert start_widget.attrs["placeholder"] == _("Select start date")
        assert end_widget.attrs["placeholder"] == _("Select end date")

    def test_form_validation_with_valid_data(self):
        """Test form validation with valid date data."""
        form_data = {"start": "2024-01-01", "end": "2024-12-31"}
        form = CartFilterForm(data=form_data)

        assert form.is_valid()
        assert form.cleaned_data["start"] == date(2024, 1, 1)
        assert form.cleaned_data["end"] == date(2024, 12, 31)

    def test_form_validation_with_empty_data(self):
        """Test form validation with empty data."""
        form_data = {}
        form = CartFilterForm(data=form_data)

        assert form.is_valid()
        assert form.cleaned_data["start"] is None
        assert form.cleaned_data["end"] is None

    def test_form_validation_with_partial_data(self):
        """Test form validation with only start or end date."""
        # Only start date
        form_data = {"start": "2024-01-01"}
        form = CartFilterForm(data=form_data)

        assert form.is_valid()
        assert form.cleaned_data["start"] == date(2024, 1, 1)
        assert form.cleaned_data["end"] is None

        # Only end date
        form_data = {"end": "2024-12-31"}
        form = CartFilterForm(data=form_data)

        assert form.is_valid()
        assert form.cleaned_data["start"] is None
        assert form.cleaned_data["end"] == date(2024, 12, 31)

    def test_form_validation_with_invalid_date_formats(self):
        """Test form validation with invalid date formats."""
        invalid_data_sets = [
            {"start": "invalid-date", "end": "2024-12-31"},
            {"start": "2024-01-01", "end": "invalid-date"},
            {"start": "2024/01/01", "end": "2024-12-31"},
            {"start": "01-01-2024", "end": "2024-12-31"},
            {"start": "2024-13-01", "end": "2024-12-31"},
            {"start": "2024-01-32", "end": "2024-12-31"},
        ]

        for form_data in invalid_data_sets:
            form = CartFilterForm(data=form_data)
            assert not form.is_valid()
            assert "start" in form.errors or "end" in form.errors

    def test_form_validation_with_empty_strings(self):
        """Test form validation with empty string values."""
        form_data = {"start": "", "end": ""}
        form = CartFilterForm(data=form_data)

        assert form.is_valid()
        assert form.cleaned_data["start"] is None
        assert form.cleaned_data["end"] is None

    def test_form_validation_with_whitespace_strings(self):
        """Test form validation with whitespace-only strings."""
        form_data = {"start": "   ", "end": "  \t  "}
        form = CartFilterForm(data=form_data)

        # Django's DateField doesn't accept whitespace-only strings as valid
        assert not form.is_valid()
        assert "start" in form.errors
        assert "end" in form.errors

    def test_form_validation_with_none_values(self):
        """Test form validation with None values."""
        form_data = {"start": None, "end": None}
        form = CartFilterForm(data=form_data)

        assert form.is_valid()
        assert form.cleaned_data["start"] is None
        assert form.cleaned_data["end"] is None

    @pytest.mark.parametrize(
        "valid_date",
        [
            "2024-01-01",
            "2024-12-31",
            "2000-02-29",  # Leap year
            "2023-06-15",
            "1900-01-01",
            "9999-12-31",
        ],
    )
    def test_form_validation_with_various_valid_dates(self, valid_date):
        """Test form validation with various valid date formats."""
        form_data = {"start": valid_date}
        form = CartFilterForm(data=form_data)

        assert form.is_valid()
        assert form.cleaned_data["start"] is not None

    @pytest.mark.parametrize(
        "invalid_date",
        [
            "invalid-date",
            "2024/01/01",
            "01-01-2024",
            "2024-13-01",
            "2024-01-32",
            "2024-02-30",
            "2024-01-01T12:00:00",
            "2024-01-01 12:00:00",
            "abc-def-ghi",
            "2024-00-01",
            "2024-01-00",
        ],
    )
    def test_form_validation_with_various_invalid_dates(self, invalid_date):
        """Test form validation with various invalid date formats."""
        form_data = {"start": invalid_date}
        form = CartFilterForm(data=form_data)

        assert not form.is_valid()
        assert "start" in form.errors

    def test_form_initial_data_handling(self):
        """Test form initial data handling."""
        initial_data = {"start": date(2024, 1, 1), "end": date(2024, 12, 31)}
        form = CartFilterForm(initial=initial_data)

        assert form.initial["start"] == date(2024, 1, 1)
        assert form.initial["end"] == date(2024, 12, 31)

    def test_form_initial_data_with_none_values(self):
        """Test form initial data with None values."""
        initial_data = {"start": None, "end": None}
        form = CartFilterForm(initial=initial_data)

        assert form.initial["start"] is None
        assert form.initial["end"] is None

    def test_form_initial_data_with_partial_values(self):
        """Test form initial data with partial values."""
        initial_data = {"start": date(2024, 1, 1)}
        form = CartFilterForm(initial=initial_data)

        assert form.initial["start"] == date(2024, 1, 1)
        assert "end" not in form.initial or form.initial["end"] is None

    def test_form_rendering_includes_correct_html_attributes(self):
        """Test that form rendering includes correct HTML attributes."""
        form = CartFilterForm()

        # Test start field rendering
        start_html = str(form["start"])
        assert 'class="form-control form-control-sm dateinput"' in start_html
        assert 'placeholder="Select start date"' in start_html
        assert 'type="text"' in start_html  # Django's DateInput uses type="text" by default

        # Test end field rendering
        end_html = str(form["end"])
        assert 'class="form-control form-control-sm dateinput"' in end_html
        assert 'placeholder="Select end date"' in end_html
        assert 'type="text"' in end_html  # Django's DateInput uses type="text" by default

    def test_form_rendering_with_data(self):
        """Test form rendering with data."""
        form_data = {"start": "2024-01-01", "end": "2024-12-31"}
        form = CartFilterForm(data=form_data)

        # Form should render without errors
        start_html = str(form["start"])
        end_html = str(form["end"])

        assert 'value="2024-01-01"' in start_html
        assert 'value="2024-12-31"' in end_html

    def test_form_rendering_with_errors(self):
        """Test form rendering with validation errors."""
        form_data = {"start": "invalid-date", "end": "also-invalid"}
        form = CartFilterForm(data=form_data)

        # Form should not be valid
        assert not form.is_valid()

        # Should have errors
        assert "start" in form.errors
        assert "end" in form.errors

    def test_form_field_order(self):
        """Test that form fields are in the correct order."""
        form = CartFilterForm()
        field_names = list(form.fields.keys())

        assert field_names == ["start", "end"]

    def test_form_field_help_text(self):
        """Test that form fields have no help text."""
        form = CartFilterForm()

        assert not form.fields["start"].help_text
        assert not form.fields["end"].help_text

    def test_form_field_error_messages(self):
        """Test that form fields have appropriate error messages."""
        form = CartFilterForm()

        # Test with invalid data to trigger error messages
        form_data = {"start": "invalid-date"}
        form = CartFilterForm(data=form_data)

        assert not form.is_valid()
        assert "start" in form.errors
        # Error message should indicate invalid date format
        assert any("date" in str(error).lower() for error in form.errors["start"])

    def test_form_validation_with_boundary_dates(self):
        """Test form validation with boundary date values."""
        boundary_dates = [
            "1900-01-01",  # Very old date
            "9999-12-31",  # Very future date
            "2000-02-29",  # Leap year
            "2024-02-29",  # Another leap year
        ]

        for test_date in boundary_dates:
            form_data = {"start": test_date}
            form = CartFilterForm(data=form_data)

            assert form.is_valid(), f"Date {test_date} should be valid"
            assert form.cleaned_data["start"] is not None

    def test_form_validation_with_invalid_boundary_dates(self):
        """Test form validation with invalid boundary date values."""
        invalid_boundary_dates = [
            "10000-01-01",  # After 9999
            "2023-02-29",  # Not a leap year
            "2024-02-30",  # Invalid day for February
        ]

        for test_date in invalid_boundary_dates:
            form_data = {"start": test_date}
            form = CartFilterForm(data=form_data)

            assert not form.is_valid(), f"Date {test_date} should be invalid"
            assert "start" in form.errors
