import os

from django.db.models.signals import post_delete, post_save
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from lfs.catalog.models import File, Property
from lfs.catalog.models import Image
from lfs.catalog.models import ProductAttachment
from lfs.catalog.models import PropertyGroup
from lfs.catalog.models import ProductPropertyValue
from lfs.catalog.models import PropertyOption
from lfs.catalog.models import GroupsPropertiesRelation
from lfs.catalog.settings import DELETE_FILES, PROPERTY_VALUE_TYPE_FILTER
from lfs.catalog.settings import DELETE_IMAGES
from lfs.catalog.settings import THUMBNAIL_SIZES
from lfs.core.signals import property_type_changed
from lfs.core.signals import product_removed_property_group


@receiver(pre_delete, sender=PropertyOption)
def property_option_deleted_listener(sender, instance, **kwargs):
    """
    This is called before a PropertyOption is deleted.

    Deletes all property values that have the PropertyOption (passed by
    instance) selected which is about to be deleted.
    """
    prop = instance.property
    ProductPropertyValue.objects.filter(property=prop, value=str(instance.id)).delete()


@receiver(pre_delete, sender=PropertyGroup)
def property_group_deleted_listener(sender, instance, **kwargs):
    """
    This is called before a PropertyGroup is deleted.

    Deletes all ProductPropertyValue which are assigned to products and
    properties of the PropertyGroup which is about to be deleted.
    """
    ProductPropertyValue.objects.filter(property_group=instance).delete()


@receiver(pre_delete, sender=GroupsPropertiesRelation)
def property_removed_from_property_group_listener(sender, instance, **kwargs):
    """
    This is called before a GroupsPropertiesRelation is deleted, in other
    words when a Property is removed from a PropertyGroup.

    Deletes all ProductPropertyValue which are assigned to the property and
    the property group from which the property is about to be removed.
    """
    ProductPropertyValue.objects.filter(property_group=instance.group, property=instance.property).delete()


@receiver(product_removed_property_group)
def product_removed_from_property_group_listener(sender, **kwargs):
    """
    This is called when a product is removed from a property group.

    Deletes all ProductPropertyValue for this product and the properties which
    belong to this property group.
    """
    property_group = sender
    product = kwargs.get("product")

    ProductPropertyValue.objects.filter(product=product, property_group=property_group).delete()


@receiver(post_save, sender=Property)
def property_changed_to_not_filterable_listener(sender, instance, created, **kwargs):
    """
    This is called when a property that was filterable is set to not filterable

    Deletes all ProductPropertyValue for this property
    """
    if not instance.filterable:
        ProductPropertyValue.objects.filter(property=instance, type=PROPERTY_VALUE_TYPE_FILTER).delete()


@receiver(property_type_changed)
def property_type_changed_listener(sender, **kwargs):
    """
    This is called after the type of a property has been changed.

    Deletes all ProductPropertyValue which are assigned to the property.
    """
    ProductPropertyValue.objects.filter(property=sender).delete()


@receiver(post_delete, sender=Image)
def delete_image_files(sender, **kwargs):
    """
    Deletes Image files on file system after an Image object has been deleted.
    """
    if DELETE_IMAGES:
        image = kwargs.get("instance")
        try:
            path = image.image._get_path()
        except ValueError:
            pass
        else:
            try:
                os.remove(path)
            except OSError:
                pass
            base, ext = os.path.splitext(path)
            for width, height in THUMBNAIL_SIZES:
                try:
                    os.remove("%s.%sx%s%s" % (base, width, height, ext))
                except OSError:
                    continue


@receiver(post_delete, sender=ProductAttachment)
@receiver(post_delete, sender=File)
def delete_file_files(sender, **kwargs):
    """
    Deletes File files on file system after an File object has been deleted.
    """
    if DELETE_FILES:
        file = kwargs.get("instance")
        try:
            path = file.file._get_path()
        except ValueError:
            pass
        else:
            try:
                os.remove(path)
            except OSError:
                pass
