# django imports
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string

# lfs imports
from lfs.catalog.models import Product
from lfs.catalog.models import ProductPropertyValue
from lfs.catalog.models import Property
from lfs.catalog.models import PropertyGroup
from lfs.core.signals import product_removed_property_group

@permission_required("manage_shop", login_url="/login/")
def manage_properties(request, product_id, template_name="manage/product/properties.html"):
    """
    """
    product = get_object_or_404(Product, pk=product_id)
    
    # Generate list of product property groups; used for enter value
    product_property_groups = []
    for property_group in product.property_groups.all():
        properties = []
        for property in property_group.properties.order_by("groupspropertiesrelation"):
            # Try to get the value, if it already exists.
            try:
                ppv = ProductPropertyValue.objects.get(property = property, product=product)
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
                "options" : options,
                "value"   : value,
            })

        product_property_groups.append({
            "id"   : property_group.id,
            "name" : property_group.name,
            "properties" : properties,
        })
    
    # Generate list of all property groups; used for group selection
    product_property_group_ids = [p["id"] for p in product_property_groups]
    shop_property_groups = []
    for property_group in PropertyGroup.objects.all():
        
        shop_property_groups.append({
            "id" : property_group.id,
            "name" : property_group.name,
            "selected" : property_group.id in product_property_group_ids,
        })
    
    return render_to_string(template_name, RequestContext(request, {
        "product" : product,
        "product_property_groups" : product_property_groups,
        "shop_property_groups" : shop_property_groups,
    }))

@permission_required("manage_shop", login_url="/login/")
def update_property_groups(request, product_id):
    """Updates property groups for the product with passed id.
    """
    selected_group_ids = request.POST.getlist("selected-property-groups")
    
    for property_group in PropertyGroup.objects.all():
        # if the group is within selected groups we try to add it to the product
        # otherwise we try do delete it
        if str(property_group.id) in selected_group_ids:
            try:
                property_group.products.get(pk=product_id)
            except ObjectDoesNotExist:
                property_group.products.add(product_id)
        else:
            property_group.products.remove(product_id)
            product = Product.objects.get(pk=product_id)
            product_removed_property_group.send([property_group, product])
    
    url = reverse("lfs_manage_product", kwargs={"product_id" : product_id})        
    return HttpResponseRedirect(url)

@permission_required("manage_shop", login_url="/login/")    
def update_properties(request, product_id):
    """Updates properties for product with passed id.
    """
    # Update properties' values
    for key, value in request.POST.items():
        if key.startswith("property") == False:
            continue        

        property_id = key.split("-")[1]
        property = get_object_or_404(Property, pk=property_id)
        product = get_object_or_404(Product, pk=product_id)
        
        try:
            ppv = ProductPropertyValue.objects.get(product = product_id, property = property_id)
        except ProductPropertyValue.DoesNotExist:
            if not property.is_valid_value(value):
                value = 0
            ProductPropertyValue.objects.create(product=product, property = property, value=value)
        else:            
            if not property.is_valid_value(value):
                value = 0
            
            ppv.value = value
            ppv.save()

    url = reverse("lfs_manage_product", kwargs={"product_id" : product_id})    
    return HttpResponseRedirect(url)
