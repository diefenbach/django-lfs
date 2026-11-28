from django.contrib.auth import get_user_model

from lfs.customer_tax.models import CustomerTax
from lfs.manage.customer_taxes.views import (
    ManageCustomerTaxesView,
    CustomerTaxTabMixin,
)

User = get_user_model()


class TestManageCustomerTaxesView:
    """Test the ManageCustomerTaxesView dispatcher."""


    def test_redirects_to_first_tax_when_taxes_exist(self, mock_request, customer_tax, monkeypatch):
        """Should redirect to first tax when taxes exist."""

        def mock_reverse(view_name, kwargs=None):
            if view_name == "lfs_manage_customer_tax" and kwargs and kwargs.get("id") == customer_tax.id:
                return f"/manage/customer-tax/{customer_tax.id}/"
            return f"/mock-url/{view_name}/"

        monkeypatch.setattr("lfs.manage.customer_taxes.views.reverse", mock_reverse)

        view = ManageCustomerTaxesView()
        view.request = mock_request
        response = view.get_redirect_url()

        assert f"/manage/customer-tax/{customer_tax.id}/" == response

    def test_redirects_to_no_taxes_when_none_exist(self, mock_request, monkeypatch):
        """Should redirect to no taxes view when no taxes exist."""
        # Delete all taxes
        CustomerTax.objects.all().delete()

        def mock_reverse(view_name, kwargs=None):
            if view_name == "lfs_manage_no_customer_taxes":
                return "/manage/customer-taxes/no"
            return f"/mock-url/{view_name}/"

        monkeypatch.setattr("lfs.manage.customer_taxes.views.reverse", mock_reverse)

        view = ManageCustomerTaxesView()
        view.request = mock_request
        response = view.get_redirect_url()

        assert response == "/manage/customer-taxes/no"








class TestCustomerTaxTabMixin:
    """Test the CustomerTaxTabMixin functionality."""

    def test_mixin_has_template_name(self):
        """Should have template_name attribute."""
        assert hasattr(CustomerTaxTabMixin, "template_name")
        assert CustomerTaxTabMixin.template_name == "manage/customer_taxes/customer_tax.html"






