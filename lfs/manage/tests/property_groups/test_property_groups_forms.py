"""
Comprehensive unit tests for property_groups forms.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Fast tests with minimal mocking

Tests cover:
- PropertyGroupForm field validation
- Form rendering and widget attributes
- Form cleaning and data handling
- Edge cases and error conditions
"""

import pytest

from django import forms
from django.test import RequestFactory
from django.utils.translation import gettext_lazy as _

from lfs.manage.property_groups.forms import PropertyGroupForm


@pytest.fixture
def request_factory():
    """Request factory for creating mock requests."""
    return RequestFactory()


class TestPropertyGroupForm:
    """Test PropertyGroupForm functionality."""

    def test_form_has_correct_fields(self):
        """Test that form has the correct fields."""
        form = PropertyGroupForm()

        assert "name" in form.fields
        assert len(form.fields) == 1

    def test_form_field_is_char_field(self):
        """Test that form field is CharField instance."""
        form = PropertyGroupForm()

        assert isinstance(form.fields["name"], forms.CharField)

    def test_form_field_is_required(self):
        """Test that form field is required."""
        form = PropertyGroupForm()

        assert form.fields["name"].required

    def test_form_field_has_correct_max_length(self):
        """Test that form field has correct max_length."""
        form = PropertyGroupForm()

        assert form.fields["name"].max_length == 50

    def test_form_field_has_correct_blank_setting(self):
        """Test that form field has correct blank setting."""
        form = PropertyGroupForm()
        # CharField doesn't have blank attribute, but we can check if it's required
        assert form.fields["name"].required == True  # Our form makes it required

    def test_form_validation_with_valid_data(self):
        """Test form validation with valid data."""
        form_data = {"name": "Test Property Group"}
        form = PropertyGroupForm(data=form_data)

        assert form.is_valid()
        assert form.cleaned_data["name"] == "Test Property Group"

    def test_form_validation_with_empty_data(self):
        """Test form validation with empty data."""
        form_data = {}
        form = PropertyGroupForm(data=form_data)

        assert not form.is_valid()
        assert "name" in form.errors

    def test_form_validation_with_empty_string(self):
        """Test form validation with empty string."""
        form_data = {"name": ""}
        form = PropertyGroupForm(data=form_data)

        assert not form.is_valid()
        assert "name" in form.errors

    def test_form_validation_with_whitespace_string(self):
        """Test form validation with whitespace-only string."""
        form_data = {"name": "   "}
        form = PropertyGroupForm(data=form_data)

        assert not form.is_valid()
        assert "name" in form.errors

    def test_form_validation_with_none_value(self):
        """Test form validation with None value."""
        form_data = {"name": None}
        form = PropertyGroupForm(data=form_data)

        assert not form.is_valid()
        assert "name" in form.errors

    def test_form_validation_with_max_length_string(self):
        """Test form validation with maximum length string."""
        max_length = 50
        form_data = {"name": "a" * max_length}
        form = PropertyGroupForm(data=form_data)

        assert form.is_valid()
        assert form.cleaned_data["name"] == "a" * max_length

    def test_form_validation_with_exceeds_max_length_string(self):
        """Test form validation with string that exceeds maximum length."""
        max_length = 50
        form_data = {"name": "a" * (max_length + 1)}
        form = PropertyGroupForm(data=form_data)

        assert not form.is_valid()
        assert "name" in form.errors

    @pytest.mark.parametrize(
        "valid_name",
        [
            "Test Property Group",
            "Property Group 1",
            "My Group",
            "Group-Name",
            "Group_Name",
            "Group Name 123",
            "Special Characters: !@#$%^&*()",
            "Unicode: 测试组",
            "Numbers: 123456789",
            "Mixed: Test123_Group",
        ],
    )
    def test_form_validation_with_various_valid_names(self, valid_name):
        """Test form validation with various valid name formats."""
        form_data = {"name": valid_name}
        form = PropertyGroupForm(data=form_data)

        assert form.is_valid()
        assert form.cleaned_data["name"] == valid_name

    @pytest.mark.parametrize(
        "invalid_name",
        [
            "",  # Empty string
            "   ",  # Whitespace only
            "a" * 51,  # Too long
            None,  # None value
        ],
    )
    def test_form_validation_with_various_invalid_names(self, invalid_name):
        """Test form validation with various invalid name formats."""
        form_data = {"name": invalid_name}
        form = PropertyGroupForm(data=form_data)

        assert not form.is_valid()
        assert "name" in form.errors

    def test_form_initial_data_handling(self):
        """Test form initial data handling."""
        initial_data = {"name": "Initial Property Group"}
        form = PropertyGroupForm(initial=initial_data)

        assert form.initial["name"] == "Initial Property Group"

    def test_form_initial_data_with_none_value(self):
        """Test form initial data with None value."""
        initial_data = {"name": None}
        form = PropertyGroupForm(initial=initial_data)

        assert form.initial["name"] is None

    def test_form_rendering_includes_correct_html_attributes(self):
        """Test that form rendering includes correct HTML attributes."""
        form = PropertyGroupForm()

        # Test name field rendering
        name_html = str(form["name"])
        assert 'name="name"' in name_html
        assert 'type="text"' in name_html
        assert 'maxlength="50"' in name_html

    def test_form_rendering_with_data(self):
        """Test form rendering with data."""
        form_data = {"name": "Test Property Group"}
        form = PropertyGroupForm(data=form_data)

        # Form should render without errors
        name_html = str(form["name"])

        assert 'value="Test Property Group"' in name_html

    def test_form_rendering_with_errors(self):
        """Test form rendering with validation errors."""
        form_data = {"name": ""}  # Invalid empty name
        form = PropertyGroupForm(data=form_data)

        # Form should not be valid
        assert not form.is_valid()

        # Should have errors
        assert "name" in form.errors

    def test_form_field_order(self):
        """Test that form fields are in the correct order."""
        form = PropertyGroupForm()
        field_names = list(form.fields.keys())

        assert field_names == ["name"]

    def test_form_field_help_text(self):
        """Test that form fields have correct help text."""
        form = PropertyGroupForm()

        assert form.fields["name"].help_text == "Name of the property group"

    def test_form_field_error_messages(self):
        """Test that form fields have appropriate error messages."""
        form = PropertyGroupForm()

        # Test with invalid data to trigger error messages
        form_data = {"name": ""}  # Empty name
        form = PropertyGroupForm(data=form_data)

        assert not form.is_valid()
        assert "name" in form.errors
        # Error message should indicate required field
        assert any("required" in str(error).lower() for error in form.errors["name"])

    def test_form_validation_with_boundary_lengths(self):
        """Test form validation with boundary length values."""
        # Test exactly at max length
        form_data = {"name": "a" * 50}
        form = PropertyGroupForm(data=form_data)

        assert form.is_valid()
        assert form.cleaned_data["name"] == "a" * 50

        # Test one character over max length
        form_data = {"name": "a" * 51}
        form = PropertyGroupForm(data=form_data)

        assert not form.is_valid()
        assert "name" in form.errors

    def test_form_validation_with_unicode_characters(self):
        """Test form validation with unicode characters."""
        unicode_names = [
            "测试属性组",  # Chinese
            "группа свойств",  # Russian
            "groupe de propriétés",  # French
            "Gruppe von Eigenschaften",  # German
            "グループのプロパティ",  # Japanese
        ]

        for name in unicode_names:
            form_data = {"name": name}
            form = PropertyGroupForm(data=form_data)

            assert form.is_valid()
            assert form.cleaned_data["name"] == name

    def test_form_validation_with_special_characters(self):
        """Test form validation with special characters."""
        special_names = [
            "Group-Name",
            "Group_Name",
            "Group.Name",
            "Group:Name",
            "Group;Name",
            "Group,Name",
            "Group Name",
            "Group!Name",
            "Group@Name",
            "Group#Name",
            "Group$Name",
            "Group%Name",
            "Group^Name",
            "Group&Name",
            "Group*Name",
            "Group(Name)",
            "Group[Name]",
            "Group{Name}",
            "Group<Name>",
            "Group>Name",
            "Group?Name",
            "Group/Name",
            "Group\\Name",
            "Group|Name",
            "Group+Name",
            "Group=Name",
            "Group~Name",
            "Group`Name",
        ]

        for name in special_names:
            form_data = {"name": name}
            form = PropertyGroupForm(data=form_data)

            assert form.is_valid()
            assert form.cleaned_data["name"] == name

    def test_form_validation_with_leading_trailing_whitespace(self):
        """Test form validation with leading and trailing whitespace."""
        form_data = {"name": "  Test Property Group  "}
        form = PropertyGroupForm(data=form_data)

        assert form.is_valid()
        # Our form strips whitespace with strip=True
        assert form.cleaned_data["name"] == "Test Property Group"

    def test_form_validation_with_tabs_and_newlines(self):
        """Test form validation with tabs and newlines."""
        form_data = {"name": "Test\tProperty\nGroup"}
        form = PropertyGroupForm(data=form_data)

        assert form.is_valid()
        assert form.cleaned_data["name"] == "Test\tProperty\nGroup"

    def test_form_validation_with_only_numbers(self):
        """Test form validation with only numbers."""
        form_data = {"name": "123456789"}
        form = PropertyGroupForm(data=form_data)

        assert form.is_valid()
        assert form.cleaned_data["name"] == "123456789"

    def test_form_validation_with_only_special_characters(self):
        """Test form validation with only special characters."""
        form_data = {"name": "!@#$%^&*()"}
        form = PropertyGroupForm(data=form_data)

        assert form.is_valid()
        assert form.cleaned_data["name"] == "!@#$%^&*()"

    def test_form_validation_with_mixed_case(self):
        """Test form validation with mixed case."""
        form_data = {"name": "Test Property Group"}
        form = PropertyGroupForm(data=form_data)

        assert form.is_valid()
        assert form.cleaned_data["name"] == "Test Property Group"

    def test_form_validation_with_single_character(self):
        """Test form validation with single character."""
        form_data = {"name": "A"}
        form = PropertyGroupForm(data=form_data)

        assert form.is_valid()
        assert form.cleaned_data["name"] == "A"

    def test_form_validation_with_very_long_valid_name(self):
        """Test form validation with very long but valid name."""
        # Create a name that's exactly at the max length
        long_name = "A" * 50
        form_data = {"name": long_name}
        form = PropertyGroupForm(data=form_data)

        assert form.is_valid()
        assert form.cleaned_data["name"] == long_name

    def test_form_validation_with_very_long_invalid_name(self):
        """Test form validation with very long invalid name."""
        # Create a name that exceeds max length
        long_name = "A" * 51
        form_data = {"name": long_name}
        form = PropertyGroupForm(data=form_data)

        assert not form.is_valid()
        assert "name" in form.errors

    def test_form_validation_with_duplicate_names(self):
        """Test form validation with duplicate names (should be valid for form validation)."""
        # Form validation doesn't check for uniqueness - that's handled at the model level
        form_data = {"name": "Duplicate Name"}
        form = PropertyGroupForm(data=form_data)

        assert form.is_valid()
        assert form.cleaned_data["name"] == "Duplicate Name"

    def test_form_validation_with_sql_injection_attempt(self):
        """Test form validation with SQL injection attempt."""
        form_data = {"name": "'; DROP TABLE property_groups; --"}
        form = PropertyGroupForm(data=form_data)

        # Form should be valid (SQL injection protection is at the ORM level)
        assert form.is_valid()
        assert form.cleaned_data["name"] == "'; DROP TABLE property_groups; --"

    def test_form_validation_with_xss_attempt(self):
        """Test form validation with XSS attempt."""
        form_data = {"name": "<script>alert('xss')</script>"}
        form = PropertyGroupForm(data=form_data)

        # Form should be valid (XSS protection is at the template level)
        assert form.is_valid()
        assert form.cleaned_data["name"] == "<script>alert('xss')</script>"
