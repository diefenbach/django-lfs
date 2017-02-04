# django imports
from django.http import Http404
from django.shortcuts import render

# lfs imports
from lfs.caching.utils import lfs_get_object_or_404
from lfs.page.models import Page


def page_view(request, slug, template_name="lfs/page/page.html"):
    """Displays page with passed slug
    """
    page = lfs_get_object_or_404(Page, slug=slug)
    if page.id == 1:
        raise Http404()

    if request.user.is_superuser or page.active:
        return render(request, template_name, {
            "page": page
        })

    raise Http404('No Page matches the given query.')


def pages_view(request, template_name="lfs/page/pages.html"):
    """Displays an overview of all pages.
    """
    pages = Page.objects.filter(active=True, exclude_from_navigation=False)

    return render(request, template_name, {
        "pages": pages,
        "page": Page.objects.get(pk=1),
    })


def popup_view(request, slug, template_name="lfs/page/popup.html"):
    """Displays page with passed slug
    """
    page = lfs_get_object_or_404(Page, slug=slug)

    return render(request, template_name, {
        "page": page
    })
