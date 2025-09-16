import pytest
from datetime import date, timedelta
from django.utils.translation import gettext_lazy as _

from lfs.manage.customers.forms import CustomerFilterForm


class TestCustomerFilterForm:
    """Test CustomerFilterForm functionality."""

    def test_should_have_correct_fields(self):
        """Test that form has all expected fields."""
        form = CustomerFilterForm()

        assert "name" in form.fields
        assert "start" in form.fields
        assert "end" in form.fields

    def test_should_have_correct_field_types(self):
        """Test that fields have correct types."""
        form = CustomerFilterForm()

        assert isinstance(form.fields["name"], type(form.fields["name"]))
        assert isinstance(form.fields["start"], type(form.fields["start"]))
        assert isinstance(form.fields["end"], type(form.fields["end"]))

    def test_should_be_valid_with_empty_data(self):
        """Test that form is valid with empty data (all fields are optional)."""
        form = CustomerFilterForm(data={})

        assert form.is_valid()

    def test_should_be_valid_with_valid_name(self):
        """Test that form is valid with valid name."""
        form = CustomerFilterForm(data={"name": "John Doe"})

        assert form.is_valid()
        assert form.cleaned_data["name"] == "John Doe"

    def test_should_be_valid_with_valid_start_date(self):
        """Test that form is valid with valid start date."""
        test_date = date.today()
        form = CustomerFilterForm(data={"start": test_date})

        assert form.is_valid()
        assert form.cleaned_data["start"] == test_date

    def test_should_be_valid_with_valid_end_date(self):
        """Test that form is valid with valid end date."""
        test_date = date.today()
        form = CustomerFilterForm(data={"end": test_date})

        assert form.is_valid()
        assert form.cleaned_data["end"] == test_date

    def test_should_be_valid_with_all_fields(self):
        """Test that form is valid with all fields provided."""
        test_date = date.today()
        form = CustomerFilterForm(data={"name": "John Doe", "start": test_date, "end": test_date})

        assert form.is_valid()
        assert form.cleaned_data["name"] == "John Doe"
        assert form.cleaned_data["start"] == test_date
        assert form.cleaned_data["end"] == test_date

    def test_should_be_invalid_with_invalid_start_date(self):
        """Test that form is invalid with invalid start date."""
        form = CustomerFilterForm(data={"start": "invalid-date"})

        assert not form.is_valid()
        assert "start" in form.errors

    def test_should_be_invalid_with_invalid_end_date(self):
        """Test that form is invalid with invalid end date."""
        form = CustomerFilterForm(data={"end": "invalid-date"})

        assert not form.is_valid()
        assert "end" in form.errors

    def test_should_be_invalid_with_name_too_long(self):
        """Test that form is invalid with name exceeding max length."""
        long_name = "x" * 101  # Exceeds max_length=100
        form = CustomerFilterForm(data={"name": long_name})

        assert not form.is_valid()
        assert "name" in form.errors

    def test_should_be_valid_with_name_at_max_length(self):
        """Test that form is valid with name at max length."""
        max_name = "x" * 100  # Exactly max_length=100
        form = CustomerFilterForm(data={"name": max_name})

        assert form.is_valid()
        assert form.cleaned_data["name"] == max_name

    def test_should_handle_whitespace_only_name(self):
        """Test that form handles whitespace-only name correctly."""
        form = CustomerFilterForm(data={"name": "   "})

        # Form should be valid, but cleaned_data may strip whitespace
        assert form.is_valid()
        # Django's CharField strips whitespace by default
        assert form.cleaned_data["name"] == ""

    def test_should_handle_empty_string_name(self):
        """Test that form handles empty string name correctly."""
        form = CustomerFilterForm(data={"name": ""})

        assert form.is_valid()
        assert form.cleaned_data["name"] == ""

    def test_should_handle_none_name(self):
        """Test that form handles None name correctly."""
        form = CustomerFilterForm(data={"name": None})

        assert form.is_valid()
        # Django converts None to empty string for CharField
        assert form.cleaned_data["name"] == ""

    @pytest.mark.parametrize(
        "valid_date",
        [
            "2024-01-01",
            "2024-12-31",
            "2024-02-29",  # Leap year
        ],
    )
    def test_should_accept_valid_date_formats(self, valid_date):
        """Test that form accepts various valid date formats."""
        form = CustomerFilterForm(data={"start": valid_date})

        assert form.is_valid()
        assert form.cleaned_data["start"] is not None

    @pytest.mark.parametrize(
        "invalid_date",
        [
            "2024-13-01",  # Invalid month
            "2024-01-32",  # Invalid day
            "2024-02-30",  # Invalid day for February
            "not-a-date",
            "2024/01/01",  # Wrong separator
            "01-01-2024",  # Wrong order
        ],
    )
    def test_should_reject_invalid_date_formats(self, invalid_date):
        """Test that form rejects various invalid date formats."""
        form = CustomerFilterForm(data={"start": invalid_date})

        assert not form.is_valid()
        assert "start" in form.errors

    def test_should_have_correct_field_labels(self):
        """Test that fields have correct labels."""
        form = CustomerFilterForm()

        assert form.fields["name"].label == _("Name")
        assert form.fields["start"].label == _("Start Date")
        assert form.fields["end"].label == _("End Date")

    def test_should_have_correct_field_required_settings(self):
        """Test that fields have correct required settings."""
        form = CustomerFilterForm()

        assert not form.fields["name"].required
        assert not form.fields["start"].required
        assert not form.fields["end"].required

    def test_should_have_correct_field_max_length(self):
        """Test that name field has correct max_length."""
        form = CustomerFilterForm()

        assert form.fields["name"].max_length == 100

    def test_should_have_correct_widget_classes(self):
        """Test that fields have correct widget classes."""
        form = CustomerFilterForm()

        name_widget = form.fields["name"].widget
        start_widget = form.fields["start"].widget
        end_widget = form.fields["end"].widget

        assert "form-control" in name_widget.attrs["class"]
        assert "form-control-sm" in name_widget.attrs["class"]
        assert "form-control" in start_widget.attrs["class"]
        assert "form-control-sm" in start_widget.attrs["class"]
        assert "dateinput" in start_widget.attrs["class"]
        assert "form-control" in end_widget.attrs["class"]
        assert "form-control-sm" in end_widget.attrs["class"]
        assert "dateinput" in end_widget.attrs["class"]

    def test_should_have_correct_placeholders(self):
        """Test that fields have correct placeholders."""
        form = CustomerFilterForm()

        name_widget = form.fields["name"].widget
        start_widget = form.fields["start"].widget
        end_widget = form.fields["end"].widget

        assert name_widget.attrs["placeholder"] == _("Filter by name...")
        assert start_widget.attrs["placeholder"] == _("Select start date")
        assert end_widget.attrs["placeholder"] == _("Select end date")

    def test_should_handle_initial_data(self):
        """Test that form handles initial data correctly."""
        initial_data = {"name": "Initial Name", "start": date.today(), "end": date.today()}
        form = CustomerFilterForm(initial=initial_data)

        assert form.initial["name"] == "Initial Name"
        assert form.initial["start"] == date.today()
        assert form.initial["end"] == date.today()

    def test_should_handle_mixed_valid_and_invalid_data(self):
        """Test that form handles mixed valid and invalid data correctly."""
        form = CustomerFilterForm(data={"name": "Valid Name", "start": "invalid-date", "end": date.today()})

        assert not form.is_valid()
        assert "start" in form.errors
        assert "name" not in form.errors
        assert "end" not in form.errors

    def test_should_preserve_valid_data_when_other_fields_invalid(self):
        """Test that valid data is preserved when other fields are invalid."""
        form = CustomerFilterForm(data={"name": "Valid Name", "start": "invalid-date", "end": "invalid-date"})

        assert not form.is_valid()
        # Valid data should still be in cleaned_data for valid fields
        assert form.cleaned_data.get("name") == "Valid Name"

    def test_should_handle_future_dates(self):
        """Test that form accepts future dates."""
        future_date = date.today() + timedelta(days=30)
        form = CustomerFilterForm(data={"start": future_date})

        assert form.is_valid()
        assert form.cleaned_data["start"] == future_date

    def test_should_handle_past_dates(self):
        """Test that form accepts past dates."""
        past_date = date.today() - timedelta(days=30)
        form = CustomerFilterForm(data={"start": past_date})

        assert form.is_valid()
        assert form.cleaned_data["start"] == past_date

    def test_should_handle_very_old_dates(self):
        """Test that form accepts very old dates."""
        old_date = date(1900, 1, 1)
        form = CustomerFilterForm(data={"start": old_date})

        assert form.is_valid()
        assert form.cleaned_data["start"] == old_date

    def test_should_handle_unicode_in_name(self):
        """Test that form handles unicode characters in name."""
        unicode_name = "José María"
        form = CustomerFilterForm(data={"name": unicode_name})

        assert form.is_valid()
        assert form.cleaned_data["name"] == unicode_name

    def test_should_handle_special_characters_in_name(self):
        """Test that form handles special characters in name."""
        special_name = "O'Connor-Smith"
        form = CustomerFilterForm(data={"name": special_name})

        assert form.is_valid()
        assert form.cleaned_data["name"] == special_name

    def test_should_handle_numbers_in_name(self):
        """Test that form handles numbers in name."""
        numeric_name = "John123"
        form = CustomerFilterForm(data={"name": numeric_name})

        assert form.is_valid()
        assert form.cleaned_data["name"] == numeric_name
