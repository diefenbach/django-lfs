from django.contrib.auth import get_user_model
from django.urls import reverse

from lfs.manufacturer.models import Manufacturer
from lfs.manage.manufacturers.views import (
    ManageManufacturersView,
    ManufacturerDataView,
    ManufacturerProductsView,
    ManufacturerSEOView,
    ManufacturerCreateView,
    ManufacturerDeleteView,
    ManufacturerViewByIDView,
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


class TestManufacturerDataView:
    """Test ManufacturerDataView behavior."""



    def test_success_url_uses_manufacturer_id(self, manufacturer):
        """Should redirect to manufacturer data tab after successful save."""
        view = ManufacturerDataView()
        view.object = manufacturer

        url = view.get_success_url()

        expected_url = reverse("lfs_manage_manufacturer", kwargs={"id": manufacturer.pk})
        assert url == expected_url




class TestManufacturerProductsView:
    """Test ManufacturerProductsView behavior."""



    def test_success_url_uses_manufacturer_id(self, manufacturer):
        """Should redirect to manufacturer products tab."""
        view = ManufacturerProductsView()
        view.kwargs = {"id": manufacturer.pk}

        url = view.get_success_url()

        expected_url = reverse("lfs_manage_manufacturer_products", kwargs={"id": manufacturer.pk})
        assert url == expected_url


class TestManufacturerSEOView:
    """Test ManufacturerSEOView behavior."""



    def test_success_url_uses_manufacturer_id(self, manufacturer):
        """Should redirect to manufacturer SEO tab after successful save."""
        view = ManufacturerSEOView()
        view.object = manufacturer

        url = view.get_success_url()

        expected_url = reverse("lfs_manage_manufacturer_seo", kwargs={"id": manufacturer.pk})
        assert url == expected_url





class TestManufacturerCreateView:
    """Test ManufacturerCreateView behavior."""


    def test_success_url_uses_created_manufacturer_id(self, manufacturer):
        """Should redirect to created manufacturer after successful creation."""
        view = ManufacturerCreateView()
        view.object = manufacturer

        url = view.get_success_url()

        expected_url = reverse("lfs_manage_manufacturer", kwargs={"id": manufacturer.pk})
        assert url == expected_url




    def test_has_success_message(self):
        """Should have success message."""
        assert hasattr(ManufacturerCreateView, "success_message")
        assert ManufacturerCreateView.success_message is not None



class TestManufacturerDeleteView:
    """Test ManufacturerDeleteView behavior."""


    def test_success_url_goes_to_manufacturers_list(self):
        """Should redirect to manufacturers list after deletion."""
        view = ManufacturerDeleteView()

        url = view.get_success_url()

        expected_url = reverse("lfs_manage_manufacturers")
        assert url == expected_url



    def test_has_success_message(self):
        """Should have success message."""
        assert hasattr(ManufacturerDeleteView, "success_message")
        assert ManufacturerDeleteView.success_message is not None


class TestManufacturerViewByIDView:
    """Test ManufacturerViewByIDView behavior."""


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



class TestManufacturersAjaxView:
    """Test ManufacturersAjaxView behavior."""


    def test_get_method_exists(self):
        """Should have get method."""
        assert hasattr(ManufacturersAjaxView, "get")
        assert callable(getattr(ManufacturersAjaxView, "get"))


class TestManufacturerTabMixin:
    """Test ManufacturerTabMixin behavior."""


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
