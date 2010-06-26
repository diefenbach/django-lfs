# django imports
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.db.models.signals import pre_delete

# lfs imports
from lfs.caching.utils import clear_cache
from lfs.cart.models import Cart
from lfs.catalog.models import Category
from lfs.catalog.models import Product
from lfs.catalog.models import StaticBlock
from lfs.core.models import Shop
from lfs.core.signals import cart_changed
from lfs.core.signals import product_changed
from lfs.core.signals import category_changed
from lfs.core.signals import shop_changed
from lfs.core.signals import topseller_changed
from lfs.marketing.models import Topseller
from lfs.order.models import OrderItem
from lfs.page.models import Page
from lfs.shipping.models import ShippingMethod

# reviews imports
from reviews.signals import review_added

# Shop
def shop_changed_listener(sender, **kwargs):
    clear_cache()
shop_changed.connect(shop_changed_listener)

# Cart
def cart_changed_listener(sender, **kwargs):
    update_cart_cache(sender)
cart_changed.connect(cart_changed_listener)

def cart_deleted_listener(sender, instance, **kwargs):
    update_cart_cache(instance)
pre_delete.connect(cart_deleted_listener, sender=Cart)
    
# Category
def category_deleted_listener(sender, instance, **kwargs):
    update_category_cache(instance)
pre_delete.connect(category_deleted_listener, sender=Category)

def category_saved_listener(sender, instance, **kwargs):
    update_category_cache(instance)
pre_save.connect(category_saved_listener, sender=Category)

def category_changed_listener(sender, **kwargs):
    update_category_cache(sender)
category_changed.connect(category_changed_listener)

# OrderItem
def order_item_listener(sender, instance, **kwargs):
    """Deletes topseller after an OrderItem has been updated. Topseller are 
    calculated automatically on base of OrderItems, hence we have to take of
    that.
    """
    cache.delete("topseller")
    try:
        for category in instance.product.get_categories(with_parents=True):
            cache.delete("topseller-%s" % category.id)
    except: 
        pass # fail silently        
pre_delete.connect(order_item_listener, sender=OrderItem)
post_save.connect(order_item_listener, sender=OrderItem)

# Page
def page_saved_listener(sender, instance, **kwargs):
    cache.delete("page-%s" % instance.slug)
    cache.delete("pages")
post_save.connect(page_saved_listener, sender=Page)

# Product
def product_changed_listener(sender, **kwargs):
    update_product_cache(sender)
product_changed.connect(product_changed_listener)

def product_saved_listener(sender, instance, **kwargs):
    # update_product_cache(instance)
    update_category_cache(instance)
post_save.connect(product_saved_listener, sender=Product)

# Shipping Method
def shipping_method_saved_listener(sender, instance, **kwargs):
    cache.delete("shipping-delivery-time")
    cache.delete("shipping-delivery-time-cart")
post_save.connect(shipping_method_saved_listener, sender=ShippingMethod)

# Shop
def shop_saved_listener(sender, instance, **kwargs):
    cache.delete("shop-%s" % instance.id)
post_save.connect(shop_saved_listener, sender=Shop)

# Static blocks
def static_blocks_saved_listener(sender, instance, **kwargs):
    update_static_block_cache(instance)
post_save.connect(static_blocks_saved_listener, sender=StaticBlock)

# Topseller
def topseller_changed_listener(sender, **kwargs):
    update_topseller_cache(sender)
topseller_changed.connect(topseller_changed_listener)

def topseller_saved_listener(sender, instance, **kwargs):
    update_topseller_cache(instance)
post_save.connect(topseller_saved_listener, sender=Topseller)

def review_added_listener(sender, **kwargs):
    ctype = ContentType.objects.get_for_id(sender.content_type_id)
    product = ctype.get_object_for_this_type(pk=sender.content_id)

    update_product_cache(product)
review_added.connect(review_added_listener)

##### 
def update_category_cache(instance):
    
    # NOTE: ATM, we clear the whole cache if a category has been changed. 
    # Otherwise is lasts to long when the a category has a lot of products 
    # (1000s) and the shop admin changes a category.
    clear_cache()
    return
    cache.delete("category-breadcrumbs-%s" % instance.slug)
    cache.delete("category-products-%s" % instance.slug)
    cache.delete("category-all-products-%s" % instance.slug)
    cache.delete("category-categories-%s" % instance.slug)

    for category in Category.objects.all():
        cache.delete("categories-portlet-%s" % category.slug)

    cache.delete("category-%s" % instance.id) 
    cache.delete("category-%s" % instance.slug)

    cache.delete("category-all-children-%s" % instance.id)
    cache.delete("category-children-%s" % instance.id)
    cache.delete("category-parents-%s" % instance.id)
    cache.delete("category-products-%s" % instance.id)
    cache.delete("category-all-products-%s" % instance.id)
    
    # Note: As this is called "pre-saved" newly created categories don't have
    # the many-to-many attribute "products", hence we have to take care of it 
    # here.
    try:
        for product in instance.products.all():
            update_product_cache(product)
    except ValueError:
        pass
    
def update_product_cache(instance):
    # If the instance is a product with variant or a variant we have to
    # delete also the parent and all other variants
    if instance.is_variant():
        parent = instance.parent
    else:
        parent = instance
    
    cache.delete("product-%s" % parent.id)
    cache.delete("product-%s" % parent.slug)
    cache.delete("product-inline-%s" % parent.id)
    cache.delete("product-images-%s" % parent.id)
    cache.delete("related-products-%s" % parent.id)    
    cache.delete("manage-properties-variants-%s" % parent.id)
    cache.delete("product-categories-%s-False" % parent.id)
    cache.delete("product-categories-%s-True" % parent.id)
    cache.delete("product-navigation-%s" % parent.slug)
    
    try:
        c = cache.get("shipping-delivery-time")
        del c["product-%s" % parent.slug]
        cache.set("shipping-delivery-time", c)
    except (KeyError, TypeError):
        pass
    
    for variant in parent.get_variants():
        cache.delete("product-%s" % variant.id)
        cache.delete("product-%s" % parent.slug)
        cache.delete("product-inline-%s" % variant.id)
        cache.delete("product-images-%s" % variant.id)
        cache.delete("related-products-%s" % variant.id)
        cache.delete("product-categories-%s-False" % variant.id)
        cache.delete("product-categories-%s-True" % variant.id)
        cache.delete("product-navigation-%s" % variant.slug)
        cache.delete("product-shipping-%s" % variant.slug)

def update_cart_cache(instance):
    """Deletes all cart relevant caches.
    """
    cache.delete("cart-%s" % instance.user)
    cache.delete("cart-%s" % instance.session)
    cache.delete("cart-items-%s" % instance.id)
    cache.delete("cart-costs-True-%s" % instance.id)
    cache.delete("cart-costs-False-%s" % instance.id)
    cache.delete("shipping-delivery-time-cart")
    cache.delete("shipping-delivery-time")
        
def update_static_block_cache(instance):
    """Deletes all static block relevant caches.
    """
    cache.delete("static-block-%s" % instance.id)
    
    for category in instance.categories.all():
        cache.delete("category-inline-%s" % category.slug)

def update_topseller_cache(topseller):
    """Deletes all topseller relevant caches.
    """
    cache.delete("topseller")
    product = topseller.product
    for category in product.get_categories(with_parents=True):
        cache.delete("topseller-%s" % category.id)