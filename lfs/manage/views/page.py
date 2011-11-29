# django imports
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST

# lfs imports
import lfs.core.utils
from lfs.core.utils import LazyEncoder
from lfs.core.widgets.file import LFSFileInput
from lfs.page.models import Page


class PageForm(ModelForm):
    """Form to edit a page.
    """
    def __init__(self, *args, **kwargs):
        super(PageForm, self).__init__(*args, **kwargs)
        self.fields["file"].widget = LFSFileInput()

    class Meta:
        model = Page
        exclude = ("position",)


class PageAddForm(ModelForm):
    """Form to add a page.
    """
    class Meta:
        model = Page
        exclude = ("active", "position", "body", "short_text", "exclude_from_navigation", "file")


@permission_required("core.manage_shop", login_url="/login/")
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


@permission_required("core.manage_shop", login_url="/login/")
def manage_page(request, id, template_name="manage/page/page.html"):
    """Provides a form to edit the page with the passed id.
    """
    page = get_object_or_404(Page, pk=id)
    if request.method == "POST":
        form = PageForm(instance=page, data=request.POST, files=request.FILES)
        if form.is_valid():
            new_page = form.save()
            _update_positions()

            # delete file
            if request.POST.get("delete_file"):
                page.file.delete()

            return lfs.core.utils.set_message_cookie(
                url=reverse("lfs_manage_page", kwargs={"id": page.id}),
                msg=_(u"Page has been saved."),
            )
    else:
        form = PageForm(instance=page)

    return render_to_response(template_name, RequestContext(request, {
        "page": page,
        "pages": Page.objects.all(),
        "form": form,
        "current_id": int(id),
    }))


@permission_required("core.manage_shop", login_url="/login/")
def add_page(request, template_name="manage/page/add_page.html"):
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

    return render_to_response(template_name, RequestContext(request, {
        "form": form,
        "pages": Page.objects.all(),
    }))


@require_POST
@permission_required("core.manage_shop", login_url="/login/")
def delete_page(request, id):
    """Deletes the page with passed id.
    """
    page = get_object_or_404(Page, pk=id)
    page.delete()

    return lfs.core.utils.set_message_cookie(
        url=reverse("lfs_manage_pages"),
        msg=_(u"Page has been deleted."),
    )


def sort_pages(request):
    """Sorts pages after drag 'n drop.
    """
    page_list = request.POST.get("pages", "").split('&')
    assert (isinstance(page_list, list))
    if len(page_list) > 0:
        pos = 10
        for page_str in page_list:
            page_id = page_str.split('=')[1]
            page_obj = Page.objects.get(pk=page_id)
            page_obj.position = pos
            page_obj.save()
            pos = pos + 10

        result = simplejson.dumps({
            "message": _(u"The pages have been sorted."),
        }, cls=LazyEncoder)

        return HttpResponse(result)


def _update_positions():
    """Updates the positions of all pages.
    """
    for i, page in enumerate(Page.objects.all()):
        page.position = (i + 1) * 10
        page.save()
