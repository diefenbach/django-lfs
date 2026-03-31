from django.contrib.auth import get_user_model

from lfs.customer_tax.models import CustomerTax
from lfs.manage.customer_taxes.views import (
    ManageCustomerTaxesView,
    NoCustomerTaxesView,
    CustomerTaxDataView,
    CustomerTaxCriteriaView,
    CustomerTaxCreateView,
    CustomerTaxDeleteConfirmView,
    CustomerTaxDeleteView,
    CustomerTaxTabMixin,
)

User = get_user_model()


class TestManageCustomerTaxesView:
    """Test the ManageCustomerTaxesView dispatcher."""

    def test_view_inheritance(self):
        """Should inherit from Django RedirectView."""
        from django.views.generic.base import RedirectView

        assert issubclass(ManageCustomerTaxesView, RedirectView)

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ManageCustomerTaxesView.permission_required == "core.manage_shop"

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


class TestNoCustomerTaxesView:
    """Test the NoCustomerTaxesView template view."""

    def test_view_inheritance(self):
        """Should inherit from Django TemplateView."""
        from django.views.generic.base import TemplateView

        assert issubclass(NoCustomerTaxesView, TemplateView)

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert NoCustomerTaxesView.permission_required == "core.manage_shop"

    def test_template_name(self):
        """Should use correct template."""
        assert NoCustomerTaxesView.template_name == "manage/customer_taxes/no_customer_taxes.html"


class TestCustomerTaxDataView:
    """Test the CustomerTaxDataView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from Django UpdateView."""
        from django.views.generic.edit import UpdateView

        assert issubclass(CustomerTaxDataView, UpdateView)

    def test_model_attribute(self):
        """Should use CustomerTax model."""
        assert CustomerTaxDataView.model == CustomerTax

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert CustomerTaxDataView.permission_required == "core.manage_shop"

    def test_form_class(self):
        """Should use CustomerTaxForm."""
        from lfs.manage.customer_taxes.forms import CustomerTaxForm

        assert CustomerTaxDataView.form_class == CustomerTaxForm

    def test_tab_name(self):
        """Should have correct tab name."""
        assert CustomerTaxDataView.tab_name == "data"

    def test_pk_url_kwarg(self):
        """Should use correct URL kwarg."""
        assert CustomerTaxDataView.pk_url_kwarg == "id"

    def test_get_success_url_method_exists(self):
        """Should have get_success_url method."""
        assert hasattr(CustomerTaxDataView, "get_success_url")
        assert callable(getattr(CustomerTaxDataView, "get_success_url"))

    def test_form_valid_method_exists(self):
        """Should have form_valid method."""
        assert hasattr(CustomerTaxDataView, "form_valid")
        assert callable(getattr(CustomerTaxDataView, "form_valid"))


class TestCustomerTaxCriteriaView:
    """Test the CustomerTaxCriteriaView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from Django TemplateView."""
        from django.views.generic.base import TemplateView

        assert issubclass(CustomerTaxCriteriaView, TemplateView)

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert CustomerTaxCriteriaView.permission_required == "core.manage_shop"

    def test_tab_name(self):
        """Should have correct tab name."""
        assert CustomerTaxCriteriaView.tab_name == "criteria"

    def test_template_name(self):
        """Should use correct template."""
        assert CustomerTaxCriteriaView.template_name == "manage/customer_taxes/customer_tax.html"

    def test_get_success_url_method_exists(self):
        """Should have get_success_url method."""
        assert hasattr(CustomerTaxCriteriaView, "get_success_url")
        assert callable(getattr(CustomerTaxCriteriaView, "get_success_url"))

    def test_post_method_exists(self):
        """Should have post method."""
        assert hasattr(CustomerTaxCriteriaView, "post")
        assert callable(getattr(CustomerTaxCriteriaView, "post"))


class TestCustomerTaxCreateView:
    """Test the CustomerTaxCreateView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from Django CreateView."""
        from django.views.generic.edit import CreateView

        assert issubclass(CustomerTaxCreateView, CreateView)

    def test_model_attribute(self):
        """Should use CustomerTax model."""
        assert CustomerTaxCreateView.model == CustomerTax

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert CustomerTaxCreateView.permission_required == "core.manage_shop"

    def test_form_class(self):
        """Should use CustomerTaxForm."""
        from lfs.manage.customer_taxes.forms import CustomerTaxForm

        assert CustomerTaxCreateView.form_class == CustomerTaxForm

    def test_template_name(self):
        """Should use correct template."""
        assert CustomerTaxCreateView.template_name == "manage/customer_taxes/add_customer_tax.html"

    def test_form_valid_method_exists(self):
        """Should have form_valid method."""
        assert hasattr(CustomerTaxCreateView, "form_valid")
        assert callable(getattr(CustomerTaxCreateView, "form_valid"))

    def test_get_success_url_method_exists(self):
        """Should have get_success_url method."""
        assert hasattr(CustomerTaxCreateView, "get_success_url")
        assert callable(getattr(CustomerTaxCreateView, "get_success_url"))


class TestCustomerTaxDeleteConfirmView:
    """Test the CustomerTaxDeleteConfirmView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from Django TemplateView."""
        from django.views.generic.base import TemplateView

        assert issubclass(CustomerTaxDeleteConfirmView, TemplateView)

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert CustomerTaxDeleteConfirmView.permission_required == "core.manage_shop"

    def test_template_name(self):
        """Should use correct template."""
        assert CustomerTaxDeleteConfirmView.template_name == "manage/customer_taxes/delete_customer_tax.html"

    def test_get_context_data_method_exists(self):
        """Should have get_context_data method."""
        assert hasattr(CustomerTaxDeleteConfirmView, "get_context_data")
        assert callable(getattr(CustomerTaxDeleteConfirmView, "get_context_data"))


class TestCustomerTaxDeleteView:
    """Test the CustomerTaxDeleteView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from Django DeleteView."""
        from django.views.generic.edit import DeleteView

        assert issubclass(CustomerTaxDeleteView, DeleteView)

    def test_model_attribute(self):
        """Should use CustomerTax model."""
        assert CustomerTaxDeleteView.model == CustomerTax

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert CustomerTaxDeleteView.permission_required == "core.manage_shop"

    def test_pk_url_kwarg(self):
        """Should use correct URL kwarg."""
        assert CustomerTaxDeleteView.pk_url_kwarg == "id"

    def test_success_message(self):
        """Should have success message."""
        assert CustomerTaxDeleteView.success_message == "Customer tax has been deleted."

    def test_get_success_url_method_exists(self):
        """Should have get_success_url method."""
        assert hasattr(CustomerTaxDeleteView, "get_success_url")
        assert callable(getattr(CustomerTaxDeleteView, "get_success_url"))


class TestCustomerTaxTabMixin:
    """Test the CustomerTaxTabMixin functionality."""

    def test_mixin_has_template_name(self):
        """Should have template_name attribute."""
        assert hasattr(CustomerTaxTabMixin, "template_name")
        assert CustomerTaxTabMixin.template_name == "manage/customer_taxes/customer_tax.html"

    def test_mixin_has_tab_name(self):
        """Should have tab_name attribute."""
        assert hasattr(CustomerTaxTabMixin, "tab_name")

    def test_get_customer_tax_method_exists(self):
        """Should have get_customer_tax method."""
        assert hasattr(CustomerTaxTabMixin, "get_customer_tax")
        assert callable(getattr(CustomerTaxTabMixin, "get_customer_tax"))

    def test_get_customer_taxes_queryset_method_exists(self):
        """Should have get_customer_taxes_queryset method."""
        assert hasattr(CustomerTaxTabMixin, "get_customer_taxes_queryset")
        assert callable(getattr(CustomerTaxTabMixin, "get_customer_taxes_queryset"))

    def test_get_context_data_method_exists(self):
        """Should have get_context_data method."""
        assert hasattr(CustomerTaxTabMixin, "get_context_data")
        assert callable(getattr(CustomerTaxTabMixin, "get_context_data"))

    def test_get_tabs_method_exists(self):
        """Should have _get_tabs method."""
        assert hasattr(CustomerTaxTabMixin, "_get_tabs")
        assert callable(getattr(CustomerTaxTabMixin, "_get_tabs"))

    def test_get_navigation_context_method_exists(self):
        """Should have _get_navigation_context method."""
        assert hasattr(CustomerTaxTabMixin, "_get_navigation_context")
        assert callable(getattr(CustomerTaxTabMixin, "_get_navigation_context"))
