# django imports
from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.template.loader import render_to_string
from django.core.cache import cache

# lfs imports
from lfs.catalog.models import Category


@permission_required("core.manage_shop")
def manage_categories_portlet(request, category_id, template_name="manage/category/manage_categories_portlet.html"):
    """Returns a management portlet of all categories.
    """
    cache_key = "%s-%s-manage-category-portlet" % (category_id, settings.CACHE_MIDDLEWARE_KEY_PREFIX)
    result = cache.get(cache_key)
    if result is not None:
        return result

    categories = []
    for category in Category.objects.filter(parent=None):
        children = categories_portlet_children(request, category)
        categories.append({
            "id": category.id,
            "slug": category.slug,
            "name": category.name,
            "url": category.get_absolute_url(),
            "children": children,
            "is_current": _is_current_category(request, category),
        })

    return render_to_string(template_name, request=request, context={
        "categories": categories,
        "category_id": category_id,
    })

    cache.set(cache_key, result)
    return result


@permission_required("core.manage_shop")
def categories_portlet_children(request, category):
    """Returns the children of the given category as HTML.
    """
    categories = []
    for child_category in category.category_set.all():
        children = categories_portlet_children(request, child_category)
        categories.append({
            "id": child_category.id,
            "slug": child_category.slug,
            "name": child_category.name,
            "url": child_category.get_absolute_url(),
            "children": children,
            "is_current": _is_current_category(request, child_category),
        })

    result = render_to_string("manage/category/manage_categories_portlet_children.html", request=request, context={
        "category": category,
        "categories": categories
    })

    return result


def _is_current_category(request, category):
    """Returns True if the passed category is the current category.
    """
    id = request.path.split("/")[-1]
    return str(category.id) == id
