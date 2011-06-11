# django imports
from django.contrib.auth.decorators import permission_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST

# lfs imports
import lfs.core.utils
from lfs.core.utils import LazyEncoder
from lfs.caching.utils import lfs_get_object_or_404
from lfs.catalog.models import StaticBlock
from lfs.catalog.models import File


class StaticBlockForm(ModelForm):
    """Form to add and edit a static block.
    """
    class Meta:
        model = StaticBlock


@permission_required("core.manage_shop", login_url="/login/")
def manage_static_blocks(request):
    """Dispatches to the first static block or to the add static block form.
    """
    try:
        sb = StaticBlock.objects.all()[0]
        url = reverse("lfs_manage_static_block", kwargs={"id": sb.id})
    except IndexError:
        url = reverse("lfs_add_static_block")

    return HttpResponseRedirect(url)


@permission_required("core.manage_shop", login_url="/login/")
def manage_static_block(request, id, template_name="manage/static_block/static_block.html"):
    """Displays the main form to manage static blocks.
    """
    sb = get_object_or_404(StaticBlock, pk=id)
    if request.method == "POST":
        form = StaticBlockForm(instance=sb, data=request.POST)
        if form.is_valid():
            form.save()
            return lfs.core.utils.set_message_cookie(
                url=reverse("lfs_manage_static_block", kwargs={"id": sb.id}),
                msg=_(u"Static block has been saved."),
            )
    else:
        form = StaticBlockForm(instance=sb)

    return render_to_response(template_name, RequestContext(request, {
        "static_block": sb,
        "static_blocks": StaticBlock.objects.all(),
        "files": files(request, sb),
        "form": form,
        "current_id": int(id),
    }))


@permission_required("core.manage_shop", login_url="/login/")
def files(request, sb, template_name="manage/static_block/files.html"):
    """Displays the files tab of the passed static block.
    """
    return render_to_string(template_name, RequestContext(request, {
        "static_block": sb,
    }))


def update_files(request, id):
    """
    """
    static_block = lfs_get_object_or_404(StaticBlock, pk=id)

    action = request.POST.get("action")
    if action == "delete":
        message = _(u"Files has been deleted.")
        for key in request.POST.keys():
            if key.startswith("delete-"):
                try:
                    id = key.split("-")[1]
                    file = File.objects.get(pk=id).delete()
                except (IndexError, ObjectDoesNotExist):
                    pass

    elif action == "update":
        message = _(u"Files has been updated.")
        for key, value in request.POST.items():
            if key.startswith("title-"):
                id = key.split("-")[1]
                try:
                    file = File.objects.get(pk=id)
                except File.ObjectDoesNotExist:
                    pass
                else:
                    file.title = value
                    file.save()

            elif key.startswith("position-"):
                try:
                    id = key.split("-")[1]
                    file = File.objects.get(pk=id)
                except (IndexError, ObjectDoesNotExist):
                    pass
                else:
                    file.position = value
                    file.save()

    for i, file in enumerate(static_block.files.all()):
        file.position = (i + 1) * 10
        file.save()

    html = (
        ("#files", files(request, static_block)),
    )

    result = simplejson.dumps({
        "html": html,
        "message": message,
    }, cls=LazyEncoder)

    return HttpResponse(result)


def reload_files(request, id):
    """
    """
    static_block = lfs_get_object_or_404(StaticBlock, pk=id)
    result = files(request, static_block)

    result = simplejson.dumps({
        "files": result,
        "message": _(u"Files has been added."),
    }, cls=LazyEncoder)

    return HttpResponse(result)


def add_files(request, id):
    """Adds files to static block with passed id.
    """
    static_block = lfs_get_object_or_404(StaticBlock, pk=id)
    if request.method == "POST":
        for file_content in request.FILES.getlist("file"):
            file = File(content=static_block, title=file_content.name)
            file.file.save(file_content.name, file_content, save=True)

    ctype = ContentType.objects.get_for_model(static_block)

    # Refresh positions
    for i, file in enumerate(File.objects.filter(content_type=ctype, content_id=static_block.id)):
        file.position = (i + 1) * 10
        file.save()

    result = simplejson.dumps({"name": file_content.name, "type": "image/jpeg", "size": "123456789"})
    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
def add_static_block(request, template_name="manage/static_block/add_static_block.html"):
    """Provides a form to add a new static block.
    """
    if request.method == "POST":
        form = StaticBlockForm(data=request.POST)
        if form.is_valid():
            new_sb = form.save()
            return lfs.core.utils.set_message_cookie(
                url=reverse("lfs_manage_static_block", kwargs={"id": new_sb.id}),
                msg=_(u"Static block has been added."),
            )
    else:
        form = StaticBlockForm()

    return render_to_response(template_name, RequestContext(request, {
        "form": form,
        "static_blocks": StaticBlock.objects.all(),
    }))


@permission_required("core.manage_shop", login_url="/login/")
def preview_static_block(request, id, template_name="manage/static_block/preview.html"):
    """Displays a preview of an static block
    """
    sb = get_object_or_404(StaticBlock, pk=id)

    return render_to_response(template_name, RequestContext(request, {
        "static_block": sb,
    }))


@require_POST
@permission_required("core.manage_shop", login_url="/login/")
def delete_static_block(request, id):
    """Deletes static block with passed id.
    """
    sb = get_object_or_404(StaticBlock, pk=id)

    # First we delete all referencing categories. Otherwise they would be
    # deleted
    for category in sb.categories.all():
        category.static_block = None
        category.save()
    sb.delete()

    return lfs.core.utils.set_message_cookie(
        url=reverse("lfs_manage_static_blocks"),
        msg=_(u"Static block has been deleted."),
    )
