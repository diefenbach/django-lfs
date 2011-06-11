# django imports
from django.conf import settings
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
    cache.delete("%s-topseller" % settings.CACHE_MIDDLEWARE_KEY_PREFIX)
    try:
        for category in instance.product.get_categories(with_parents=True):
            cache.delete("%s-topseller-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, category.id))
    except:
        pass  # fail silently
pre_delete.connect(order_item_listener, sender=OrderItem)
post_save.connect(order_item_listener, sender=OrderItem)


# Page
def page_saved_listener(sender, instance, **kwargs):
    cache.delete("%s-page-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.slug))
    cache.delete("%s-pages" % settings.CACHE_MIDDLEWARE_KEY_PREFIX)
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
    cache.delete("%s-shipping-delivery-time" % settings.CACHE_MIDDLEWARE_KEY_PREFIX)
    cache.delete("%s-shipping-delivery-time-cart" % settings.CACHE_MIDDLEWARE_KEY_PREFIX)
post_save.connect(shipping_method_saved_listener, sender=ShippingMethod)


# Shop
def shop_saved_listener(sender, instance, **kwargs):
    cache.delete("%s-shop-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.id))
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
    cache.delete("%s-category-breadcrumbs-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.slug))
    cache.delete("%s-category-products-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.slug))
    cache.delete("%s-category-all-products-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.slug))
    cache.delete("%s-category-categories-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.slug))

    for category in Category.objects.all():
        cache.delete("%s-categories-portlet-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, category.slug))

    cache.delete("%s-category-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.id))
    cache.delete("%s-category-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.slug))

    cache.delete("%s-category-all-children-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.id))
    cache.delete("%s-category-children-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.id))
    cache.delete("%s-category-parents-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.id))
    cache.delete("%s-category-products-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.id))
    cache.delete("%s-category-all-products-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.id))

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

    cache.delete("%s-product-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, parent.id))
    cache.delete("%s-product-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, parent.slug))
    cache.delete("%s-product-inline-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, parent.id))
    cache.delete("%s-product-images-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, parent.id))
    cache.delete("%s-related-products-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, parent.id))
    cache.delete("%s-manage-properties-variants-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, parent.id))
    cache.delete("%s-product-categories-%s-False" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, parent.id))
    cache.delete("%s-product-categories-%s-True" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, parent.id))
    cache.delete("%s-product-navigation-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, parent.slug))

    try:
        c = cache.get("%s-shipping-delivery-time" % settings.CACHE_MIDDLEWARE_KEY_PREFIX)
        del c["%s-product-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, parent.slug)]
        cache.set("%s-shipping-delivery-time" % settings.CACHE_MIDDLEWARE_KEY_PREFIX, c)
    except (KeyError, TypeError):
        pass

    for variant in parent.get_variants():
        cache.delete("%s-product-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, variant.id))
        cache.delete("%s-product-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, parent.slug))
        cache.delete("%s-product-inline-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, variant.id))
        cache.delete("%s-product-images-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, variant.id))
        cache.delete("%s-related-products-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, variant.id))
        cache.delete("%s-product-categories-%s-False" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, variant.id))
        cache.delete("%s-product-categories-%s-True" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, variant.id))
        cache.delete("%s-product-navigation-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, variant.slug))
        cache.delete("%s-product-shipping-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, variant.slug))


def update_cart_cache(instance):
    """Deletes all cart relevant caches.
    """
    cache.delete("%s-cart-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.user))
    cache.delete("%s-cart-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.session))
    cache.delete("%s-cart-items-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.id))
    cache.delete("%s-cart-costs-True-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.id))
    cache.delete("%s-cart-costs-False-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.id))
    cache.delete("%s-shipping-delivery-time-cart" % settings.CACHE_MIDDLEWARE_KEY_PREFIX)
    cache.delete("%s-shipping-delivery-time" % settings.CACHE_MIDDLEWARE_KEY_PREFIX)


def update_static_block_cache(instance):
    """Deletes all static block relevant caches.
    """
    cache.delete("%s-static-block-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.id))

    for category in instance.categories.all():
        cache.delete("%s-category-inline-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, category.slug))


def update_topseller_cache(topseller):
    """Deletes all topseller relevant caches.
    """
    cache.delete("%s-topseller" % settings.CACHE_MIDDLEWARE_KEY_PREFIX)
    product = topseller.product
    for category in product.get_categories(with_parents=True):
        cache.delete("%s-topseller-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, category.id))
