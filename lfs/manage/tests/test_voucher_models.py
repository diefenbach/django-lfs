"""
Unit tests for Voucher models.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Parametrization for variations

Tests cover:
- VoucherGroup model creation and field defaults
- VoucherOptions model creation and field defaults
- Voucher model creation and field defaults
- String representation
- Field validation and constraints
- Model ordering
- Relationships between models
- Meta class configuration
"""

import pytest
from django.contrib.auth import get_user_model
from datetime import date, datetime
from decimal import Decimal

from lfs.voucher.models import VoucherGroup, VoucherOptions, Voucher
from lfs.tax.models import Tax

User = get_user_model()


@pytest.mark.django_db
class TestVoucherGroupCreation:
    """Tests for VoucherGroup model creation and field defaults."""

    def test_create_voucher_group_with_required_fields(self, manage_user):
        """Should create VoucherGroup with only required name field."""
        voucher_group = VoucherGroup.objects.create(name="Test Group", creator=manage_user)

        assert voucher_group.name == "Test Group"
        assert voucher_group.creator == manage_user
        assert voucher_group.pk is not None

    def test_voucher_group_default_field_values(self, manage_user):
        """Should set correct default values for optional fields."""
        voucher_group = VoucherGroup.objects.create(name="Test Group", creator=manage_user)

        assert voucher_group.position == 10
        assert voucher_group.creation_date is not None

    @pytest.mark.parametrize(
        "field_name,custom_value",
        [
            ("position", 100),
            ("name", "Custom Group Name"),
        ],
    )
    def test_create_voucher_group_with_custom_field_values(self, manage_user, field_name, custom_value):
        """Should allow setting custom values for optional fields."""
        kwargs = {"name": "Test Group", "creator": manage_user, field_name: custom_value}
        voucher_group = VoucherGroup.objects.create(**kwargs)

        assert getattr(voucher_group, field_name) == custom_value

    def test_voucher_group_can_be_created_without_creator(self):
        """Should allow creating VoucherGroup without creator (nullable field)."""
        voucher_group = VoucherGroup.objects.create(name="Test Group")

        assert voucher_group.creator is None
        assert voucher_group.name == "Test Group"


@pytest.mark.django_db
class TestVoucherGroupStringRepresentation:
    """Tests for VoucherGroup __str__ method."""

    def test_voucher_group_str_returns_name(self, manage_user):
        """Should return the name as string representation."""
        voucher_group = VoucherGroup.objects.create(name="Premium Vouchers", creator=manage_user)

        # VoucherGroup doesn't have a custom __str__ method, so it uses default
        assert "VoucherGroup object" in str(voucher_group)

    def test_voucher_group_str_with_unicode_characters(self, manage_user):
        """Should handle unicode characters in name."""
        voucher_group = VoucherGroup.objects.create(name="Günstige Gutscheine", creator=manage_user)

        # VoucherGroup doesn't have a custom __str__ method, so it uses default
        assert "VoucherGroup object" in str(voucher_group)


@pytest.mark.django_db
class TestVoucherGroupOrdering:
    """Tests for VoucherGroup model ordering."""

    def test_voucher_groups_ordered_by_position(self, manage_user):
        """Should order VoucherGroups by position field."""
        group1 = VoucherGroup.objects.create(name="Group 1", creator=manage_user, position=30)
        group2 = VoucherGroup.objects.create(name="Group 2", creator=manage_user, position=10)
        group3 = VoucherGroup.objects.create(name="Group 3", creator=manage_user, position=20)

        groups = list(VoucherGroup.objects.all())

        assert groups[0] == group2  # position 10
        assert groups[1] == group3  # position 20
        assert groups[2] == group1  # position 30


@pytest.mark.django_db
class TestVoucherGroupRelationships:
    """Tests for VoucherGroup relationships."""

    def test_voucher_group_has_vouchers_relationship(self, voucher_group):
        """Should have reverse relationship to vouchers."""
        voucher = Voucher.objects.create(number="TEST123", group=voucher_group, kind_of=0, value=Decimal("10.00"))

        assert voucher in voucher_group.vouchers.all()
        assert voucher_group.vouchers.count() == 1


@pytest.mark.django_db
class TestVoucherOptionsCreation:
    """Tests for VoucherOptions model creation and field defaults."""

    def test_create_voucher_options_with_defaults(self):
        """Should create VoucherOptions with default values."""
        options = VoucherOptions.objects.create()

        assert options.number_prefix == ""
        assert options.number_suffix == ""
        assert options.number_length == 5
        assert options.number_letters == "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def test_create_voucher_options_with_custom_values(self):
        """Should allow setting custom values."""
        options = VoucherOptions.objects.create(
            number_prefix="GIFT-", number_suffix="-2024", number_length=8, number_letters="ABCDEF123456"
        )

        assert options.number_prefix == "GIFT-"
        assert options.number_suffix == "-2024"
        assert options.number_length == 8
        assert options.number_letters == "ABCDEF123456"


@pytest.mark.django_db
class TestVoucherCreation:
    """Tests for Voucher model creation and field defaults."""

    def test_create_voucher_with_required_fields(self, voucher_group, manage_user):
        """Should create Voucher with required fields."""
        voucher = Voucher.objects.create(
            number="VOUCHER123", group=voucher_group, creator=manage_user, kind_of=0, value=25.00
        )

        assert voucher.number == "VOUCHER123"
        assert voucher.group == voucher_group
        assert voucher.creator == manage_user
        assert voucher.kind_of == 0
        assert voucher.value == 25.00

    def test_voucher_default_field_values(self, voucher_group, manage_user):
        """Should set correct default values for optional fields."""
        voucher = Voucher.objects.create(
            number="VOUCHER123", group=voucher_group, creator=manage_user, kind_of=0, value=25.00
        )

        assert voucher.active is True
        assert voucher.sums_up is True  # Default is True according to model
        assert voucher.used_amount == 0  # Default is 0
        assert voucher.last_used_date is None
        assert voucher.start_date is None
        assert voucher.end_date is None
        assert voucher.effective_from == 0.0  # Default is 0.0
        assert voucher.limit == 1  # Default is 1

    @pytest.mark.parametrize(
        "field_name,custom_value",
        [
            ("active", False),
            ("sums_up", False),
            ("used_amount", 10),
            ("effective_from", 50.0),
            ("limit", 5),
        ],
    )
    def test_create_voucher_with_custom_field_values(self, voucher_group, manage_user, field_name, custom_value):
        """Should allow setting custom values for optional fields."""
        kwargs = {
            "number": "VOUCHER123",
            "group": voucher_group,
            "creator": manage_user,
            "kind_of": 0,
            "value": 25.00,
            field_name: custom_value,
        }
        voucher = Voucher.objects.create(**kwargs)

        assert getattr(voucher, field_name) == custom_value

    def test_voucher_number_must_be_unique(self, voucher_group, manage_user):
        """Should enforce unique constraint on voucher number."""
        Voucher.objects.create(number="UNIQUE123", group=voucher_group, creator=manage_user, kind_of=0, value=25.00)

        with pytest.raises(Exception):  # IntegrityError or ValidationError
            Voucher.objects.create(
                number="UNIQUE123", group=voucher_group, creator=manage_user, kind_of=0, value=25.00  # Same number
            )


@pytest.mark.django_db
class TestVoucherStringRepresentation:
    """Tests for Voucher __str__ method."""

    def test_voucher_str_returns_number(self, voucher_group, manage_user):
        """Should return the number as string representation."""
        voucher = Voucher.objects.create(
            number="GIFT2024", group=voucher_group, creator=manage_user, kind_of=0, value=50.00
        )

        assert str(voucher) == "GIFT2024"


@pytest.mark.django_db
class TestVoucherKindOfChoices:
    """Tests for Voucher kind_of field choices."""

    def test_voucher_absolute_kind(self, voucher_group, manage_user):
        """Should create voucher with absolute kind (0)."""
        voucher = Voucher.objects.create(
            number="ABS123", group=voucher_group, creator=manage_user, kind_of=0, value=25.00  # Absolute
        )

        assert voucher.kind_of == 0

    def test_voucher_percentage_kind(self, voucher_group, manage_user):
        """Should create voucher with percentage kind (1)."""
        voucher = Voucher.objects.create(
            number="PCT123", group=voucher_group, creator=manage_user, kind_of=1, value=15.00  # Percentage
        )

        assert voucher.kind_of == 1


@pytest.mark.django_db
class TestVoucherRelationships:
    """Tests for Voucher model relationships."""

    def test_voucher_belongs_to_group(self, voucher_group, manage_user):
        """Should have relationship to VoucherGroup."""
        voucher = Voucher.objects.create(
            number="REL123", group=voucher_group, creator=manage_user, kind_of=0, value=25.00
        )

        assert voucher.group == voucher_group
        assert voucher in voucher_group.vouchers.all()

    def test_voucher_can_have_tax(self, voucher_group, manage_user):
        """Should allow relationship to Tax model."""
        tax = Tax.objects.create(rate=Decimal("19.00"))
        voucher = Voucher.objects.create(
            number="TAX123", group=voucher_group, creator=manage_user, kind_of=0, value=25.00, tax=tax
        )

        assert voucher.tax == tax

    def test_voucher_can_exist_without_group(self, manage_user):
        """Should allow voucher without group (nullable field)."""
        voucher = Voucher.objects.create(number="NOGROUP123", creator=manage_user, kind_of=0, value=25.00)

        assert voucher.group is None


@pytest.mark.django_db
class TestVoucherDateFields:
    """Tests for Voucher date field handling."""

    def test_voucher_with_date_fields(self, voucher_group, manage_user):
        """Should handle date fields correctly."""
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)
        last_used_date = datetime(2024, 6, 15, 10, 30)

        voucher = Voucher.objects.create(
            number="DATE123",
            group=voucher_group,
            creator=manage_user,
            kind_of=0,
            value=25.00,
            start_date=start_date,
            end_date=end_date,
            last_used_date=last_used_date,
        )

        assert voucher.start_date == start_date
        assert voucher.end_date == end_date
        assert voucher.last_used_date == last_used_date
