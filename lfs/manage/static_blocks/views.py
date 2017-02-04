import json

# django imports
from django.contrib.auth.decorators import permission_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST

# lfs imports
import lfs.core.utils
from lfs.core.utils import LazyEncoder
from lfs.caching.utils import lfs_get_object_or_404
from lfs.catalog.models import StaticBlock
from lfs.catalog.models import File
from lfs.manage.static_blocks.forms import StaticBlockForm


# views
@permission_required("core.manage_shop")
def manage_static_blocks(request):
    """Dispatches to the first static block or to the add static block form.
    """
    try:
        sb = StaticBlock.objects.all()[0]
        url = reverse("lfs_manage_static_block", kwargs={"id": sb.id})
    except IndexError:
        url = reverse("lfs_manage_no_static_blocks")

    return HttpResponseRedirect(url)


@permission_required("core.manage_shop")
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

    return render(request, template_name, {
        "static_block": sb,
        "static_blocks": StaticBlock.objects.all(),
        "files": files(request, sb),
        "form": form,
        "current_id": int(id),
    })


@permission_required("core.manage_shop")
def no_static_blocks(request, template_name="manage/static_block/no_static_blocks.html"):
    """Displays that no static blocks exist.
    """
    return render(request, template_name, {})


# parts
@permission_required("core.manage_shop")
def files(request, sb, template_name="manage/static_block/files.html"):
    """Displays the files tab of the passed static block.
    """
    return render_to_string(template_name, request=request, context={
        "static_block": sb,
    })


@permission_required("core.manage_shop")
def list_files(request, sb, template_name="manage/static_block/files-list.html"):
    """Displays the files tab of the passed static block.
    """
    return files(request, sb, template_name=template_name)


# actions
@permission_required("core.manage_shop")
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
        ("#files-list", list_files(request, static_block)),
    )

    result = json.dumps({
        "html": html,
        "message": message,
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def reload_files(request, id):
    """
    """
    static_block = lfs_get_object_or_404(StaticBlock, pk=id)
    result = list_files(request, static_block)

    result = json.dumps({
        "html": result,
        "message": _(u"Files has been added."),
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def add_files(request, id):
    """Adds files to static block with passed id.
    """
    static_block = lfs_get_object_or_404(StaticBlock, pk=id)
    if request.method == "POST":
        for file_content in request.FILES.getlist("files[]"):
            file = File(content=static_block, title=file_content.name)
            file.file.save(file_content.name, file_content, save=True)

    ctype = ContentType.objects.get_for_model(static_block)

    # Refresh positions
    for i, file in enumerate(File.objects.filter(content_type=ctype, content_id=static_block.id)):
        file.position = (i + 1) * 10
        file.save()

    result = json.dumps({"name": file_content.name, "type": "image/jpeg", "size": "123456789"})
    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
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

    return render(request, template_name, {
        "form": form,
        "static_blocks": StaticBlock.objects.all(),
        "came_from": (request.POST if request.method == 'POST' else request.GET).get("came_from",
                                                                                     reverse("lfs_manage_static_blocks")),
    })


@permission_required("core.manage_shop")
def preview_static_block(request, id, template_name="manage/static_block/preview.html"):
    """Displays a preview of an static block
    """
    sb = get_object_or_404(StaticBlock, pk=id)

    return render(request, template_name, {
        "static_block": sb,
    })


@permission_required("core.manage_shop")
@require_POST
def sort_static_blocks(request):
    """Sorts static blocks after drag 'n drop.
    """
    static_blocks = request.POST.get("objs", "").split('&')
    assert (isinstance(static_blocks, list))
    if len(static_blocks) > 0:
        position = 10
        for sb_str in static_blocks:
            sb_id = sb_str.split('=')[1]
            sb_obj = StaticBlock.objects.get(pk=sb_id)
            sb_obj.position = position
            sb_obj.save()
            position = position + 10

        result = json.dumps({
            "message": _(u"The static blocks have been sorted."),
        }, cls=LazyEncoder)

        return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
@require_POST
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
