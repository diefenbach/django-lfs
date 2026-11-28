from django import template
from django.template.loader import render_to_string
from django.utils.translation import gettext
from django.utils.translation import pgettext_lazy

from lfs.catalog.models import Category
from lfs.manufacturer.models import Manufacturer

register = template.Library()

# Labels of the tabs whose views pass only a key, with the context "tab" ("View" is a noun here, not "to view").
# Product tabs carry their own label (lfs.manage.products.tabs).
TAB_LABELS = {
    "carousel": pgettext_lazy("tab", "Carousel"),
    "data": pgettext_lazy("tab", "Data"),
    "default_values": pgettext_lazy("tab", "Default Values"),
    "list": pgettext_lazy("tab", "List"),
    "order_numbers": pgettext_lazy("tab", "Order Numbers"),
    "portlets": pgettext_lazy("tab", "Portlets"),
    "products": pgettext_lazy("tab", "Products"),
    "properties": pgettext_lazy("tab", "Properties"),
    "seo": pgettext_lazy("tab", "SEO"),
    "upload": pgettext_lazy("tab", "Upload"),
    "view": pgettext_lazy("tab", "View"),
}


@register.filter
def tab_label(key: str) -> str:
    """Return the translated label of the tab ``key``; an unknown key is capitalised and translated if possible."""
    label = TAB_LABELS.get(key)
    return str(label) if label is not None else gettext(key.replace("_", " ").capitalize())


@register.inclusion_tag("manage/category/category_filter.html", takes_context=True)
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
        categories.append(
            {
                "id": category.id,
                "name": category.name,
                "children": children,
                "selected": str(category.id) == selected,
            }
        )

    result = {"categories": categories, "css_class": css_class, "name": name, "selected": selected}
    return result


# NOTE: The reason why not to use another inclusion_tag is that the request is
# not available within an inclusion_tag if one inclusion_tag is called by
# another. (Don't know why yet.)
def category_filter_children(request, category, name="category_filter", level=1):
    """Returns the children of the given category as HTML."""
    categories = []
    for category in category.category_set.all():
        children = category_filter_children(request, category, name, level + 1)
        categories.append(
            {
                "id": category.id,
                "name": "%s%s" % ("&nbsp;" * level * 5, category.name),
                "children": children,
                "level": level,
                "selected": str(category.id) == request.session.get("product_filters", {}).get("category"),
            }
        )

    result = render_to_string(
        "manage/category/category_filter_children.html", request=request, context={"categories": categories}
    )

    return result


@register.inclusion_tag("manage/manufacturers/manufacturer_filter.html", takes_context=True)
def manufacturer_filter(context, css_class="", name="manufacturer"):
    """Returns the categories of the shop for management purposes.

    The css_class attribute is used for different ajax based requests in
    different views.
    """
    request = context.get("request")
    selected = request.session.get("product_filters", {}).get("manufacturer")
    manufacturers = []
    for manufacturer in Manufacturer.objects.all():
        manufacturers.append(
            {
                "id": manufacturer.id,
                "name": manufacturer.name,
                "selected": str(manufacturer.id) == selected,
            }
        )

    result = {"manufacturers": manufacturers, "css_class": css_class, "name": name, "selected": selected}
    return result
