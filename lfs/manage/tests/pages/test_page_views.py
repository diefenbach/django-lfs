"""The page management, tested through real requests as a shop manager: the list and its search, adding, saving
(including the attached file), SEO, portlets, viewing and deleting a page, and the root page, which only has
portlets."""

import pytest
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from lfs.page.models import Page

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def media_root(settings, tmp_path):
    """Store uploaded files in a temporary folder."""
    settings.MEDIA_ROOT = str(tmp_path)


@pytest.fixture(autouse=True)
def root():
    """The root page, which holds the portlets of all pages."""
    return Page.objects.get_or_create(pk=1, defaults={"title": "Root", "slug": "root"})[0]


@pytest.fixture
def manager(client, admin_user, shop):
    """A test client logged in as a shop manager."""
    client.force_login(admin_user)
    return client


@pytest.fixture
def imprint():
    return Page.objects.create(title="Imprint", slug="imprint", active=True)


def messages_of(response) -> list[str]:
    """Return the messages the request added for the manager."""
    return [str(m) for m in get_messages(response.wsgi_request)]


class TestStartAndList:
    def test_shows_the_first_page_by_title_but_not_the_root(self, manager):
        Page.objects.create(title="Terms", slug="terms")
        imprint = Page.objects.create(title="Imprint", slug="imprint")

        assert manager.get(reverse("lfs_manage_pages"))["Location"] == reverse(
            "lfs_manage_page", kwargs={"id": imprint.id}
        )

    def test_with_only_the_root_offers_to_add_a_page(self, manager):
        assert manager.get(reverse("lfs_manage_pages"))["Location"] == reverse("lfs_add_page")

    def test_search_filters_the_list_and_the_tabs_keep_it(self, manager, imprint):
        terms = Page.objects.create(title="Terms", slug="terms")
        url = reverse("lfs_manage_page", kwargs={"id": imprint.id})
        assert list(manager.get(url).context["pages"]) == [imprint, terms]  # without the root page

        response = manager.get(url, {"q": "impr"})

        assert list(response.context["pages"]) == [imprint]
        assert [name for name, _ in response.context["tabs"]] == ["data", "seo", "portlets"]
        assert all(url.endswith("?q=impr") for _, url in response.context["tabs"])


class TestPage:
    def test_adds_a_page(self, manager):
        response = manager.post(reverse("lfs_add_page"), {"title": "Imprint", "slug": "imprint"})

        imprint = Page.objects.get(slug="imprint")
        assert response["Location"] == reverse("lfs_manage_page", kwargs={"id": imprint.id})
        assert messages_of(response) == ["Page has been created."]

    def test_a_slug_must_be_unique(self, manager, imprint):
        response = manager.post(reverse("lfs_add_page"), {"title": "Imprint 2", "slug": "imprint"})

        assert response.context["form"].errors["slug"]
        assert Page.objects.filter(slug="imprint").count() == 1

    def test_saves_the_data(self, manager, imprint):
        url = reverse("lfs_manage_page", kwargs={"id": imprint.id})

        response = manager.post(url, {"title": "Legal", "slug": "legal", "body": "<p>Us</p>", "active": "on"})

        imprint.refresh_from_db()
        assert (imprint.title, imprint.slug, imprint.body, imprint.active) == ("Legal", "legal", "<p>Us</p>", True)
        assert response["Location"] == url
        assert messages_of(response) == ["Page has been saved."]

    def test_uploads_and_clears_the_file(self, manager, imprint):
        url = reverse("lfs_manage_page", kwargs={"id": imprint.id})
        data = {"title": "Imprint", "slug": "imprint"}

        manager.post(url, data | {"file": SimpleUploadedFile("terms.pdf", b"pdf")})
        assert Page.objects.get(pk=imprint.pk).file.read() == b"pdf"

        manager.post(url, data | {"file-clear": "on"})
        assert not Page.objects.get(pk=imprint.pk).file

    def test_shows_the_seo_data(self, manager, imprint):
        response = manager.get(reverse("lfs_manage_page_seo", kwargs={"id": imprint.id}))

        assert response.context["form"].instance == imprint

    def test_saves_the_seo_data(self, manager, imprint):
        url = reverse("lfs_manage_page_seo", kwargs={"id": imprint.id})

        response = manager.post(url, {"meta_title": "Imprint", "meta_description": "Who we are", "meta_keywords": "us"})

        imprint.refresh_from_db()
        assert (imprint.meta_title, imprint.meta_description, imprint.meta_keywords) == ("Imprint", "Who we are", "us")
        assert response["Location"] == url
        assert messages_of(response) == ["SEO data has been saved."]

    def test_shows_the_portlets_tab(self, manager, imprint):
        response = manager.get(reverse("lfs_manage_page_portlets", kwargs={"id": imprint.id}))

        assert response.context["active_tab"] == "portlets" and response.context["portlets"]

    def test_view_opens_the_page_in_the_shop(self, manager, imprint):
        response = manager.get(reverse("lfs_page_view_by_id", kwargs={"id": imprint.id}))

        assert response["Location"] == reverse("lfs_page_view", kwargs={"slug": "imprint"})

    def test_confirmation_names_the_page(self, manager, imprint):
        assert manager.get(reverse("lfs_delete_page_confirm", kwargs={"id": imprint.id})).context["page"] == imprint

    def test_deletes_the_page(self, manager, imprint):
        response = manager.post(reverse("lfs_delete_page", kwargs={"id": imprint.id}))

        assert not Page.objects.filter(pk=imprint.pk).exists()
        assert response["Location"] == reverse("lfs_manage_pages")
        assert messages_of(response) == ["Page has been deleted."]


class TestRootPage:
    def test_has_only_the_portlets_tab(self, manager, root):
        response = manager.get(reverse("lfs_manage_page_portlets", kwargs={"id": root.id}))

        assert [name for name, _ in response.context["tabs"]] == ["portlets"]

    def test_data_tab_leads_to_the_portlets(self, manager, root):
        response = manager.get(reverse("lfs_manage_page", kwargs={"id": root.id}))

        assert response["Location"] == reverse("lfs_manage_page_portlets", kwargs={"id": root.id})

    @pytest.mark.parametrize("method", ["get", "post"])
    def test_has_no_seo(self, manager, root, method: str):
        response = getattr(manager, method)(
            reverse("lfs_manage_page_seo", kwargs={"id": root.id}), {"meta_title": "X"} if method == "post" else {}
        )

        assert response.status_code == 403
        assert Page.objects.get(pk=root.pk).meta_title != "X"

    def test_cannot_be_viewed_in_the_shop(self, manager, root):
        assert manager.get(reverse("lfs_page_view_by_id", kwargs={"id": root.id})).status_code == 404
