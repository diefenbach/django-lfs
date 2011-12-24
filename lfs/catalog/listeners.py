# django imports
from django.db.models.signals import pre_delete, m2m_changed
from django.conf import settings
from django.core.cache import cache

# lfs imports
from lfs.catalog.models import PropertyGroup
from lfs.catalog.models import ProductPropertyValue
from lfs.catalog.models import PropertyOption
from lfs.catalog.models import GroupsPropertiesRelation
from lfs.catalog.models import Category
from lfs.core.signals import property_type_changed
from lfs.core.signals import product_removed_property_group


def property_option_deleted_listener(sender, instance, **kwargs):
    """
    This is called before a PropertyOption is deleted.

    Deletes all property values that have the PropertyOption (passed by
    instance) selected which is about to be deleted.
    """
    property = instance.property
    ProductPropertyValue.objects.filter(property=property, value=str(instance.id)).delete()
pre_delete.connect(property_option_deleted_listener, sender=PropertyOption)


def property_group_deleted_listener(sender, instance, **kwargs):
    """
    This is called before a PropertyGroup is deleted.

    Deletes all ProductPropertyValue which are assigned to products and
    properties of the PropertyGroup which is about to be deleted.
    """
    properties = instance.properties.all()
    products = instance.products.all()

    for product in products:
        for property in properties:
            ProductPropertyValue.objects.filter(product=product, property=property).delete()
pre_delete.connect(property_group_deleted_listener, sender=PropertyGroup)


def property_removed_from_property_group_listener(sender, instance, **kwargs):
    """
    This is called before a GroupsPropertiesRelation is deleted, in other
    words when a Property is removed from a PropertyGroup.

    Deletes all ProductPropertyValue which are assigned to the property and
    the property group from which the property is about to be removed.
    """
    property = instance.property
    products = instance.group.products.all()

    for product in products:
        ProductPropertyValue.objects.filter(product=product, property=property).delete()
pre_delete.connect(property_removed_from_property_group_listener, sender=GroupsPropertiesRelation)


def product_removed_from_property_group_listener(sender, **kwargs):
    """
    This is called when a product is removed from a property group.

    Deletes all ProductPropertyValue for this product and the properties which
    are belong to this property group.
    """
    property_group, product = sender

    for property in property_group.properties.all():
        ProductPropertyValue.objects.filter(product=product, property=property).delete()
product_removed_property_group.connect(product_removed_from_property_group_listener)


def property_type_changed_listener(sender, **kwargs):
    """
    This is called after the type of a property has been changed.

    Deletes all ProductPropertyValue which are assigned to the property.
    """
    ProductPropertyValue.objects.filter(property=sender).delete()
property_type_changed.connect(property_type_changed_listener)
