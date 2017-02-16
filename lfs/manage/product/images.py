import json

# django imports
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

# lfs.imports
import lfs.core.utils
from lfs.caching.utils import lfs_get_object_or_404
from lfs.catalog.models import Image
from lfs.catalog.models import Product
from lfs.core.signals import product_changed
from lfs.core.utils import LazyEncoder

# Load logger
import logging
logger = logging.getLogger(__name__)


@permission_required("core.manage_shop")
def manage_images(request, product_id, as_string=False, template_name="manage/product/images.html"):
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
            "images": result,
            "message": _(u"Images have been added."),
        }, cls=LazyEncoder)

        return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def list_images(request, product_id, as_string=False, template_name="manage/product/images-list.html"):
    """
    """
    result = manage_images(request, product_id, as_string=True, template_name=template_name)

    if as_string:
        return result
    else:
        result = json.dumps({
            "images": result,
            "message": _(u"Images have been added."),
        }, cls=LazyEncoder)

        return HttpResponse(result, content_type='application/json')


# Actions
@permission_required("core.manage_shop")
def add_image(request, product_id):
    """Adds an image to product with passed product_id.
    """
    product = lfs_get_object_or_404(Product, pk=product_id)
    if request.method == "POST":
        for file_content in request.FILES.getlist("files[]"):
            image = Image(content=product, title=file_content.name)
            try:
                image.image.save(file_content.name, file_content, save=True)
            except Exception, e:
                logger.info("Upload image: %s %s" % (file_content.name, e))
                continue

    # Refresh positions
    for i, image in enumerate(product.images.all()):
        image.position = (i + 1) * 10
        image.save()

    product_changed.send(product, request=request)

    result = json.dumps({"name": file_content.name, "type": "image/jpeg", "size": "123456789"})
    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def update_images(request, product_id):
    """Saves/deletes images with given ids (passed by request body).
    """
    product = lfs_get_object_or_404(Product, pk=product_id)

    action = request.POST.get("action")
    if action == "delete":
        message = _(u"Images has been deleted.")
        for key in request.POST.keys():
            if key.startswith("delete-"):
                try:
                    id = key.split("-")[1]
                    image = Image.objects.get(pk=id).delete()
                except (IndexError, ObjectDoesNotExist):
                    pass

    elif action == "update":
        message = _(u"Images has been updated.")
        for key, value in request.POST.items():
            if key.startswith("title-"):
                id = key.split("-")[1]
                try:
                    image = Image.objects.get(pk=id)
                except ObjectDoesNotExist:
                    pass
                else:
                    image.title = value
                    image.save()

            elif key.startswith("alt-"):
                id = key.split("-")[1]
                try:
                    image = Image.objects.get(pk=id)
                except ObjectDoesNotExist:
                    pass
                else:
                    image.alt = value
                    image.save()

            elif key.startswith("position-"):
                try:
                    id = key.split("-")[1]
                    image = Image.objects.get(pk=id)
                except (IndexError, ObjectDoesNotExist):
                    pass
                else:
                    image.position = value
                    image.save()

    # Refresh positions
    for i, image in enumerate(product.images.all()):
        image.position = (i + 1) * 10
        image.save()

    product_changed.send(product, request=request)

    html = [["#images-list", list_images(request, product_id, as_string=True)]]
    result = json.dumps({
        "html": html,
        "message": message,
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def move_image(request, id):
    """Moves the image with passed id up or down.

    **Parameters:**

        id
            The id of the image which should be edited.

    **Query String:**

        direction
            The direction in which the image should be moved. One of 0 (up)
            or 1 (down).

    **Permission:**

        edit (of the belonging content object)
    """
    image = Image.objects.get(pk=id)
    product = image.content

    direction = request.GET.get("direction", 0)

    if direction == "1":
        image.position += 15
    else:
        image.position -= 15
        if image.position < 0:
            image.position = 10

    image.save()

    # Refresh positions
    for i, image in enumerate(product.images.all()):
        image.position = (i + 1) * 10
        image.save()

    product_changed.send(product, request=request)

    html = [["#images-list", list_images(request, product.id, as_string=True)]]

    result = json.dumps({
        "html": html,
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def update_active_images(request, product_id):
    """Updates the images activity state for product variants.
    """
    product = Product.objects.get(pk=product_id)
    if request.POST.get("active_images"):
        product.active_images = True
    else:
        product.active_images = False
    product.save()

    return lfs.core.utils.set_message_cookie(
        url=reverse("lfs_manage_product", kwargs={"product_id": product.id}),
        msg=_(u"Active images has been updated."),
    )
