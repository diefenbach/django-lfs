# python imports
import sys
import traceback

# django imports
from django.conf import settings
from django.core.mail import EmailMessage
from django.http import HttpResponseServerError
from django.shortcuts import render
from django.template import loader

# lfs imports
from django.views.generic import TemplateView
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.models import Shop

# Load logger
import logging

logger = logging.getLogger(__name__)


def shop_view(request, template_name="lfs/shop/shop.html"):
    """Displays the shop."""
    # TODO: this is not necessary here as we have context processor that sets 'SHOP' variable
    #       this should be removed at some point but is here for backward compatibility
    shop = lfs_get_object_or_404(Shop, pk=1)
    return render(
        request,
        template_name,
        context={
            "shop": shop,
        },
    )


def server_error(request):
    """Own view in order to send an error message."""
    exc_type, exc_info, tb = sys.exc_info()
    response = "%s\n" % exc_type.__name__
    response += "%s\n" % exc_info
    response += "TRACEBACK:\n"
    for tb in traceback.format_tb(tb):
        response += "%s\n" % tb

    if request.user:
        response += "User: %s\n" % request.user.username

    response += "\nREQUEST:\n%s" % request

    try:
        from_email = settings.ADMINS[0][1]
        to_emails = [a[1] for a in settings.ADMINS]
    except IndexError:
        pass
    else:
        mail = EmailMessage(subject="Error LFS", body=response, from_email=from_email, to=to_emails)
        mail.send(fail_silently=True)

    t = loader.get_template("500.html")
    return HttpResponseServerError(t.render(request=request))


class TextTemplateView(TemplateView):
    def render_to_response(self, context, **kwargs):
        return super(TextTemplateView, self).render_to_response(context, content_type="text/plain", **kwargs)
