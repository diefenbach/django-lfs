# django imports
from django.contrib.auth.decorators import permission_required
from django.forms import ModelForm
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

# lfs.imports
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.utils import LazyEncoder
from lfs.catalog.models import Category
from lfs.catalog.settings import CATEGORY_TEMPLATES
from lfs.utils.widgets import SelectImage


class ViewForm(ModelForm):
    """Form to add/edit category.
    """
    def __init__(self, *args, **kwargs):
        super(ViewForm, self).__init__(*args, **kwargs)
        self.fields["template"].widget = SelectImage(choices=CATEGORY_TEMPLATES)

    class Meta:
        model = Category
        fields = ("template", "show_all_products", "active_formats",
            "product_cols", "product_rows", "category_cols", )


@permission_required("core.manage_shop")
def category_view(request, category_id, template_name="manage/category/view.html"):
    """Displays the view data for the category with passed category id.

    This is used as a part of the whole category form.
    """
    category = lfs_get_object_or_404(Category, pk=category_id)

    if request.method == "POST":
        form = ViewForm(instance=category, data=request.POST)
        if form.is_valid():
            form.save()
            message = _(u"View data has been saved.")
        else:
            message = _(u"Please correct the indicated errors.")
    else:
        form = ViewForm(instance=category)

    view_html = render_to_string(template_name, RequestContext(request, {
        "category": category,
        "form": form,
    }))

    if request.is_ajax():
        html = [["#view", view_html]]
        return HttpResponse(simplejson.dumps({
            "html": html,
            "message": message,
        }, cls=LazyEncoder), mimetype='application/json')
    else:
        return view_html


@permission_required("core.manage_shop")
def no_categories(request, template_name="manage/category/no_categories.html"):
    """Displays that there are no categories.
    """
    return render_to_response(template_name, RequestContext(request, {}))

