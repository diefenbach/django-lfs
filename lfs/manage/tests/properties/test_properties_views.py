import pytest
from unittest.mock import patch

from lfs.catalog.models import Property, PropertyOption
from lfs.manage.properties.views import (
    ManagePropertiesView,
    PropertyNavigationMixin,
    PropertyDataView,
    PropertyCreateView,
    PropertyDeleteConfirmView,
    PropertyDeleteView,
    NoPropertiesView,
    PropertyOptionAddView,
    PropertyOptionUpdateView,
    PropertyOptionDeleteView,
)


class TestManagePropertiesView:
    def test_permission_required_attribute(self):
        assert ManagePropertiesView.permission_required == "core.manage_shop"

    @pytest.mark.django_db
    def test_redirects_to_first_property_when_exists(self, mock_request_with_messages, admin_user):
        p = Property.objects.create(name="Width", title="Width")
        view = ManagePropertiesView()
        view.request = mock_request_with_messages
        url = view.get_redirect_url()
        assert str(p.id) in url

    @pytest.mark.django_db
    def test_redirects_to_add_when_none_exist(self, mock_request_with_messages, admin_user):
        Property.objects.all().delete()
        view = ManagePropertiesView()
        view.request = mock_request_with_messages
        url = view.get_redirect_url()
        assert "add" in url


class TestPropertyNavigationMixinUnit:
    @pytest.mark.django_db
    def test_get_properties_queryset_returns_queryset(self, mock_request_with_messages, admin_user):
        Property.objects.create(name="Color", title="Color")
        view = PropertyDataView()
        view.request = mock_request_with_messages
        qs = view.get_properties_queryset()
        assert qs.model == Property

    @pytest.mark.django_db
    def test_get_properties_queryset_applies_search(self, request_factory, mock_request_with_messages, admin_user):
        Property.objects.create(name="Color", title="Color")
        Property.objects.create(name="Size", title="Size")
        request = request_factory.get("/?q=col")
        request.session = {}
        view = PropertyDataView()
        view.request = request
        names = set(view.get_properties_queryset().values_list("name", flat=True))
        assert names == {"Color"}

    @pytest.mark.django_db
    def test_get_context_data_includes_navigation(self, mock_request_with_messages, admin_user):
        p = Property.objects.create(name="Material", title="Material")
        view = PropertyDataView()
        view.request = mock_request_with_messages
        view.kwargs = {"id": p.id}
        view.object = p
        context = view.get_context_data()
        assert "property" in context
        assert "properties" in context
        assert "page" in context
        assert context["property"].id == p.id


class TestPropertyDataViewUnit:
    def test_view_inheritance(self):
        from django.views.generic.edit import UpdateView

        assert issubclass(PropertyDataView, PropertyNavigationMixin)
        assert issubclass(PropertyDataView, UpdateView)

    def test_permission_required(self):
        assert PropertyDataView.permission_required == "core.manage_shop"

    def test_pk_url_kwarg(self):
        assert PropertyDataView.pk_url_kwarg == "id"

    def test_model(self):
        assert PropertyDataView.model == Property

    @pytest.mark.django_db
    def test_get_success_url(self, mock_request_with_messages, admin_user):
        p = Property.objects.create(name="Weight", title="Weight")
        view = PropertyDataView()
        view.request = mock_request_with_messages
        view.object = p
        url = view.get_success_url()
        assert str(p.id) in url

    @pytest.mark.django_db
    def test_form_valid_triggers_signal_when_type_changes(self, mock_request_with_messages, admin_user):
        p = Property.objects.create(name="Length", title="Length")
        view = PropertyDataView()
        view.request = mock_request_with_messages
        view.object = p
        view.kwargs = {"id": p.id}

        class DummyForm:
            def __init__(self):
                self.cleaned_data = {}

            def save(self, commit=True):
                return p

        with patch("lfs.manage.properties.views.property_type_changed.send") as mock_send, patch(
            "lfs.manage.properties.views.invalidate_cache_group_id"
        ) as mock_invalidate:
            # Simulate change: old_type != new type
            original_type = p.type
            p.type = original_type + 1
            response = view.form_valid(DummyForm())
            mock_send.assert_called_once()
            mock_invalidate.assert_called_once_with("global-properties-version")
            assert response is not None


class TestPropertyCreateViewUnit:
    def test_view_inheritance(self):
        from django.views.generic.edit import CreateView

        assert issubclass(PropertyCreateView, CreateView)

    def test_permission_required(self):
        assert PropertyCreateView.permission_required == "core.manage_shop"

    def test_template_name(self):
        assert PropertyCreateView.template_name == "manage/properties/add_property.html"

    @pytest.mark.django_db
    def test_form_valid_sets_defaults_and_redirects(self, mock_request_with_messages, admin_user):
        view = PropertyCreateView()
        view.request = mock_request_with_messages

        class DummyForm:
            def __init__(self):
                self.cleaned_data = {}

            def save(self, commit=True):
                return Property.objects.create(name="Density", title="")

        view.form_valid(DummyForm())
        p = Property.objects.latest("id")
        assert p.title == "Density"


class TestPropertyDeleteViewsUnit:
    @pytest.mark.django_db
    def test_delete_confirm_includes_property(self, mock_request_with_messages, admin_user):
        p = Property.objects.create(name="SKU", title="SKU")
        view = PropertyDeleteConfirmView()
        view.request = mock_request_with_messages
        view.kwargs = {"id": p.id}
        ctx = view.get_context_data()
        assert ctx["property"].id == p.id

    @pytest.mark.django_db
    def test_delete_removes_property(self, mock_request_with_messages, admin_user):
        p = Property.objects.create(name="Foo", title="Foo")
        view = PropertyDeleteView()
        view.request = mock_request_with_messages
        view.kwargs = {"id": p.id}
        with patch.object(view, "get_success_url", return_value="/ok/"), patch(
            "lfs.manage.properties.views.invalidate_cache_group_id"
        ) as mock_invalidate:
            view.delete(mock_request_with_messages)
            assert not Property.objects.filter(id=p.id).exists()
            mock_invalidate.assert_called_once_with("global-properties-version")

    def test_delete_success_url(self):
        assert "properties" in PropertyDeleteView().get_success_url()


class TestNoPropertiesViewUnit:
    @pytest.mark.django_db
    def test_get_renders_template(self, mock_request_with_messages, admin_user):
        view = NoPropertiesView()
        view.request = mock_request_with_messages
        resp = view.get(mock_request_with_messages)
        assert resp.status_code == 200


class TestPropertyOptionViewsUnit:
    @pytest.mark.django_db
    def test_option_add_creates_option(self, request_factory, mock_request_with_messages, admin_user):
        p = Property.objects.create(name="Shade", title="Shade")
        request = request_factory.post("/", data={"name": "Dark", "price": "1.5"})
        request.session = {}
        request._messages = mock_request_with_messages._messages
        view = PropertyOptionAddView()
        view.request = request
        view.kwargs = {"property_id": p.id}
        with patch("lfs.manage.properties.views.invalidate_cache_group_id") as mock_invalidate:
            view.post(request, property_id=p.id)
            assert p.options.filter(name="Dark").exists()
            mock_invalidate.assert_called_once_with("global-properties-version")

    @pytest.mark.django_db
    def test_option_add_without_name_shows_error(self, request_factory, mock_request_with_messages, admin_user):
        p = Property.objects.create(name="Pattern", title="Pattern")
        request = request_factory.post("/", data={"name": "", "price": ""})
        request.session = {}
        request._messages = mock_request_with_messages._messages
        view = PropertyOptionAddView()
        view.request = request
        view.kwargs = {"property_id": p.id}
        view.post(request, property_id=p.id)  # should not raise
        assert p.options.count() == 0

    @pytest.mark.django_db
    def test_option_update_changes_values(self, request_factory, mock_request_with_messages, admin_user):
        p = Property.objects.create(name="Finish", title="Finish")
        opt = PropertyOption.objects.create(name="Matte", property=p, price=0)
        request = request_factory.post("/", data={"option_id": opt.id, "name": "Gloss", "price": "2.2"})
        request.session = {}
        request._messages = mock_request_with_messages._messages
        view = PropertyOptionUpdateView()
        view.request = request
        view.kwargs = {"property_id": p.id}
        with patch("lfs.manage.properties.views.invalidate_cache_group_id") as mock_invalidate:
            view.post(request, property_id=p.id)
            opt.refresh_from_db()
            assert opt.name == "Gloss"
            assert opt.price >= 0
            mock_invalidate.assert_called_once_with("global-properties-version")

    @pytest.mark.django_db
    def test_option_update_with_missing_name_errors(self, request_factory, mock_request_with_messages, admin_user):
        p = Property.objects.create(name="Grain", title="Grain")
        opt = PropertyOption.objects.create(name="Fine", property=p, price=0)
        request = request_factory.post("/", data={"option_id": opt.id, "name": "", "price": "1"})
        request.session = {}
        request._messages = mock_request_with_messages._messages
        view = PropertyOptionUpdateView()
        view.request = request
        view.kwargs = {"property_id": p.id}
        view.post(request, property_id=p.id)  # should not raise
        opt.refresh_from_db()
        assert opt.name == "Fine"

    @pytest.mark.django_db
    def test_option_delete_removes_option(self, mock_request_with_messages, admin_user):
        p = Property.objects.create(name="Edge", title="Edge")
        opt = PropertyOption.objects.create(name="Soft", property=p, price=0)
        view = PropertyOptionDeleteView()
        view.request = mock_request_with_messages
        view.kwargs = {"option_id": opt.id}
        with patch("lfs.manage.properties.views.invalidate_cache_group_id") as mock_invalidate:
            response = view.delete(mock_request_with_messages)
            assert response is not None
            assert not PropertyOption.objects.filter(id=opt.id).exists()
            mock_invalidate.assert_called_once_with("global-properties-version")
