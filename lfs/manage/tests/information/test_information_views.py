import pytest
from django.test import RequestFactory

from lfs.manage.information.views import EnvironmentView


class MockSession(dict):
    """Mock session with session_key attribute and proper dict-like behavior."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session_key = "test_session_key"

    def get(self, key, default=None):
        return super().get(key, default)


class TestEnvironmentView:
    """Test the environment view function."""

    @pytest.mark.django_db
    def test_environment_view_returns_correct_context(self, admin_user):
        """Test that environment view returns correct context data."""
        factory = RequestFactory()
        request = factory.get("/environment")
        request.user = admin_user
        request.session = MockSession()

        view = EnvironmentView()
        view.request = request
        response = view.get(request)

        assert response.status_code == 200
        # For class-based views, we can check context data
        assert "lfs_version" in response.context_data
        assert "apps" in response.context_data
        assert isinstance(response.context_data["apps"], list)

    @pytest.mark.django_db
    def test_environment_view_filters_installed_apps(self, admin_user):
        """Test that environment view filters out LFS and Django apps."""
        factory = RequestFactory()
        request = factory.get("/environment")
        request.user = admin_user
        request.session = MockSession()

        view = EnvironmentView()
        view.request = request
        response = view.get(request)
        apps = response.context_data["apps"]

        # Should not contain LFS or Django apps
        app_names = [app["name"] for app in apps]
        for app_name in app_names:
            assert not app_name.startswith("lfs.")
            assert not app_name.startswith("django.")
            assert app_name != "lfs"

    @pytest.mark.django_db
    def test_environment_view_apps_sorted_by_name(self, admin_user):
        """Test that apps are sorted alphabetically by name."""
        factory = RequestFactory()
        request = factory.get("/environment")
        request.user = admin_user
        request.session = MockSession()

        view = EnvironmentView()
        view.request = request
        response = view.get(request)
        apps = response.context_data["apps"]

        # Check that apps are sorted by name
        app_names = [app["name"] for app in apps]
        assert app_names == sorted(app_names)

    @pytest.mark.django_db
    def test_environment_view_handles_missing_version(self, admin_user):
        """Test that environment view handles apps without __version__ gracefully."""
        factory = RequestFactory()
        request = factory.get("/environment")
        request.user = admin_user
        request.session = MockSession()

        view = EnvironmentView()
        view.request = request
        response = view.get(request)
        apps = response.context_data["apps"]

        # All apps should have a version field, even if "N/A"
        for app in apps:
            assert "version" in app
            assert app["version"] is not None

    @pytest.mark.django_db
    def test_environment_view_uses_correct_template(self, admin_user):
        """Test that environment view uses the correct template."""
        factory = RequestFactory()
        request = factory.get("/environment")
        request.user = admin_user
        request.session = MockSession()

        view = EnvironmentView()
        view.request = request
        response = view.get(request)

        assert response.status_code == 200
        assert "manage/information/environment.html" in response.template_name
