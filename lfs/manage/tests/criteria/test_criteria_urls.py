"""
Unit tests for criteria management URLs.

Ziele:
- Sicherstellen, dass URLs korrekt definiert, aufgelöst und reversibel sind.
- HTTP-Methoden werden unterstützt/rejectet wie erwartet.
- URL-Namen folgen der Projektkonvention (lfs_manage_*).
"""

from django.urls import reverse, resolve
from django.http import HttpResponse

from lfs.manage.criteria import urls
from lfs.manage.criteria.views import (
    add_criterion,
    change_criterion_form,
    delete_criterion,
)


class TestCriteriaURLResolution:
    """Core tests: URLs müssen auflösen und reversen funktionieren."""

    def test_add_resolves_and_reverses(self):
        url = reverse("lfs_manage_add_criterion")
        assert url == "/manage/add-criterion"
        resolved = resolve(url)
        assert resolved.func == add_criterion

    def test_change_resolves_and_reverses(self):
        url = reverse("lfs_manage_change_criterion_form")
        assert url == "/manage/change-criterion"
        resolved = resolve(url)
        assert resolved.func == change_criterion_form

    def test_delete_resolves_and_reverses(self):
        url = reverse("lfs_manage_delete_criterion")
        assert url == "/manage/delete-criterion"
        resolved = resolve(url)
        assert resolved.func == delete_criterion


class TestCriteriaURLIntegration:
    """Integration: Views liefern Response für korrekte Methoden."""

    def test_add_accepts_get(self, monkeypatch, request_factory, manage_user, db):
        request = request_factory.get("/add-criterion")
        request.user = manage_user

        class DummyCriterion:
            def __init__(self, *args, **kwargs):
                pass

            def render(self, *args, **kwargs):
                return "<div>ok</div>"

        monkeypatch.setattr(
            "lfs.manage.criteria.views.import_symbol",
            lambda path: DummyCriterion,
        )

        response = add_criterion(request)
        assert isinstance(response, HttpResponse)
        assert response.status_code == 200

    def test_change_accepts_post(self, monkeypatch, request_factory, manage_user, db):
        request = request_factory.post(
            "/change-criterion",
            {"type": "lfs.criteria.models.CartPriceCriterion"},
        )
        request.user = manage_user

        class DummyCriterion:
            def __init__(self, *args, **kwargs):
                pass

            def render(self, *args, **kwargs):
                return "<div>ok</div>"

        monkeypatch.setattr(
            "lfs.manage.criteria.views.import_symbol",
            lambda path: DummyCriterion,
        )

        response = change_criterion_form(request)
        assert isinstance(response, HttpResponse)
        assert response.status_code == 200

    def test_delete_accepts_delete_and_rejects_others(self, request_factory, manage_user):
        request = request_factory.delete("/delete-criterion")
        request.user = manage_user
        response = delete_criterion(request)
        assert response.status_code == 200

        # reject GET
        request = request_factory.get("/delete-criterion")
        request.user = manage_user
        assert delete_criterion(request).status_code == 405


class TestCriteriaURLNaming:
    """Architekturtests: Namen/Konventionen konsistent."""

    def test_names_are_unique_and_follow_convention(self):
        names = [p.name for p in urls.urlpatterns if p.name]
        assert len(names) == len(set(names))  # unique
        for name in names:
            assert name.startswith("lfs_manage_")
            assert "_criterion" in name
