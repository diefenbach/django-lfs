# django imports
from django.db.models.signals import pre_delete

# lfs imports
from lfs.catalog.models import PropertyGroup
from lfs.catalog.models import ProductPropertyValue
from lfs.catalog.models import PropertyOption
from lfs.catalog.models import GroupsPropertiesRelation
from lfs.core.signals import property_type_changed
from lfs.core.signals import product_removed_property_group

def property_option_deleted_listener(sender, instance, **kwargs):
    """Deletes all property values which have the deleted PropertyOption 
    (instance) selected.
    
    NOTE: This has to be done via a event/listener pair, because the id of
    the option is stored within value field (a char field) of the Product-
    PropertyValue [1]. That means that there is no relation at ORM level, 
    hence the automatic integrity check doesn't take place at all.
    
    [1] This is done because the value field can also contain free text, for
    instance if the type of the property is a PROPERTY_TEXT_FIELD. 
    """
    property = instance.property
    for ppv in ProductPropertyValue.objects.filter(
        property=property, value=str(instance.id)):
        ppv.delete()
pre_delete.connect(property_option_deleted_listener, sender=PropertyOption)

def property_group_deleted_listener(sender, instance, **kwargs):
    """Deletes all ProductPropertyValue, which fullfill following criteria:
       1. Property belongs to the deleted PropertyGroup
       2. Product has the deleted PropertyGroup selected
    """
    properties = instance.properties.all()
    products = instance.products.all()
    
    for product in products:
        for property in properties:
            try:
                ppv = ProductPropertyValue.objects.get(product=product, property=property)
            except ProductPropertyValue.DoesNotExist:
                pass
            else:
                ppv.delete()
pre_delete.connect(property_group_deleted_listener, sender=PropertyGroup)

def property_removed_listener(sender, instance, **kwargs):
    """This is called when a GroupsPropertiesRelation is about to be deleted. 
    This stands for removing a Property from a PropertyGroup.
    
    This deletes all ProductPropertyValue of products which are in the group of 
    question and with the removed property.
    """
    property = instance.property
    products = instance.group.products.all()

    for product in products:
        try:
            ppv = ProductPropertyValue.objects.get(product=product, property=property)
        except ProductPropertyValue.DoesNotExist:
            pass
        else:
            ppv.delete()    
pre_delete.connect(property_removed_listener, sender=GroupsPropertiesRelation)

def property_type_changed_listener(sender, **kwargs):
    """This is called when the type of a Property has been changed. Then all 
    ProductPropertyValue with this property have to be deleted.
    """
    ppvs = ProductPropertyValue.objects.filter(property=sender)
    ppvs.delete()
property_type_changed.connect(property_type_changed_listener)

def product_removed_from_property_group_listener(sender, **kwargs):
    """
    """
    property_group, product = sender
    
    # Remove property values for product and properties of the group.
    for property in property_group.properties.all():
        try:
            ppv = ProductPropertyValue.objects.get(product=product, property=property)
        except ProductPropertyValue.DoesNotExist:
            pass
        else:
            ppv.delete()
product_removed_property_group.connect(product_removed_from_property_group_listener)
