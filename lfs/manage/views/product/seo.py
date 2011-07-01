# django imports
from django.contrib.auth.decorators import permission_required
from django.forms import ModelForm
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

# lfs.imports
from lfs.caching.utils import lfs_get_object_or_404
from lfs.catalog.models import Product
from lfs.core.utils import LazyEncoder


class SEOForm(ModelForm):
    """Form to add/edit seo properties of a product.
    """
    class Meta:
        model = Product
        fields = (
            "active_meta_title", "meta_title",
            "active_meta_keywords", "meta_keywords",
            "active_meta_description", "meta_description",
        )


@permission_required("core.manage_shop", login_url="/login/")
def manage_seo(request, product_id, template_name="manage/product/seo.html"):
    """
    """
    product = lfs_get_object_or_404(Product, pk=product_id)

    if request.method == "POST":
        form = SEOForm(instance=product, data=request.POST)
        if form.is_valid():
            form.save()
    else:
        form = SEOForm(instance=product)

    result = render_to_string(template_name, RequestContext(request, {
        "product": product,
        "form": form,
    }))

    if request.is_ajax():
        return HttpResponse(simplejson.dumps({
            "message": _(u"Seo data has been saved."),
        }, cls=LazyEncoder))
    else:
        return result
