# django imports
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.utils import LazyEncoder
from lfs.core.signals import category_changed
from lfs.catalog.models import Product
from lfs.catalog.models import Category


@permission_required("core.manage_shop", login_url="/login/")
def manage_categories(request, product_id, template_name="manage/product/categories.html"):
    """Displays the manage category view.
    """
    product = lfs_get_object_or_404(Product, pk=product_id)
    product_category_ids = [p.id for p in product.get_categories()]

    categories = []
    for category in Category.objects.filter(parent=None):

        children = children_categories(request, category, product_category_ids)

        categories.append({
            "id": category.id,
            "slug": category.slug,
            "name": category.name,
            "url": category.get_absolute_url(),
            "checked": category.id in product_category_ids,
            "children": children,
        })

    result = render_to_string(template_name, RequestContext(request, {
        "product": product,
        "categories": categories
    }))

    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
def children_categories(request, category, product_category_ids,
    template_name="manage/product/categories_children.html"):
    """Renders the children categories of given category as HTML.
    """
    categories = []
    for category in category.category_set.all():

        children = children_categories(request, category, product_category_ids)

        categories.append({
            "id": category.id,
            "slug": category.slug,
            "name": category.name,
            "url": category.get_absolute_url(),
            "checked": category.id in product_category_ids,
            "children": children,
        })

    result = render_to_string(template_name, RequestContext(request, {
        "categories": categories
    }))

    return result


# Actions
@permission_required("core.manage_shop", login_url="/login/")
def change_categories(request, product_id):
    """Changes categories by passed request body.
    """
    product = lfs_get_object_or_404(Product, pk=product_id)

    # Signal that the old categories of the product have been changed.
    for category in product.categories.all():
        category_changed.send(category)

    if request.method == "POST":
        product.categories = request.POST.getlist("categories")
        product.save()

    # Signal that the new categories of the product have been changed.
    for category in product.categories.all():
        category_changed.send(category)

    return HttpResponse(simplejson.dumps({
        "message": _(u"Categories have been saved."),
    }, cls=LazyEncoder))
