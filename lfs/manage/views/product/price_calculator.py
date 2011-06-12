# django imports
from django.contrib.auth.decorators import permission_required
from django import forms
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

# lfs.imports
from lfs.caching.utils import lfs_get_object_or_404
from lfs.catalog.models import Product
from lfs.core.utils import LazyEncoder
import lfs.core.settings as lfs_settings

class PriceCalculatorForm(forms.Form):
    """Form to select price_calculator property of a product.
    """
    price_calculator = forms.ChoiceField(choices=lfs_settings.LFS_PRICE_CALCULATOR_CHOICES)
    
@permission_required("core.manage_shop", login_url="/login/")
def manage_price_calculator(request, product_id, template_name="manage/product/price_calculator.html"):
    """
    """
    product = lfs_get_object_or_404(Product, pk=product_id)

    if request.method == "POST":
        form = PriceCalculatorForm(data=request.POST)
        if form.is_valid():
            product.price_calculator = form.cleaned_data.get('price_calculator', lfs_settings.LFS_DEFAULT_PRICE_CALCULATOR)
            product.save()
    else:
        initial = {'price_calculator': product.price_calculator}
        form = PriceCalculatorForm(initial)

    result = render_to_string(template_name, RequestContext(request, {
        "product" : product,
        "form" : form,
    }))

    if request.is_ajax():
        return HttpResponse(simplejson.dumps({
            "price_calculator_inline" : result,
            "message" : _(u"Price calculator data has been saved."),
        }, cls = LazyEncoder))
    else:
        return result