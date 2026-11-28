"""The static block management, tested through real requests as a shop manager: the list and its search, adding,
saving, previewing and deleting a block, and uploading, updating and deleting its files."""

import pytest
from django.contrib.messages import get_messages
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from lfs.catalog.models import File, StaticBlock

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def media_root(settings, tmp_path):
    """Store uploaded files in a temporary folder."""
    settings.MEDIA_ROOT = str(tmp_path)


@pytest.fixture
def manager(client, admin_user, shop):
    """A test client logged in as a shop manager."""
    client.force_login(admin_user)
    return client


@pytest.fixture
def block():
    return StaticBlock.objects.create(name="Footer", html="<p>Hello</p>")


def messages_of(response) -> list[str]:
    """Return the messages the request added for the manager."""
    return [str(m) for m in get_messages(response.wsgi_request)]


def attach(block: StaticBlock, title: str, position: int = 999) -> File:
    """Attach a stored file to the block."""
    file = File(content=block, title=title, position=position)
    file.file.save(f"{title}.txt", ContentFile(b"content"), save=True)
    return file


class TestStartAndList:
    def test_shows_the_first_block_by_name(self, manager):
        StaticBlock.objects.create(name="Header")
        footer = StaticBlock.objects.create(name="Footer")

        assert manager.get(reverse("lfs_manage_static_blocks"))["Location"] == reverse(
            "lfs_manage_static_block", kwargs={"id": footer.id}
        )

    def test_without_blocks_shows_the_empty_page(self, manager):
        assert manager.get(reverse("lfs_manage_static_blocks"))["Location"] == reverse("lfs_manage_no_static_blocks")

    def test_search_filters_the_list_and_the_tabs_keep_it(self, manager, block):
        StaticBlock.objects.create(name="Header")

        response = manager.get(reverse("lfs_manage_static_block", kwargs={"id": block.id}), {"q": "foot & more"})

        assert list(response.context["static_blocks"]) == []
        assert all(url.endswith("?q=foot+%26+more") for _, url in response.context["tabs"])
        assert list(manager.get(response.request["PATH_INFO"], {"q": "foo"}).context["static_blocks"]) == [block]


class TestBlock:
    def test_adds_a_block(self, manager):
        response = manager.post(reverse("lfs_manage_add_static_block"), {"name": "Footer"})

        footer = StaticBlock.objects.get()
        assert response["Location"] == reverse("lfs_manage_static_block", kwargs={"id": footer.id})
        assert messages_of(response) == ["Static block has been created."]

    def test_a_block_needs_a_name(self, manager):
        manager.post(reverse("lfs_manage_add_static_block"), {"name": ""})

        assert not StaticBlock.objects.exists()

    def test_saves_name_and_html(self, manager, block):
        url = reverse("lfs_manage_static_block", kwargs={"id": block.id})

        response = manager.post(url, {"name": "Shop footer", "html": "<p>Bye</p>"})

        block.refresh_from_db()
        assert (block.name, block.html) == ("Shop footer", "<p>Bye</p>")
        assert response["Location"] == url
        assert messages_of(response) == ["Static block has been saved."]

    def test_preview_shows_the_html(self, manager, block):
        response = manager.get(reverse("lfs_preview_static_block", kwargs={"id": block.id}))

        assert "<p>Hello</p>" in response.content.decode()

    def test_confirmation_names_the_block(self, manager, block):
        response = manager.get(reverse("lfs_manage_delete_static_block_confirm", kwargs={"id": block.id}))

        assert response.context["static_block"] == block

    def test_deletes_the_block_with_its_files(self, manager, block):
        attach(block, "logo")

        response = manager.post(reverse("lfs_delete_static_block", kwargs={"id": block.id}))

        assert not StaticBlock.objects.exists()
        assert not File.objects.exists()
        assert response["Location"] == reverse("lfs_manage_static_blocks")


class TestFiles:
    def url(self, block) -> str:
        return reverse("lfs_manage_static_block_files", kwargs={"id": block.id})

    def test_lists_the_files_of_this_block(self, manager, block):
        attach(block, "footer-logo")
        attach(StaticBlock.objects.create(name="Header"), "header-logo")

        page = manager.get(self.url(block)).content.decode()

        assert "footer-logo" in page and "header-logo" not in page

    def test_uploads_files_named_after_the_upload_and_numbers_them(self, manager, block):
        attach(block, "existing", position=5)

        response = manager.post(
            self.url(block),
            {"files[]": [SimpleUploadedFile("a.png", b"a"), SimpleUploadedFile("b.png", b"b")]},
        )

        assert list(block.files.values_list("title", "position")) == [("existing", 10), ("a.png", 20), ("b.png", 30)]
        assert block.files.get(title="a.png").file.read() == b"a"
        assert response["Location"] == self.url(block)
        assert messages_of(response) == ["Files have been uploaded successfully."]

    def test_updates_titles_and_positions(self, manager, block):
        first, second = attach(block, "first", 10), attach(block, "second", 20)

        response = manager.post(
            self.url(block),
            {"update": "1", f"title-{first.id}": "Logo", f"position-{first.id}": "30", f"position-{second.id}": "abc"},
        )

        assert list(block.files.values_list("title", "position")) == [("second", 20), ("Logo", 30)]
        assert messages_of(response) == ["Files have been updated successfully."]

    def test_deletes_the_checked_files_and_renumbers_the_rest(self, manager, block):
        attach(block, "first", 1)
        second = attach(block, "second", 2)
        attach(block, "third", 3)

        response = manager.post(self.url(block), {"delete": "1", f"delete-{second.id}": "on", "delete-abc": "on"})

        assert list(block.files.values_list("title", "position")) == [("first", 10), ("third", 20)]
        assert messages_of(response) == ["Files have been deleted successfully."]


class TestFilesOfOtherBlocks:
    """The files tab of one block must not change the files of another block."""

    def test_are_not_updated(self, manager, block):
        other = attach(StaticBlock.objects.create(name="Header"), "other", 10)

        manager.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": block.id}),
            {"update": "1", f"title-{other.id}": "Hacked", f"position-{other.id}": "1"},
        )

        other.refresh_from_db()
        assert (other.title, other.position) == ("other", 10)

    def test_are_not_deleted(self, manager, block):
        other = attach(StaticBlock.objects.create(name="Header"), "other")

        manager.post(
            reverse("lfs_manage_static_block_files", kwargs={"id": block.id}),
            {"delete": "1", f"delete-{other.id}": "on"},
        )

        assert File.objects.filter(pk=other.pk).exists()
