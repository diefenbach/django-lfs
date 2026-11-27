"""The footer of the management interface links to the project's own website."""

from django.urls import reverse


def test_footer_links_to_the_project_website_not_to_getlfs(authenticated_client):
    """getlfs.com belongs to someone else since 2025 and redirects to an unrelated site."""
    response = authenticated_client.get(reverse("lfs_manage_dashboard"))

    content = response.content.decode()
    assert 'href="https://django-lfs.com/"' in content
    assert "getlfs.com" not in content
