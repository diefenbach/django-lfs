from django.contrib.auth import get_user_model
from django.urls import reverse

from lfs.manufacturer.models import Manufacturer
from lfs.manage.manufacturers.views import (
    ManageManufacturersView,
    ManufacturerDataView,
    ManufacturerProductsView,
    ManufacturerSEOView,
    ManufacturerPortletsView,
    ManufacturerCreateView,
    ManufacturerDeleteConfirmView,
    ManufacturerDeleteView,
    ManufacturerViewByIDView,
    NoManufacturersView,
    ManufacturersAjaxView,
)

User = get_user_model()


class TestManageManufacturersView:
    """Test ManageManufacturersView behavior."""

    def test_redirect_to_first_manufacturer_when_exists(self, request_factory, admin_user, manufacturer):
        """Should redirect to first manufacturer when manufacturers exist."""
        view = ManageManufacturersView()
        request = request_factory.get("/")
        request.user = admin_user
        view.request = request

        url = view.get_redirect_url()

        expected_url = reverse("lfs_manage_manufacturer", kwargs={"id": manufacturer.id})
        assert url == expected_url

    def test_redirect_to_no_manufacturers_when_none_exist(self, request_factory, admin_user, db):
        """Should redirect to no manufacturers view when no manufacturers exist."""
        # Ensure no manufacturers exist
        Manufacturer.objects.all().delete()

        view = ManageManufacturersView()
        request = request_factory.get("/")
        request.user = admin_user
        view.request = request

        url = view.get_redirect_url()

        expected_url = reverse("lfs_manage_no_manufacturers")
        assert url == expected_url

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ManageManufacturersView.permission_required == "core.manage_shop"


class TestManufacturerDataView:
    """Test ManufacturerDataView behavior."""

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ManufacturerDataView.permission_required == "core.manage_shop"

    def test_tab_name_is_data(self):
        """Should have correct tab name."""
        assert ManufacturerDataView.tab_name == "data"

    def test_success_url_uses_manufacturer_id(self, manufacturer):
        """Should redirect to manufacturer data tab after successful save."""
        view = ManufacturerDataView()
        view.object = manufacturer

        url = view.get_success_url()

        expected_url = reverse("lfs_manage_manufacturer", kwargs={"id": manufacturer.pk})
        assert url == expected_url

    def test_model_is_manufacturer(self):
        """Should use Manufacturer model."""
        assert ManufacturerDataView.model == Manufacturer

    def test_form_class_is_manufacturer_form(self):
        """Should use ManufacturerForm."""
        from lfs.manage.manufacturers.forms import ManufacturerForm

        assert ManufacturerDataView.form_class == ManufacturerForm

    def test_pk_url_kwarg_is_id(self):
        """Should use 'id' as URL keyword argument."""
        assert ManufacturerDataView.pk_url_kwarg == "id"


class TestManufacturerProductsView:
    """Test ManufacturerProductsView behavior."""

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ManufacturerProductsView.permission_required == "core.manage_shop"

    def test_tab_name_is_products(self):
        """Should have correct tab name."""
        assert ManufacturerProductsView.tab_name == "products"

    def test_success_url_uses_manufacturer_id(self, manufacturer):
        """Should redirect to manufacturer products tab."""
        view = ManufacturerProductsView()
        view.kwargs = {"id": manufacturer.pk}

        url = view.get_success_url()

        expected_url = reverse("lfs_manage_manufacturer_products", kwargs={"id": manufacturer.pk})
        assert url == expected_url

    def test_template_name_is_manufacturer_html(self):
        """Should use correct template."""
        assert ManufacturerProductsView.template_name == "manage/manufacturers/manufacturer.html"


class TestManufacturerSEOView:
    """Test ManufacturerSEOView behavior."""

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ManufacturerSEOView.permission_required == "core.manage_shop"

    def test_tab_name_is_seo(self):
        """Should have correct tab name."""
        assert ManufacturerSEOView.tab_name == "seo"

    def test_success_url_uses_manufacturer_id(self, manufacturer):
        """Should redirect to manufacturer SEO tab after successful save."""
        view = ManufacturerSEOView()
        view.object = manufacturer

        url = view.get_success_url()

        expected_url = reverse("lfs_manage_manufacturer_seo", kwargs={"id": manufacturer.pk})
        assert url == expected_url

    def test_model_is_manufacturer(self):
        """Should use Manufacturer model."""
        assert ManufacturerSEOView.model == Manufacturer

    def test_fields_include_seo_fields(self):
        """Should include SEO fields."""
        expected_fields = ["meta_title", "meta_description", "meta_keywords"]
        assert ManufacturerSEOView.fields == expected_fields

    def test_pk_url_kwarg_is_id(self):
        """Should use 'id' as URL keyword argument."""
        assert ManufacturerSEOView.pk_url_kwarg == "id"


class TestManufacturerPortletsView:
    """Test ManufacturerPortletsView behavior."""

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ManufacturerPortletsView.permission_required == "core.manage_shop"

    def test_tab_name_is_portlets(self):
        """Should have correct tab name."""
        assert ManufacturerPortletsView.tab_name == "portlets"


class TestManufacturerCreateView:
    """Test ManufacturerCreateView behavior."""

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ManufacturerCreateView.permission_required == "core.manage_shop"

    def test_success_url_uses_created_manufacturer_id(self, manufacturer):
        """Should redirect to created manufacturer after successful creation."""
        view = ManufacturerCreateView()
        view.object = manufacturer

        url = view.get_success_url()

        expected_url = reverse("lfs_manage_manufacturer", kwargs={"id": manufacturer.pk})
        assert url == expected_url

    def test_model_is_manufacturer(self):
        """Should use Manufacturer model."""
        assert ManufacturerCreateView.model == Manufacturer

    def test_form_class_is_manufacturer_add_form(self):
        """Should use ManufacturerAddForm."""
        from lfs.manage.manufacturers.forms import ManufacturerAddForm

        assert ManufacturerCreateView.form_class == ManufacturerAddForm

    def test_template_name_is_add_manufacturer_html(self):
        """Should use correct template."""
        assert ManufacturerCreateView.template_name == "manage/manufacturers/add_manufacturer.html"

    def test_has_success_message(self):
        """Should have success message."""
        assert hasattr(ManufacturerCreateView, "success_message")
        assert ManufacturerCreateView.success_message is not None


class TestManufacturerDeleteConfirmView:
    """Test ManufacturerDeleteConfirmView behavior."""

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ManufacturerDeleteConfirmView.permission_required == "core.manage_shop"

    def test_template_name_is_delete_manufacturer_html(self):
        """Should use correct template."""
        assert ManufacturerDeleteConfirmView.template_name == "manage/manufacturers/delete_manufacturer.html"


class TestManufacturerDeleteView:
    """Test ManufacturerDeleteView behavior."""

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ManufacturerDeleteView.permission_required == "core.manage_shop"

    def test_success_url_goes_to_manufacturers_list(self):
        """Should redirect to manufacturers list after deletion."""
        view = ManufacturerDeleteView()

        url = view.get_success_url()

        expected_url = reverse("lfs_manage_manufacturers")
        assert url == expected_url

    def test_model_is_manufacturer(self):
        """Should use Manufacturer model."""
        assert ManufacturerDeleteView.model == Manufacturer

    def test_pk_url_kwarg_is_id(self):
        """Should use 'id' as URL keyword argument."""
        assert ManufacturerDeleteView.pk_url_kwarg == "id"

    def test_has_success_message(self):
        """Should have success message."""
        assert hasattr(ManufacturerDeleteView, "success_message")
        assert ManufacturerDeleteView.success_message is not None


class TestManufacturerViewByIDView:
    """Test ManufacturerViewByIDView behavior."""

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ManufacturerViewByIDView.permission_required == "core.manage_shop"

    def test_redirect_url_uses_manufacturer_slug(self, request_factory, admin_user, manufacturer):
        """Should redirect to manufacturer detail page using slug."""
        view = ManufacturerViewByIDView()
        request = request_factory.get("/")
        request.user = admin_user
        view.request = request
        view.kwargs = {"id": manufacturer.id}

        url = view.get_redirect_url()

        expected_url = reverse("lfs_manufacturer", kwargs={"slug": manufacturer.slug})
        assert url == expected_url


class TestNoManufacturersView:
    """Test NoManufacturersView behavior."""

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert NoManufacturersView.permission_required == "core.manage_shop"

    def test_template_name_is_no_manufacturers_html(self):
        """Should use correct template."""
        assert NoManufacturersView.template_name == "manage/manufacturers/no_manufacturers.html"


class TestManufacturersAjaxView:
    """Test ManufacturersAjaxView behavior."""

    def test_permission_required(self):
        """Should require core.manage_shop permission."""
        assert ManufacturersAjaxView.permission_required == "core.manage_shop"

    def test_get_method_exists(self):
        """Should have get method."""
        assert hasattr(ManufacturersAjaxView, "get")
        assert callable(getattr(ManufacturersAjaxView, "get"))


class TestManufacturerTabMixin:
    """Test ManufacturerTabMixin behavior."""

    def test_template_name_is_manufacturer_html(self):
        """Should use correct template."""
        from lfs.manage.manufacturers.views import ManufacturerTabMixin

        assert ManufacturerTabMixin.template_name == "manage/manufacturers/manufacturer.html"

    def test_has_get_manufacturer_method(self):
        """Should have get_manufacturer method."""
        from lfs.manage.manufacturers.views import ManufacturerTabMixin

        assert hasattr(ManufacturerTabMixin, "get_manufacturer")
        assert callable(getattr(ManufacturerTabMixin, "get_manufacturer"))

    def test_has_get_manufacturers_queryset_method(self):
        """Should have get_manufacturers_queryset method."""
        from lfs.manage.manufacturers.views import ManufacturerTabMixin

        assert hasattr(ManufacturerTabMixin, "get_manufacturers_queryset")
        assert callable(getattr(ManufacturerTabMixin, "get_manufacturers_queryset"))

    def test_has_get_context_data_method(self):
        """Should have get_context_data method."""
        from lfs.manage.manufacturers.views import ManufacturerTabMixin

        assert hasattr(ManufacturerTabMixin, "get_context_data")
        assert callable(getattr(ManufacturerTabMixin, "get_context_data"))

    def test_has_get_tabs_method(self):
        """Should have _get_tabs method."""
        from lfs.manage.manufacturers.views import ManufacturerTabMixin

        assert hasattr(ManufacturerTabMixin, "_get_tabs")
        assert callable(getattr(ManufacturerTabMixin, "_get_tabs"))

    def test_has_get_navigation_context_method(self):
        """Should have _get_navigation_context method."""
        from lfs.manage.manufacturers.views import ManufacturerTabMixin

        assert hasattr(ManufacturerTabMixin, "_get_navigation_context")
        assert callable(getattr(ManufacturerTabMixin, "_get_navigation_context"))

    def test_tab_name_attribute_exists(self):
        """Should have tab_name attribute."""
        from lfs.manage.manufacturers.views import ManufacturerTabMixin

        assert hasattr(ManufacturerTabMixin, "tab_name")
