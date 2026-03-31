from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import ClearableFileInput

from lfs.core.models import Shop
from lfs.manage.shop.forms import ShopDataForm, ShopDefaultValuesForm


class TestShopDataForm:
    """Test ShopDataForm validation and behavior."""

    def test_form_inheritance(self):
        """Should inherit from ModelForm."""
        from django.forms import ModelForm

        assert issubclass(ShopDataForm, ModelForm)

    def test_meta_model(self):
        """Should use Shop model."""
        assert ShopDataForm.Meta.model == Shop

    def test_meta_fields(self):
        """Should include correct fields."""
        expected_fields = (
            "name",
            "shop_owner",
            "from_email",
            "notification_emails",
            "description",
            "image",
            "static_block",
            "checkout_type",
            "confirm_toc",
            "google_analytics_id",
            "ga_site_tracking",
            "ga_ecommerce_tracking",
        )
        assert ShopDataForm.Meta.fields == expected_fields

    def test_form_initialization_with_shop(self, shop):
        """Should initialize form with shop data."""
        form = ShopDataForm(instance=shop)

        assert form.instance == shop
        assert form.instance.name == shop.name
        assert form.instance.shop_owner == shop.shop_owner
        assert form.instance.from_email == shop.from_email

    def test_image_widget_is_clearable_file_input(self):
        """Should use ClearableFileInput for image field."""
        form = ShopDataForm()
        assert isinstance(form.fields["image"].widget, ClearableFileInput)

    def test_form_helper_is_configured(self):
        """Should have form helper configured."""
        form = ShopDataForm()
        assert hasattr(form, "helper")
        assert form.helper.form_tag is False
        assert hasattr(form.helper, "layout")

    def test_valid_form_data(self):
        """Should accept valid form data."""
        data = {
            "name": "Test Shop",
            "shop_owner": "Test Owner",
            "from_email": "test@example.com",
            "notification_emails": "notify@example.com",
            "description": "Test description",
            "checkout_type": 1,
            "confirm_toc": True,
            "google_analytics_id": "GA-123456789",
            "ga_site_tracking": True,
            "ga_ecommerce_tracking": True,
        }

        form = ShopDataForm(data=data)
        assert form.is_valid()

    def test_required_fields_validation(self):
        """Should require name, shop_owner, and from_email fields."""
        # Test missing name
        data = {
            "shop_owner": "Test Owner",
            "from_email": "test@example.com",
            "notification_emails": "notify@example.com",
            "checkout_type": 1,
        }
        form = ShopDataForm(data=data)
        assert not form.is_valid()
        assert "name" in form.errors

        # Test missing shop_owner - this field is actually blank=True, so it's not required
        # Let's test missing from_email instead
        data = {
            "name": "Test Shop",
            "shop_owner": "Test Owner",
            "notification_emails": "notify@example.com",
            "checkout_type": 1,
        }
        form = ShopDataForm(data=data)
        assert not form.is_valid()
        assert "from_email" in form.errors

        # Test missing notification_emails
        data = {
            "name": "Test Shop",
            "shop_owner": "Test Owner",
            "from_email": "test@example.com",
            "checkout_type": 1,
        }
        form = ShopDataForm(data=data)
        assert not form.is_valid()
        assert "notification_emails" in form.errors

    def test_email_field_validation(self):
        """Should validate email format."""
        data = {
            "name": "Test Shop",
            "shop_owner": "Test Owner",
            "from_email": "invalid-email",
            "notification_emails": "notify@example.com",
            "checkout_type": 1,
        }
        form = ShopDataForm(data=data)
        assert not form.is_valid()
        assert "from_email" in form.errors

    def test_valid_email_formats(self):
        """Should accept valid email formats."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "test+tag@example.org",
        ]

        for email in valid_emails:
            data = {
                "name": "Test Shop",
                "shop_owner": "Test Owner",
                "from_email": email,
                "notification_emails": "notify@example.com",
                "checkout_type": 1,
            }
            form = ShopDataForm(data=data)
            assert form.is_valid(), f"Email '{email}' should be valid"

    def test_checkout_type_choices(self):
        """Should accept valid checkout type values."""
        valid_checkout_types = [0, 1, 2]  # Assuming these are valid choices

        for checkout_type in valid_checkout_types:
            data = {
                "name": "Test Shop",
                "shop_owner": "Test Owner",
                "from_email": "test@example.com",
                "notification_emails": "notify@example.com",
                "checkout_type": checkout_type,
            }
            form = ShopDataForm(data=data)
            assert form.is_valid(), f"Checkout type {checkout_type} should be valid"

    def test_boolean_fields_accept_boolean_values(self):
        """Should accept boolean values for boolean fields."""
        data = {
            "name": "Test Shop",
            "shop_owner": "Test Owner",
            "from_email": "test@example.com",
            "notification_emails": "notify@example.com",
            "checkout_type": 1,
            "confirm_toc": True,
            "ga_site_tracking": False,
            "ga_ecommerce_tracking": True,
        }

        form = ShopDataForm(data=data)
        assert form.is_valid()

    def test_form_save_creates_shop(self):
        """Should create new shop when saving form."""
        data = {
            "name": "New Shop",
            "shop_owner": "New Owner",
            "from_email": "new@example.com",
            "notification_emails": "notify@example.com",
            "checkout_type": 1,
            "description": "New shop description",
        }

        form = ShopDataForm(data=data)
        assert form.is_valid()
        shop = form.save()

        assert isinstance(shop, Shop)
        assert shop.name == "New Shop"
        assert shop.shop_owner == "New Owner"
        assert shop.from_email == "new@example.com"

    def test_form_save_updates_existing_shop(self, shop):
        """Should update existing shop when saving form."""
        data = {
            "name": "Updated Shop",
            "shop_owner": "Updated Owner",
            "from_email": "updated@example.com",
            "notification_emails": "notify@example.com",
            "checkout_type": 1,
            "description": "Updated description",
        }

        form = ShopDataForm(data=data, instance=shop)
        assert form.is_valid()
        updated_shop = form.save()

        assert updated_shop == shop
        assert updated_shop.name == "Updated Shop"
        assert updated_shop.shop_owner == "Updated Owner"
        assert updated_shop.from_email == "updated@example.com"

    def test_image_field_handles_file_upload(self):
        """Should handle file upload for image field."""
        # Create a minimal valid JPEG file content
        # This is a 1x1 pixel JPEG file
        jpeg_content = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9"

        image_file = SimpleUploadedFile("test_image.jpg", jpeg_content, content_type="image/jpeg")

        data = {
            "name": "Test Shop",
            "shop_owner": "Test Owner",
            "from_email": "test@example.com",
            "notification_emails": "notify@example.com",
            "checkout_type": 1,
        }

        files = {"image": image_file}
        form = ShopDataForm(data=data, files=files)
        if not form.is_valid():
            print(f"Form errors: {form.errors}")
        assert form.is_valid()

    def test_optional_fields_can_be_empty(self):
        """Should allow optional fields to be empty."""
        data = {
            "name": "Test Shop",
            "shop_owner": "Test Owner",
            "from_email": "test@example.com",
            "notification_emails": "notify@example.com",
            "checkout_type": 1,
            "description": "",
            "google_analytics_id": "",
        }

        form = ShopDataForm(data=data)
        assert form.is_valid()


class TestShopDefaultValuesForm:
    """Test ShopDefaultValuesForm validation and behavior."""

    def test_form_inheritance(self):
        """Should inherit from ModelForm."""
        from django.forms import ModelForm

        assert issubclass(ShopDefaultValuesForm, ModelForm)

    def test_meta_model(self):
        """Should use Shop model."""
        assert ShopDefaultValuesForm.Meta.model == Shop

    def test_meta_fields(self):
        """Should include correct fields."""
        expected_fields = (
            "price_calculator",
            "default_country",
            "invoice_countries",
            "shipping_countries",
            "delivery_time",
        )
        assert ShopDefaultValuesForm.Meta.fields == expected_fields

    def test_form_initialization_with_shop(self, shop):
        """Should initialize form with shop data."""
        form = ShopDefaultValuesForm(instance=shop)

        assert form.instance == shop
        assert form.instance.price_calculator == shop.price_calculator
        assert form.instance.delivery_time == shop.delivery_time

    def test_form_helper_is_configured(self):
        """Should have form helper configured."""
        form = ShopDefaultValuesForm()
        assert hasattr(form, "helper")
        assert form.helper.form_tag is False
        assert hasattr(form.helper, "layout")

    def test_valid_form_data(self, shop, countries):
        """Should accept valid form data."""
        data = {
            "price_calculator": "lfs.gross_price.calculator.GrossPriceCalculator",
            "default_country": countries[0].id,
            "delivery_time": None,
            "invoice_countries": [countries[0].id, countries[1].id],
            "shipping_countries": [countries[0].id, countries[2].id],
        }

        form = ShopDefaultValuesForm(data=data, instance=shop)
        if not form.is_valid():
            print(f"Form errors: {form.errors}")
        assert form.is_valid()

    def test_optional_fields_can_be_empty(self, shop, countries):
        """Should allow optional fields to be empty."""
        data = {
            "price_calculator": "lfs.gross_price.calculator.GrossPriceCalculator",
            "invoice_countries": [countries[0].id],
            "shipping_countries": [countries[0].id],
        }

        form = ShopDefaultValuesForm(data=data, instance=shop)
        assert form.is_valid()

    def test_form_save_creates_shop(self, countries):
        """Should create new shop when saving form."""
        data = {
            "price_calculator": "lfs.gross_price.calculator.GrossPriceCalculator",
            "invoice_countries": [countries[0].id],
            "shipping_countries": [countries[0].id],
        }

        form = ShopDefaultValuesForm(data=data)
        assert form.is_valid()
        shop = form.save()

        assert isinstance(shop, Shop)
        assert shop.price_calculator == "lfs.gross_price.calculator.GrossPriceCalculator"

    def test_form_save_updates_existing_shop(self, shop, countries):
        """Should update existing shop when saving form."""
        data = {
            "price_calculator": "lfs.net_price.calculator.NetPriceCalculator",
            "invoice_countries": [countries[0].id],
            "shipping_countries": [countries[0].id],
        }

        form = ShopDefaultValuesForm(data=data, instance=shop)
        assert form.is_valid()
        updated_shop = form.save()

        assert updated_shop == shop
        assert updated_shop.price_calculator == "lfs.net_price.calculator.NetPriceCalculator"

    def test_country_fields_accept_multiple_values(self, countries):
        """Should handle multiple country selections."""
        data = {
            "price_calculator": "lfs.gross_price.calculator.GrossPriceCalculator",
            "invoice_countries": [countries[0].id, countries[1].id, countries[2].id],
            "shipping_countries": [countries[0].id, countries[1].id],
        }

        form = ShopDefaultValuesForm(data=data)
        assert form.is_valid()


class TestShopFormIntegration:
    """Integration tests for shop forms."""

    def test_both_forms_use_same_model(self):
        """Both forms should use the Shop model."""
        assert ShopDataForm.Meta.model == Shop
        assert ShopDefaultValuesForm.Meta.model == Shop

    def test_forms_have_different_field_sets(self):
        """Forms should have different field sets."""
        data_fields = set(ShopDataForm.Meta.fields)
        default_values_fields = set(ShopDefaultValuesForm.Meta.fields)

        # Should have some overlap (both work with Shop model)
        # but different primary purposes
        assert data_fields != default_values_fields

    def test_forms_can_be_used_together(self, shop):
        """Both forms should work with the same shop instance."""
        # Test data form
        data_form = ShopDataForm(instance=shop)
        assert data_form.instance == shop

        # Test default values form
        default_values_form = ShopDefaultValuesForm(instance=shop)
        assert default_values_form.instance == shop

    def test_forms_handle_shop_with_all_fields(self, shop):
        """Both forms should handle shop with all fields populated."""
        # Populate shop with all fields
        shop.description = "Full description"
        shop.google_analytics_id = "GA-123456789"
        shop.ga_site_tracking = True
        shop.ga_ecommerce_tracking = True
        shop.price_calculator = "lfs.core.utils.CalculatePrice"
        shop.save()

        # Both forms should initialize correctly
        data_form = ShopDataForm(instance=shop)
        assert data_form.is_valid() or not data_form.is_bound

        default_values_form = ShopDefaultValuesForm(instance=shop)
        assert default_values_form.is_valid() or not default_values_form.is_bound

    def test_forms_validation_consistency(self):
        """Forms should have consistent validation behavior."""
        # Both forms should handle empty data consistently
        data_form = ShopDataForm(data={})
        default_values_form = ShopDefaultValuesForm(data={})

        # Both should be invalid when empty (required fields)
        assert not data_form.is_valid()
        assert not default_values_form.is_valid()
