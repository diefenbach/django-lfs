# django imports
from django.shortcuts import render_to_response
from django.template import RequestContext

# lfs imports
from lfs.caching.utils import lfs_get_object_or_404
from lfs.page.models import Page

def page_view(request, slug, template_name="lfs/page/page.html"):
    """Displays page with passed slug
    """
    if request.user.is_superuser:
        page = lfs_get_object_or_404(Page, slug=slug)
    else:
        page = lfs_get_object_or_404(Page, slug=slug, active=True)

    return render_to_response(template_name, RequestContext(request, {
        "page" : page
    }))

def pages_view(request, template_name="lfs/page/pages.html"):
    """Displays an overview of all pages.
    """
    pages = Page.objects.filter(active=True, exclude_from_navigation=False)

    return render_to_response(template_name, RequestContext(request, {
        "pages" : pages
    }))


def popup_view(request, slug, template_name="lfs/page/popup.html"):
    """Displays page with passed slug
    """
    page = lfs_get_object_or_404(Page, slug=slug)

    return render_to_response(template_name, RequestContext(request, {
        "page" : page
    }))