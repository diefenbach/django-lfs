# django imports
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

# lfs imports
import lfs.caching.utils
import lfs.core.utils
import lfs.catalog.models

@permission_required("manage_shop", login_url="/login/")
def utilities(request, template_name="manage/utils.html"):
    """Displays the utility view.
    """
    return render_to_response(template_name, RequestContext(request, {}))
    
def clear_cache(request):
    """Clears the whole cache.
    """
    lfs.caching.utils.clear_cache()
    return lfs.core.utils.set_message_cookie(
        url = reverse("lfs_manage_utils"),
        msg = _(u"Cache has been cleared."),
    )

def set_category_levels(request):
    """Sets the category levels based on the position in category hierarchy.
    """
    lfs.core.utils.set_category_levels()
    return lfs.core.utils.set_message_cookie(
        url = reverse("lfs_manage_utils"),
        msg = _(u"Categoy levels have been created."),
    )
    
def update_effective_price(request):
    """Saves the price or sale price to effective price.
    """
    for product in lfs.catalog.models.Product.objects.all():
        product.save()
        
    return lfs.core.utils.set_message_cookie(
        url = reverse("lfs_manage_utils"),
        msg = _(u"Effective prices have been set."),
    )
        