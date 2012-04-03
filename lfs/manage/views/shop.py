# django imports
from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST

# lfs imports
import lfs.core.utils
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.models import Shop
from lfs.core.signals import shop_changed
from lfs.core.utils import import_module
from lfs.core.utils import import_symbol
from lfs.core.utils import LazyEncoder
from lfs.core.widgets.image import LFSImageInput
from lfs.manage.views.lfs_portlets import portlets_inline


class ShopDataForm(ModelForm):
    """Form to edit shop data.
    """
    def __init__(self, *args, **kwargs):
        super(ShopDataForm, self).__init__(*args, **kwargs)
        self.fields["image"].widget = LFSImageInput()

    class Meta:
        model = Shop
        fields = ("name", "shop_owner", "from_email", "notification_emails",
            "description", "image", "static_block", "checkout_type", "confirm_toc",
            "google_analytics_id", "ga_site_tracking", "ga_ecommerce_tracking")


class ShopSEOForm(ModelForm):
    """Form to edit shop SEO data.
    """
    class Meta:
        model = Shop
        fields = ("meta_title", "meta_keywords", "meta_description")


class ShopDefaultValuesForm(ModelForm):
    """Form to edit shop default values.
    """
    class Meta:
        model = Shop
        fields = ("price_calculator", "product_cols", "product_rows", "category_cols",
            "default_country", "invoice_countries", "shipping_countries", "default_locale", "use_international_currency_code")


@permission_required("core.manage_shop", login_url="/login/")
def manage_shop(request, template_name="manage/shop/shop.html"):
    """Displays the form to manage shop data.
    """
    shop = lfs.core.utils.get_default_shop()
    data_form = ShopDataForm(instance=shop)
    seo_form = ShopSEOForm(instance=shop)
    default_values_form = ShopDefaultValuesForm(instance=shop)

    ong = lfs.core.utils.import_symbol(settings.LFS_ORDER_NUMBER_GENERATOR)

    try:
        order_number = ong.objects.get(id="order_number")
    except ong.DoesNotExist:
        order_number = ong.objects.create(id="order_number")
    order_numbers_form = order_number.get_form(instance=order_number)

    return render_to_response(template_name, RequestContext(request, {
        "shop": shop,
        "data": data_tab(request, shop, data_form),
        "default_values": default_values_tab(request, shop, default_values_form),
        "order_numbers": order_numbers_tab(request, shop, order_numbers_form),
        "seo": seo_tab(request, shop, seo_form),
        "portlets": portlets_inline(request, shop),
    }))


# Parts
def data_tab(request, shop, form, template_name="manage/shop/data_tab.html"):
    """Renders the data tab of the shop.
    """
    return render_to_string(template_name, RequestContext(request, {
        "shop": shop,
        "form": form,
    }))


def order_numbers_tab(request, shop, form, template_name="manage/order_numbers/order_numbers_tab.html"):
    """Renders the ordern number tab of the shop.
    """
    return render_to_string(template_name, RequestContext(request, {
        "shop": shop,
        "form": form,
    }))


def default_values_tab(request, shop, form, template_name="manage/shop/default_values_tab.html"):
    """Renders the default value tab of the shop.
    """
    return render_to_string(template_name, RequestContext(request, {
        "shop": shop,
        "form": form,
    }))


def seo_tab(request, shop, form, template_name="manage/shop/seo_tab.html"):
    """Renders the SEO tab of the shop.
    """
    return render_to_string(template_name, RequestContext(request, {
        "shop": shop,
        "form": form,
    }))


# Actions
@permission_required("core.manage_shop", login_url="/login/")
@require_POST
def save_data_tab(request):
    """Saves the data tab of the default shop.
    """
    shop = lfs.core.utils.get_default_shop()

    form = ShopDataForm(instance=shop, data=request.POST, files=request.FILES)
    if form.is_valid():
        form.save()

        # Delete image
        if request.POST.get("delete_image"):
            shop.image.delete()

        # reinitialize form in order to properly display uploaded image
        form = ShopDataForm(instance=shop)
        shop_changed.send(shop)
        message = _(u"Shop data has been saved.")
    else:
        message = _(u"Please correct the indicated errors.")

    result = simplejson.dumps({
        "html": [["#data", data_tab(request, shop, form)]],
        "message": message,
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
@require_POST
def save_default_values_tab(request):
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

    result = simplejson.dumps({
        "html": [["#default_values", default_values_tab(request, shop, form)]],
        "message": message
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
@require_POST
def save_seo_tab(request):
    """Saves the seo tab of the default shop.
    """
    shop = lfs.core.utils.get_default_shop()

    form = ShopSEOForm(instance=shop, data=request.POST)
    if form.is_valid():
        form.save()
        shop_changed.send(shop)
        message = _(u"Shop SEO data has been saved.")
    else:
        message = _(u"Please correct the indicated errors.")

    result = simplejson.dumps({
        "html": [["#seo", seo_tab(request, shop, form)]],
        "message": message,
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
@require_POST
def save_order_numbers_tab(request):
    """Saves the order number tab of the default shop.
    """
    shop = lfs.core.utils.get_default_shop()

    ong = import_symbol(settings.LFS_ORDER_NUMBER_GENERATOR)
    order_number = ong.objects.get(id="order_number")
    form = order_number.get_form(instance=order_number, data=request.POST)

    if form.is_valid():
        form.save()
        shop_changed.send(shop)
        message = _(u"Order numbers has been saved.")
    else:
        message = _(u"Please correct the indicated errors.")

    result = simplejson.dumps({
        "html": [["#order_numbers", order_numbers_tab(request, shop, form)]],
        "message": message,
    }, cls=LazyEncoder)

    return HttpResponse(result)
