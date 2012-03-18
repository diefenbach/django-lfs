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
from lfs.core.utils import LazyEncoder
from lfs.catalog.models import Category


class SEOForm(ModelForm):
    """Form to add/edit seo properties of a category.
    """
    class Meta:
        model = Category
        fields = ("meta_title", "meta_keywords", "meta_description")


@permission_required("core.manage_shop", login_url="/login/")
def edit_seo(request, category_id, template_name="manage/category/seo.html"):
    """Displays an edit form for category seo fields and saves the entered
    values.

    If it is called by an ajax request it returns the result and a status
    message as json.

    This is used as a part of the whole category form.
    """
    category = lfs_get_object_or_404(Category, pk=category_id)

    if request.method == "POST":
        form = SEOForm(instance=category, data=request.POST)
        if form.is_valid():
            form.save()
            message = _(u"SEO data has been saved.")
        else:
            message = _(u"Please correct the indicated errors.")
    else:
        form = SEOForm(instance=category)

    seo_html = render_to_string(template_name, RequestContext(request, {
        "category": category,
        "form": form,
    }))

    if request.is_ajax():
        return HttpResponse(simplejson.dumps({
            "seo": seo_html,
            "message": message,
        }, cls=LazyEncoder))
    else:
        return seo_html
