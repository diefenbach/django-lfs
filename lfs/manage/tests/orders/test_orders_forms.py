import pytest
from datetime import date, timedelta
from django import forms

from django.test import RequestFactory
from django.utils.translation import gettext_lazy as _

from lfs.manage.orders.forms import OrderFilterForm


@pytest.fixture
def request_factory():
    """Request factory for creating mock requests."""
    return RequestFactory()


class TestOrderFilterForm:
    """Test OrderFilterForm functionality."""

    def test_form_has_correct_fields(self):
        """Test that form has the correct fields."""
        form = OrderFilterForm()

        assert "name" in form.fields
        assert "state" in form.fields
        assert "start" in form.fields
        assert "end" in form.fields
        assert len(form.fields) == 4

    def test_form_fields_have_correct_types(self):
        """Test that form fields are the correct types."""
        form = OrderFilterForm()

        assert isinstance(form.fields["name"], forms.CharField)
        assert isinstance(form.fields["state"], forms.ChoiceField)
        assert isinstance(form.fields["start"], forms.DateField)
        assert isinstance(form.fields["end"], forms.DateField)

    def test_name_field_attributes(self):
        """Test name field has correct attributes."""
        form = OrderFilterForm()
        name_field = form.fields["name"]

        assert name_field.required is False
        assert name_field.max_length == 100
        assert "form-control form-control-sm" in name_field.widget.attrs["class"]
        assert name_field.widget.attrs["placeholder"] == _("Customer name")

    def test_state_field_attributes(self):
        """Test state field has correct attributes."""
        form = OrderFilterForm()
        state_field = form.fields["state"]

        assert state_field.required is False
        assert "form-select form-select-sm" in state_field.widget.attrs["class"]

    def test_date_fields_attributes(self):
        """Test date fields have correct attributes."""
        form = OrderFilterForm()

        for field_name in ["start", "end"]:
            field = form.fields[field_name]
            assert field.required is False
            assert "form-control form-control-sm dateinput" in field.widget.attrs["class"]

    def test_form_valid_data(self):
        """Test form validates with valid data."""
        today = date.today()
        form_data = {
            "name": "John Doe",
            "state": "1",
            "start": today.strftime("%Y-%m-%d"),
            "end": (today + timedelta(days=7)).strftime("%Y-%m-%d"),
        }

        form = OrderFilterForm(data=form_data)
        assert form.is_valid()

        assert form.cleaned_data["name"] == "John Doe"
        assert form.cleaned_data["state"] == "1"
        assert form.cleaned_data["start"] == today
        assert form.cleaned_data["end"] == today + timedelta(days=7)

    def test_form_empty_data(self):
        """Test form validates with empty data."""
        form = OrderFilterForm(data={})
        assert form.is_valid()

        assert form.cleaned_data["name"] == ""
        assert form.cleaned_data["state"] == ""
        assert form.cleaned_data["start"] is None
        assert form.cleaned_data["end"] is None

    def test_form_partial_data(self):
        """Test form validates with partial data."""
        form_data = {
            "name": "Jane Smith",
            "state": "",
        }

        form = OrderFilterForm(data=form_data)
        assert form.is_valid()

        assert form.cleaned_data["name"] == "Jane Smith"
        assert form.cleaned_data["state"] == ""
        assert form.cleaned_data["start"] is None

    def test_name_field_max_length(self):
        """Test name field enforces max length."""
        long_name = "A" * 101  # Exceeds max_length of 100
        form_data = {"name": long_name}

        form = OrderFilterForm(data=form_data)
        assert not form.is_valid()
        assert "name" in form.errors

    def test_invalid_date_format(self):
        """Test form handles invalid date formats."""
        form_data = {
            "start": "invalid-date",
            "end": "2023-13-45",  # Invalid date
        }

        form = OrderFilterForm(data=form_data)
        assert not form.is_valid()
        assert "start" in form.errors
        assert "end" in form.errors

    def test_state_field_choices(self):
        """Test state field has correct choices."""
        form = OrderFilterForm()
        state_field = form.fields["state"]

        # Should have empty choice plus order states
        choices = list(state_field.choices)
        assert choices[0] == ("", _("All States"))

        # Should have additional state choices (exact count depends on ORDER_STATES)
        assert len(choices) > 1

    def test_form_with_initial_data(self):
        """Test form initializes correctly with initial data."""
        today = date.today()
        initial_data = {
            "name": "Initial Name",
            "state": "2",
            "start": today,
            "end": today + timedelta(days=30),
        }

        form = OrderFilterForm(initial=initial_data)

        assert form.initial["name"] == "Initial Name"
        assert form.initial["state"] == "2"
        assert form.initial["start"] == today
        assert form.initial["end"] == today + timedelta(days=30)

    def test_form_field_labels(self):
        """Test form fields have correct labels."""
        form = OrderFilterForm()

        assert form.fields["name"].label == _("Customer Name")
        assert form.fields["state"].label == _("Order State")
        assert form.fields["start"].label == _("Start Date")
        assert form.fields["end"].label == _("End Date")

    def test_form_field_help_texts(self):
        """Test form fields have appropriate help texts."""
        form = OrderFilterForm()

        # Most fields have empty string as help text by default
        assert form.fields["name"].help_text == ""
        assert form.fields["state"].help_text == ""
        assert form.fields["start"].help_text == ""
        assert form.fields["end"].help_text == ""

    def test_form_validation_edge_cases(self):
        """Test form validation with edge cases."""
        # Test with whitespace in name - CharField strips whitespace by default
        form_data = {"name": "   John Doe   "}
        form = OrderFilterForm(data=form_data)
        assert form.is_valid()
        assert form.cleaned_data["name"] == "John Doe"  # Whitespace is stripped by CharField

    def test_form_with_request_data(self, request_factory):
        """Test form handling with request data."""
        request = request_factory.post(
            "/",
            {
                "name": "Posted Name",
                "state": "1",
            },
        )

        form = OrderFilterForm(data=request.POST)
        assert form.is_valid()
        assert form.cleaned_data["name"] == "Posted Name"
        assert form.cleaned_data["state"] == "1"

    def test_form_field_order(self):
        """Test form fields are in expected order."""
        form = OrderFilterForm()
        field_names = list(form.fields.keys())

        expected_order = ["name", "state", "start", "end"]
        assert field_names == expected_order

    def test_form_as_table_rendering(self):
        """Test form can be rendered as table."""
        form = OrderFilterForm()
        table_html = form.as_table()

        assert isinstance(table_html, str)
        assert "<tr>" in table_html or "<td>" in table_html

    def test_form_as_p_rendering(self):
        """Test form can be rendered as paragraphs."""
        form = OrderFilterForm()
        p_html = form.as_p()

        assert isinstance(p_html, str)
        assert "<p>" in p_html

    def test_form_as_ul_rendering(self):
        """Test form can be rendered as list."""
        form = OrderFilterForm()
        ul_html = form.as_ul()

        assert isinstance(ul_html, str)
        assert "<li>" in ul_html
