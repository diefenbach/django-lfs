import json

# django imports
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

# lfs.imports
from lfs.caching.utils import lfs_get_object_or_404
from lfs.catalog.models import ProductAttachment
from lfs.catalog.models import Product
from lfs.core.signals import product_changed
from lfs.core.utils import LazyEncoder


@permission_required("core.manage_shop")
def manage_attachments(request, product_id, as_string=False, template_name="manage/product/attachments.html"):
    """
    """
    product = lfs_get_object_or_404(Product, pk=product_id)

    result = render_to_string(template_name, request=request, context={
        "product": product,
    })

    if as_string:
        return result
    else:
        result = json.dumps({
            "attachments": result,
            "message": _(u"Attachments have been added."),
        }, cls=LazyEncoder)

        return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def list_attachments(request, product_id, as_string=False, template_name="manage/product/attachments-list.html"):
    """
    """
    result = manage_attachments(request, product_id, as_string=True, template_name=template_name)
    if as_string:
        return result
    else:
        result = json.dumps({
            "html": result,
            "message": _(u"Attachments have been added."),
        }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


# Actions
@permission_required("core.manage_shop")
def add_attachment(request, product_id):
    """Adds an attachment to product with passed product_id.
    """
    product = lfs_get_object_or_404(Product, pk=product_id)
    if request.method == "POST":
        for file_content in request.FILES.getlist("files[]"):
            attachment = ProductAttachment(product=product, title=file_content.name[:50])
            attachment.file.save(file_content.name, file_content, save=True)

    # Refresh positions
    for i, attachment in enumerate(product.attachments.all()):
        attachment.position = (i + 1) * 10
        attachment.save()

    product_changed.send(product, request=request)
    return manage_attachments(request, product_id)


@permission_required("core.manage_shop")
def update_attachments(request, product_id):
    """Saves/deletes attachments with given ids (passed by request body).
    """
    product = lfs_get_object_or_404(Product, pk=product_id)
    action = request.POST.get("action")
    message = _(u"Attachment has been updated.")

    if action == "delete":
        message = _(u"Attachment has been deleted.")
        for key in request.POST.keys():
            if key.startswith("delete-"):
                try:
                    id = key.split("-")[1]
                    attachment = ProductAttachment.objects.get(pk=id).delete()
                except (IndexError, ObjectDoesNotExist):
                    pass
    elif action == "update":
        message = _(u"Attachment has been updated.")
        for attachment in product.attachments.all():
            attachment.title = request.POST.get("title-%s" % attachment.id)[:50]
            attachment.position = request.POST.get("position-%s" % attachment.id)
            attachment.description = request.POST.get("description-%s" % attachment.id)
            attachment.save()

    # Refresh positions
    for i, attachment in enumerate(product.attachments.all()):
        attachment.position = (i + 1) * 10
        attachment.save()

    product_changed.send(product, request=request)

    html = [["#attachments-list", list_attachments(request, product_id, as_string=True)]]
    result = json.dumps({
        "html": html,
        "message": message,
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def move_attachment(request, id):
    """Moves the attachment with passed id up or down.

    **Parameters:**

        id
            The id of the attachment which should be edited.

    **Query String:**

        direction
            The direction in which the attachment should be moved. One of 0 (up)
            or 1 (down).

    **Permission:**

        edit (of the belonging content object)
    """
    attachment = ProductAttachment.objects.get(pk=id)
    product = attachment.product

    direction = request.GET.get("direction", 0)

    if direction == "1":
        attachment.position += 15
    else:
        attachment.position -= 15
        if attachment.position < 0:
            attachment.position = 10

    attachment.save()

    # Refresh positions
    for i, attachment in enumerate(product.attachments.all()):
        attachment.position = (i + 1) * 10
        attachment.save()

    html = [["#attachments-list", list_attachments(request, product.id, as_string=True)]]

    result = json.dumps({
        "html": html,
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')
