# django imports
from django.contrib import admin

# lfs imports
from lfs.catalog.models import Category
from lfs.catalog.models import FilterStep
from lfs.catalog.models import Image
from lfs.catalog.models import Product
from lfs.catalog.models import ProductAccessories
from lfs.catalog.models import Property
from lfs.catalog.models import PropertyOption
from lfs.catalog.models import PropertyGroup
from lfs.catalog.models import ProductPropertyValue
from lfs.catalog.models import StaticBlock
from lfs.catalog.models import DeliveryTime


class CategoryAdmin(admin.ModelAdmin):
    """
    """
    prepopulated_fields = {"slug": ("name",)}
admin.site.register(Category, CategoryAdmin)


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name", )}
admin.site.register(Product, ProductAdmin)


class ImageAdmin(admin.ModelAdmin):
    """
    """
admin.site.register(Image, ImageAdmin)


class ProductAccessoriesAdmin(admin.ModelAdmin):
    """
    """
admin.site.register(ProductAccessories, ProductAccessoriesAdmin)


class StaticBlockAdmin(admin.ModelAdmin):
    """
    """
admin.site.register(StaticBlock, StaticBlockAdmin)


class DeliveryTimeAdmin(admin.ModelAdmin):
    """
    """
admin.site.register(DeliveryTime, DeliveryTimeAdmin)


admin.site.register(PropertyGroup)
admin.site.register(Property)
admin.site.register(PropertyOption)
admin.site.register(ProductPropertyValue)
admin.site.register(FilterStep)
