# django imports
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.caching.utils import lfs_get_object_or_404
from lfs.catalog.models import Product
from lfs.catalog.models import ProductPropertyValue
from lfs.catalog.models import PropertyGroup
from lfs.core.utils import LazyEncoder

@permission_required("core.manage_shop", login_url="/login/")
def product_values(request, property_group_id, template_name="manage/properties/pg_product_values.html"):
    """Renders the products values part of the property groups management views.
    """
    property_group = lfs_get_object_or_404(PropertyGroup, pk=property_group_id)
    all_properties = property_group.properties.order_by("groupspropertiesrelation")
    products = []
    for product in property_group.products.all():
        properties = []
        for property in all_properties:
            # Try to get the value, if it already exists.
            try:
                ppv = ProductPropertyValue.objects.get(property = property, product=product, type=1)
            except ProductPropertyValue.DoesNotExist:
                value = ""
            else:
                value = ppv.value

            # mark selected options "selected"
            options = []
            for option in property.options.all():
                options.append({
                    "id"       : option.id,
                    "name"     : option.name,
                    "selected" : str(option.id) == value
                })

            properties.append({
                "id"      : property.id,
                "name"    : property.name,
                "type"    : property.type,
                "is_select_field" : property.is_select_field,
                "options" : options,
                "value"   : value,
            })

        products.append({
            "id" : product.id,
            "name" : product.get_name(),
            "properties" : properties,
        })

    return render_to_string(template_name, RequestContext(request, {
        "property_group" : property_group,
        "products" : products,
        "all_properties" : all_properties,
    }))

@permission_required("core.manage_shop", login_url="/login/")
def update_product_values(request, property_group_id):
    """Updates product property values.
    """
    property_group = lfs_get_object_or_404(PropertyGroup, pk=property_group_id)
    product_ids = request.POST.getlist("product-id")
    products = Product.objects.filter(pk__in=product_ids)

    for product in products:
        for property in property_group.properties.all():
            value = request.POST.get("property-%s-%s" % (product.id, property.id), "")
            if value != "":
                try:
                    ppv = ProductPropertyValue.objects.get(property = property, product=product)
                except ProductPropertyValue.DoesNotExist:
                    ProductPropertyValue.objects.create(property = property, product=product, value=value)
                else:
                    ppv.value = value
                    ppv.save()

    result = simplejson.dumps({
        "html" : product_values(request, property_group_id),
        "message" : _(u"Product Values have been saved.")
    }, cls=LazyEncoder);

    return HttpResponse(result)
