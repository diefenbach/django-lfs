# django imports
from django.contrib.admin import widgets
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.manage.views.marketing.topseller import manage_topseller
from lfs.manage.views.marketing.featured import manage_featured


@permission_required("core.manage_shop", login_url="/login/")
def manage_marketing(request, template_name="manage/marketing/marketing.html"):
    """Displays the main manage/edit form for marketing.
    """
    topseller = manage_topseller(request)

    return render_to_response(template_name, RequestContext(request, {
        "topseller": topseller,
    }))


@permission_required("manage_shop", login_url="/login/")
def manage_featured_page(request, template_name="manage/marketing/marketing_featured.html"):
    """Displays the main manage/edit form for featured products.
    """
    featured = manage_featured(request)

    return render_to_response(template_name, RequestContext(request, {
        "featured": featured,
    }))
