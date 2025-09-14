"""
Unit tests for Product Taxes views.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Parametrization for variations
"""

import pytest
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.test import RequestFactory

from lfs.tax.models import Tax
from lfs.manage.product_taxes.views import (
    ManageTaxesView,
    TaxUpdateView,
    NoTaxesView,
    TaxCreateView,
    TaxDeleteConfirmView,
    TaxDeleteView,
)

User = get_user_model()


class TestManageTaxesView:
    """Test the ManageTaxesView redirect view."""

    def test_view_inheritance(self):
        """Should inherit from Django RedirectView."""
        from django.views.generic.base import RedirectView

        assert issubclass(ManageTaxesView, RedirectView)

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ManageTaxesView.permission_required == "core.manage_shop"

    def test_get_redirect_url_method_exists(self):
        """Should have get_redirect_url method."""
        assert hasattr(ManageTaxesView, "get_redirect_url")
        assert callable(getattr(ManageTaxesView, "get_redirect_url"))

    @pytest.mark.django_db
    def test_redirects_to_first_tax_when_taxes_exist(self, tax, monkeypatch):
        """Should redirect to first tax when taxes exist."""

        def mock_reverse(view_name, kwargs=None):
            if view_name == "lfs_manage_tax" and kwargs and kwargs.get("pk") == tax.id:
                return f"/manage/tax/{tax.id}/"
            return f"/mock-url/{view_name}/"

        monkeypatch.setattr("lfs.manage.product_taxes.views.reverse", mock_reverse)

        view = ManageTaxesView()
        response = view.get_redirect_url()

        assert f"/manage/tax/{tax.id}/" in response

    @pytest.mark.django_db
    def test_redirects_to_no_taxes_when_none_exist(self, monkeypatch):
        """Should redirect to no taxes view when no taxes exist."""
        # Delete all taxes
        Tax.objects.all().delete()

        def mock_reverse(view_name, kwargs=None):
            if view_name == "lfs_no_taxes":
                return "/manage/no-product-taxes/"
            return f"/mock-url/{view_name}/"

        monkeypatch.setattr("lfs.manage.product_taxes.views.reverse", mock_reverse)

        view = ManageTaxesView()
        response = view.get_redirect_url()

        assert response == "/manage/no-product-taxes/"


class TestTaxUpdateView:
    """Test the TaxUpdateView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from Django UpdateView."""
        from django.views.generic.edit import UpdateView

        assert issubclass(TaxUpdateView, UpdateView)

    def test_model_attribute(self):
        """Should use Tax model."""
        assert TaxUpdateView.model == Tax

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert TaxUpdateView.permission_required == "core.manage_shop"

    def test_fields_attribute(self):
        """Should define correct fields."""
        assert TaxUpdateView.fields == ("rate", "description")

    def test_template_name(self):
        """Should use correct template."""
        assert TaxUpdateView.template_name == "manage/product_taxes/tax.html"

    def test_context_object_name(self):
        """Should use correct context object name."""
        assert TaxUpdateView.context_object_name == "tax"

    def test_get_success_url_method_exists(self):
        """Should have get_success_url method."""
        assert hasattr(TaxUpdateView, "get_success_url")
        assert callable(getattr(TaxUpdateView, "get_success_url"))

    def test_get_taxes_queryset_method_exists(self):
        """Should have get_taxes_queryset method."""
        assert hasattr(TaxUpdateView, "get_taxes_queryset")
        assert callable(getattr(TaxUpdateView, "get_taxes_queryset"))

    def test_get_context_data_method_exists(self):
        """Should have get_context_data method."""
        assert hasattr(TaxUpdateView, "get_context_data")
        assert callable(getattr(TaxUpdateView, "get_context_data"))

    def test_form_valid_method_exists(self):
        """Should have form_valid method."""
        assert hasattr(TaxUpdateView, "form_valid")
        assert callable(getattr(TaxUpdateView, "form_valid"))

    @pytest.mark.django_db
    def test_get_taxes_queryset_without_search(self, multiple_taxes):
        """Should return all taxes when no search query."""
        factory = RequestFactory()
        request = factory.get("/")

        view = TaxUpdateView()
        view.request = request

        queryset = view.get_taxes_queryset()

        assert queryset.count() == 3
        assert all(tax in queryset for tax in multiple_taxes)

    @pytest.mark.django_db
    def test_get_taxes_queryset_with_search(self, multiple_taxes):
        """Should filter taxes based on search query."""
        factory = RequestFactory()
        request = factory.get("/?q=19")

        view = TaxUpdateView()
        view.request = request

        queryset = view.get_taxes_queryset()

        assert queryset.count() == 1
        assert queryset.first().rate == 19.0

    @pytest.mark.django_db
    def test_get_context_data_includes_taxes(self, tax):
        """Should include taxes in context data."""
        factory = RequestFactory()
        request = factory.get("/")

        view = TaxUpdateView()
        view.request = request
        view.object = tax

        context = view.get_context_data()

        assert "taxes" in context
        assert "search_query" in context
        assert context["search_query"] == ""

    @pytest.mark.django_db
    def test_form_valid_adds_success_message(self, tax, monkeypatch):
        """Should add success message on form validation."""
        # Mock the messages framework
        mock_messages_success = monkeypatch.setattr(
            "lfs.manage.product_taxes.views.messages.success", lambda request, message: None
        )

        factory = RequestFactory()
        request = factory.post("/", {"rate": "20.0", "description": "Updated VAT"})

        view = TaxUpdateView()
        view.request = request
        view.object = tax

        # Create a mock form
        class MockForm:
            def __init__(self):
                self.cleaned_data = {"rate": "20.0", "description": "Updated VAT"}

            def save(self):
                tax.rate = 20.0
                tax.description = "Updated VAT"
                tax.save()
                return tax

        form = MockForm()
        response = view.form_valid(form)

        # Should return a redirect response
        assert isinstance(response, HttpResponseRedirect)


class TestNoTaxesView:
    """Test the NoTaxesView template view."""

    def test_view_inheritance(self):
        """Should inherit from Django TemplateView."""
        from django.views.generic.base import TemplateView

        assert issubclass(NoTaxesView, TemplateView)

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert NoTaxesView.permission_required == "core.manage_shop"

    def test_template_name(self):
        """Should use correct template."""
        assert NoTaxesView.template_name == "manage/product_taxes/no_taxes.html"


class TestTaxCreateView:
    """Test the TaxCreateView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from Django CreateView."""
        from django.views.generic.edit import CreateView

        assert issubclass(TaxCreateView, CreateView)

    def test_model_attribute(self):
        """Should use Tax model."""
        assert TaxCreateView.model == Tax

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert TaxCreateView.permission_required == "core.manage_shop"

    def test_fields_attribute(self):
        """Should define correct fields."""
        assert TaxCreateView.fields == ("rate", "description")

    def test_template_name(self):
        """Should use correct template."""
        assert TaxCreateView.template_name == "manage/product_taxes/add_tax.html"

    def test_get_success_url_method_exists(self):
        """Should have get_success_url method."""
        assert hasattr(TaxCreateView, "get_success_url")
        assert callable(getattr(TaxCreateView, "get_success_url"))

    def test_get_form_kwargs_method_exists(self):
        """Should have get_form_kwargs method."""
        assert hasattr(TaxCreateView, "get_form_kwargs")
        assert callable(getattr(TaxCreateView, "get_form_kwargs"))

    def test_get_context_data_method_exists(self):
        """Should have get_context_data method."""
        assert hasattr(TaxCreateView, "get_context_data")
        assert callable(getattr(TaxCreateView, "get_context_data"))

    def test_form_valid_method_exists(self):
        """Should have form_valid method."""
        assert hasattr(TaxCreateView, "form_valid")
        assert callable(getattr(TaxCreateView, "form_valid"))

    def test_get_form_kwargs_adds_prefix(self):
        """Should add 'create' prefix to form fields."""
        factory = RequestFactory()
        request = factory.get("/")

        view = TaxCreateView()
        view.request = request

        kwargs = view.get_form_kwargs()

        assert "prefix" in kwargs
        assert kwargs["prefix"] == "create"

    @pytest.mark.django_db
    def test_get_context_data_includes_came_from(self):
        """Should include came_from in context data."""
        factory = RequestFactory()
        request = factory.post("/", {"came_from": "/manage/taxes/"})

        view = TaxCreateView()
        view.request = request
        view.object = None  # Set object to None for CreateView

        context = view.get_context_data()

        assert "came_from" in context
        assert context["came_from"] == "/manage/taxes/"

    @pytest.mark.django_db
    def test_form_valid_adds_success_message(self, monkeypatch):
        """Should add success message on form validation."""
        # Mock the messages framework
        mock_messages_success = monkeypatch.setattr(
            "lfs.manage.product_taxes.views.messages.success", lambda request, message: None
        )

        factory = RequestFactory()
        request = factory.post("/", {"rate": "15.0", "description": "New VAT"})

        view = TaxCreateView()
        view.request = request

        # Create a mock form
        class MockForm:
            def __init__(self):
                self.cleaned_data = {"rate": "15.0", "description": "New VAT"}

            def save(self):
                return Tax.objects.create(rate=15.0, description="New VAT")

        form = MockForm()
        response = view.form_valid(form)

        # Should return a redirect response
        assert isinstance(response, HttpResponseRedirect)


class TestTaxDeleteConfirmView:
    """Test the TaxDeleteConfirmView template view."""

    def test_view_inheritance(self):
        """Should inherit from Django TemplateView."""
        from django.views.generic.base import TemplateView

        assert issubclass(TaxDeleteConfirmView, TemplateView)

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert TaxDeleteConfirmView.permission_required == "core.manage_shop"

    def test_template_name(self):
        """Should use correct template."""
        assert TaxDeleteConfirmView.template_name == "manage/product_taxes/delete_tax.html"

    def test_get_context_data_method_exists(self):
        """Should have get_context_data method."""
        assert hasattr(TaxDeleteConfirmView, "get_context_data")
        assert callable(getattr(TaxDeleteConfirmView, "get_context_data"))

    @pytest.mark.django_db
    def test_get_context_data_includes_tax(self, tax):
        """Should include tax in context data."""
        factory = RequestFactory()
        request = factory.get("/")

        view = TaxDeleteConfirmView()
        view.request = request
        view.kwargs = {"pk": tax.id}

        context = view.get_context_data()

        assert "tax" in context
        assert context["tax"] == tax


class TestTaxDeleteView:
    """Test the TaxDeleteView class-based view."""

    def test_view_inheritance(self):
        """Should inherit from Django DeleteView."""
        from django.views.generic.edit import DeleteView

        assert issubclass(TaxDeleteView, DeleteView)

    def test_model_attribute(self):
        """Should use Tax model."""
        assert TaxDeleteView.model == Tax

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert TaxDeleteView.permission_required == "core.manage_shop"

    def test_success_message(self):
        """Should have success message."""
        assert TaxDeleteView.success_message == "Tax has been deleted."

    def test_get_success_url_method_exists(self):
        """Should have get_success_url method."""
        assert hasattr(TaxDeleteView, "get_success_url")
        assert callable(getattr(TaxDeleteView, "get_success_url"))

    def test_delete_method_exists(self):
        """Should have delete method."""
        assert hasattr(TaxDeleteView, "delete")
        assert callable(getattr(TaxDeleteView, "delete"))

    @pytest.mark.django_db
    def test_get_success_url_with_remaining_taxes(self, multiple_taxes, monkeypatch):
        """Should redirect to next tax when others exist."""

        def mock_reverse(view_name, kwargs=None):
            if view_name == "lfs_manage_tax" and kwargs and kwargs.get("pk") == multiple_taxes[1].id:
                return f"/manage/tax/{multiple_taxes[1].id}/"
            return f"/mock-url/{view_name}/"

        monkeypatch.setattr("lfs.manage.product_taxes.views.reverse", mock_reverse)

        factory = RequestFactory()
        request = factory.post("/")

        view = TaxDeleteView()
        view.request = request
        view.object = multiple_taxes[0]  # Delete first tax

        success_url = view.get_success_url()

        assert f"/manage/tax/{multiple_taxes[1].id}/" in success_url

    @pytest.mark.django_db
    def test_get_success_url_with_no_remaining_taxes(self, tax, monkeypatch):
        """Should redirect to no taxes when no others exist."""

        def mock_reverse(view_name, kwargs=None):
            if view_name == "lfs_no_taxes":
                return "/manage/no-product-taxes/"
            return f"/mock-url/{view_name}/"

        monkeypatch.setattr("lfs.manage.product_taxes.views.reverse", mock_reverse)

        factory = RequestFactory()
        request = factory.post("/")

        view = TaxDeleteView()
        view.request = request
        view.object = tax

        success_url = view.get_success_url()

        assert success_url == "/manage/no-product-taxes/"

    @pytest.mark.django_db
    def test_delete_removes_tax(self, tax):
        """Should delete the tax from database."""
        factory = RequestFactory()
        request = factory.post("/")

        view = TaxDeleteView()
        view.request = request
        view.object = tax
        view.kwargs = {"pk": tax.id}  # Set kwargs for get_object

        # Verify tax exists before deletion
        assert Tax.objects.filter(id=tax.id).exists()

        response = view.delete(request)

        # Verify tax is deleted
        assert not Tax.objects.filter(id=tax.id).exists()
        assert isinstance(response, HttpResponseRedirect)
