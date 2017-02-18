from django import template
from django.template.loader import render_to_string

from lfs.catalog.models import Category
from lfs.manufacturer.models import Manufacturer

register = template.Library()


@register.inclusion_tag('manage/category/category_filter.html', takes_context=True)
def category_filter(context, css_class="", name="category"):
    """Returns the categories of the shop for management purposes.

    The css_class attribute is used for different ajax based requests in
    different views.
    """
    request = context.get("request")
    selected = request.session.get("product_filters", {}).get("category")
    categories = []
    for category in Category.objects.filter(parent=None):
        children = category_filter_children(request, category, name)
        categories.append({
            "id": category.id,
            "name": category.name,
            "children": children,
            "selected": str(category.id) == selected,
        })

    result = {"categories": categories, "css_class": css_class, "name": name, "selected": selected}
    return result


# NOTE: The reason why not to use another inclusion_tag is that the request is
# not available within an inclusion_tag if one inclusion_tag is called by
# another. (Don't know why yet.)
def category_filter_children(request, category, name="category_filter", level=1):
    """Returns the children of the given category as HTML.
    """
    categories = []
    for category in category.category_set.all():
        children = category_filter_children(request, category, name, level + 1)
        categories.append({
            "id": category.id,
            "name": "%s%s" % ("&nbsp;" * level * 5, category.name),
            "children": children,
            "level": level,
            "selected": str(category.id) == request.session.get("product_filters", {}).get("category")
        })

    result = render_to_string("manage/category/category_filter_children.html", request=request, context={
        "categories": categories
    })

    return result


@register.inclusion_tag('manage/manufacturers/manufacturer_filter.html', takes_context=True)
def manufacturer_filter(context, css_class="", name="manufacturer"):
    """Returns the categories of the shop for management purposes.

    The css_class attribute is used for different ajax based requests in
    different views.
    """
    request = context.get("request")
    selected = request.session.get("product_filters", {}).get("manufacturer")
    manufacturers = []
    for manufacturer in Manufacturer.objects.all():
        manufacturers.append({
            "id": manufacturer.id,
            "name": manufacturer.name,
            "selected": str(manufacturer.id) == selected,
        })

    result = {"manufacturers": manufacturers, "css_class": css_class, "name": name, "selected": selected}
    return result
