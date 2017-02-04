import json

# django imports
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseForbidden
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST

# lfs imports
import lfs.core.utils
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.utils import LazyEncoder
from lfs.manage.seo.views import SEOView
from lfs.manage.views.lfs_portlets import portlets_inline
from lfs.manage.pages.forms import PageAddForm
from lfs.manage.pages.forms import PageForm
from lfs.page.models import Page


# Views
class PageSEOView(SEOView):
    def get(self, request, id):
        if id == '1':
            return HttpResponseForbidden()
        return super(PageSEOView, self).get(request, id)

    def post(self, request, id):
        if id == '1':
            return HttpResponseForbidden()
        return super(PageSEOView, self).post(request, id)


@permission_required("core.manage_shop")
def manage_pages(request):
    """Dispatches to the first page or to the form to add a page (if there is no
    page yet).
    """
    try:
        page = Page.objects.all()[0]
        url = reverse("lfs_manage_page", kwargs={"id": page.id})
    except IndexError:
        url = reverse("lfs_add_page")

    return HttpResponseRedirect(url)


@permission_required("core.manage_shop")
def manage_page(request, id, template_name="manage/pages/page.html"):
    """Provides a form to edit the page with the passed id.
    """
    page = get_object_or_404(Page, pk=id)

    return render(request, template_name, {
        "page": page,
        "navigation": navigation(request, page),
        "seo_tab": PageSEOView(Page).render(request, page),
        "data_tab": data_tab(request, page),
        "portlets": portlets_inline(request, page),
    })


@permission_required("core.manage_shop")
def page_view_by_id(request, id, template_name="lfs/page/page.html"):
    """Displays page with passed id.
    """
    if id == 1:
        raise Http404()

    page = lfs_get_object_or_404(Page, pk=id)
    url = reverse("lfs_page_view", kwargs={"slug": page.slug})
    return HttpResponseRedirect(url)


# Parts
def data_tab(request, page, template_name="manage/pages/data_tab.html"):
    """Renders the data tab for passed page.
    """
    if request.method == "POST":
        form = PageForm(instance=page, data=request.POST, files=request.FILES)
        if form.is_valid():
            page = form.save()

        # delete file
        if request.POST.get("delete_file"):
            page.file.delete()

    else:
        form = PageForm(instance=page)

    return render_to_string(template_name, request=request, context={
        "form": form,
        "page": page,
    })


def navigation(request, page, template_name="manage/pages/navigation.html"):
    """Renders the navigation for passed page.
    """
    return render_to_string(template_name, request=request, context={
        "root": Page.objects.get(pk=1),
        "page": page,
        "pages": Page.objects.exclude(pk=1),
    })


# Actions
@permission_required("core.manage_shop")
def save_data_tab(request, id):
    """Saves the data tab.
    """
    if id == 1:
        raise Http404()

    page = lfs_get_object_or_404(Page, pk=id)

    html = (
        ("#data_tab", data_tab(request, page)),
        ("#navigation", navigation(request, page)),
    )

    result = json.dumps({
        "html": html,
        "message": _(u"Data has been saved."),
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def add_page(request, template_name="manage/pages/add_page.html"):
    """Provides a form to add a new page.
    """
    if request.method == "POST":
        form = PageAddForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            page = form.save()
            _update_positions()

            return lfs.core.utils.set_message_cookie(
                url=reverse("lfs_manage_page", kwargs={"id": page.id}),
                msg=_(u"Page has been added."),
            )
    else:
        form = PageAddForm()

    return render(request, template_name, {
        "form": form,
        "pages": Page.objects.all(),
        "came_from": (request.POST if request.method == 'POST' else request.GET).get("came_from",
                                                                                     reverse("lfs_manage_pages")),
    })


@permission_required("core.manage_shop")
@require_POST
def delete_page(request, id):
    """Deletes the page with passed id.
    """
    page = get_object_or_404(Page, pk=id)
    page.delete()

    return lfs.core.utils.set_message_cookie(
        url=reverse("lfs_manage_pages"),
        msg=_(u"Page has been deleted."),
    )


@permission_required("core.manage_shop")
@require_POST
def sort_pages(request):
    """Sorts pages after drag 'n drop.
    """
    page_list = request.POST.get("objs", "").split('&')
    assert (isinstance(page_list, list))
    if len(page_list) > 0:
        pos = 10
        for page_str in page_list:
            page_id = page_str.split('=')[1]
            page_obj = Page.objects.get(pk=page_id)
            page_obj.position = pos
            page_obj.save()
            pos = pos + 10

        result = json.dumps({
            "message": _(u"The pages have been sorted."),
        }, cls=LazyEncoder)

        return HttpResponse(result, content_type='application/json')


def _update_positions():
    """Updates the positions of all pages.
    """
    for i, page in enumerate(Page.objects.all()):
        page.position = (i + 1) * 10
        page.save()
