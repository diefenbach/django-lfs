# python imports
import re
import urlparse

# django imports
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.views.decorators.http import require_POST
from django.utils.translation import ugettext as _

# lfs imports
from lfs.catalog.models import Image
from lfs.catalog.settings import THUMBNAIL_SIZES
from lfs.core.utils import LazyEncoder

# Load logger
import logging
logger = logging.getLogger("default")

# views
@permission_required("core.manage_shop", login_url="/login/")
def images(request, template_name="manage/images/images.html"):
    """
    Display images management.
    """
    result = render_to_string(template_name, RequestContext(request, {
        "images": Image.objects.all()
    }))

    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
@require_POST
def delete_images(request):
    """
    Deletes images which are passed via HTTP query.
    """
    Image.objects.filter(pk__in=request.POST.getlist("images")).delete()
    return HttpResponseRedirect(reverse("lfs_manage_global_images"))


@permission_required("core.manage_shop", login_url="/login/")
def add_images(request):
    """
    Adds a global images.
    """
    if request.method == "POST":
        for file_content in request.FILES.getlist("file"):
            image = Image(title=file_content.name)
            try:
                image.image.save(file_content.name, file_content, save=True)
            except Exception, e:
                image.delete()
                logger.info("Upload of image failed: %s %s" % (file_content.name, e))
                continue

    result = simplejson.dumps({"name": file_content.name, "type": "image/jpeg", "size": "123456789"})
    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
def imagebrowser(request, template_name="manage/images/filebrowser_images.html"):
    """
    Displays a browser for images.
    """
    selected_size = None
    selected_image = None
    selected_class = request.GET.get("class")
    url = request.GET.get("url")

    if url:
        parsed_url = urlparse.urlparse(url)
        try:
            temp_url = "/".join(parsed_url.path.split("/")[2:])
            result = re.search("(.*)(\.)(\d+x\d+)(.*)", temp_url)
            if result:
                temp_url = result.groups()[0] + result.groups()[3]
                selected_image = Image.objects.get(image=temp_url)
                selected_size = result.groups()[2]
            else:
                value = None
                title = None
                selected_size = None

        except (IndexError, Image.DoesNotExist):
            pass

    sizes = []
    for size in THUMBNAIL_SIZES:
        size = "%sx%s" % (size[0], size[1])
        sizes.append({
            "value": size,
            "title": size,
            "selected": size == selected_size,
        })

    classes = [{"value": 'inline',
                "title": _(u'inline'),
                "selected": 'inline' == selected_class},
               {"value": 'left',
                "title": _(u'left'),
                "selected": 'left' == selected_class},
               {"value": 'right',
                "title": _(u'right'),
                "selected": 'right' == selected_class}]

    images = []
    for image in Image.objects.all():
        images.append({
            "id": image.id,
            "title": image.title,
            "checked": image == selected_image,
            "url": image.image.url_100x100,
        })

    html = render_to_string(template_name, RequestContext(request, {
        "sizes": sizes,
        "classes": classes,
        "images": images,
    }))

    result = simplejson.dumps({
        "html": html,
        "message": "msg",
    }, cls=LazyEncoder)

    return HttpResponse(result)
