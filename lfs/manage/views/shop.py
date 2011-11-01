# django imports
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

# lfs imports
import lfs.core.utils
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.models import Shop
from lfs.core.signals import shop_changed
from lfs.core.utils import LazyEncoder
from lfs.core.widgets.image import LFSImageInput
from lfs.manage.views.lfs_portlets import portlets_inline


class ShopForm(ModelForm):
    """Form to edit shop data.
    """
    def __init__(self, *args, **kwargs):
        super(ShopForm, self).__init__(*args, **kwargs)
        self.fields["image"].widget = LFSImageInput()

    class Meta:
        model = Shop
        fields = ("name", "shop_owner", "from_email", "notification_emails",
            "description", "image", "static_block", "checkout_type", "confirm_toc",
            "google_analytics_id", "ga_site_tracking", "ga_ecommerce_tracking")


class ShopDefaultValuesForm(ModelForm):
    """
    """
    class Meta:
        model = Shop
        fields = ("price_calculator", "product_cols", "product_rows", "category_cols",
            "default_country", "invoice_countries", "shipping_countries", "default_locale", "use_international_currency_code")


@permission_required("core.manage_shop", login_url="/login/")
def manage_shop(request, template_name="manage/shop/shop.html"):
    """Displays the form to manage shop data.
    """
    shop = lfs_get_object_or_404(Shop, pk=1)
    if request.method == "POST":
        form = ShopForm(instance=shop, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            return lfs.core.utils.set_message_cookie(
                url=reverse("lfs_manage_shop"),
                msg=_(u"Shop data has been saved."),
            )
    else:
        form = ShopForm(instance=shop)

    return render_to_response(template_name, RequestContext(request, {
        "shop": shop,
        "form": form,
        "default_values": default_values_part(request),
        "portlets": portlets_inline(request, shop),
    }))


@permission_required("core.manage_shop", login_url="/login/")
def default_values_part(request, template_name="manage/shop/default_values.html"):
    """Displays the default value part of the shop form.
    """
    shop = lfs_get_object_or_404(Shop, pk=1)

    if request.method == "POST":
        form = ShopDefaultValuesForm(instance=shop, data=request.POST)
    else:
        form = ShopDefaultValuesForm(instance=shop)

    return render_to_string(template_name, RequestContext(request, {
        "shop": shop,
        "form": form,
    }))


def save_default_values(request):
    """Saves the default value part
    """
    shop = lfs_get_object_or_404(Shop, pk=1)
    form = ShopDefaultValuesForm(instance=shop, data=request.POST)

    if form.is_valid():
        shop = form.save()
        shop_changed.send(shop)
        message = _(u"Shop default values have been saved.")
    else:
        message = _(u"Please correct the indicated errors.")

    html = [["#default-values", default_values_part(request)]]

    result = simplejson.dumps({
        "html": html,
        "message": message
    }, cls=LazyEncoder)

    return HttpResponse(result)
