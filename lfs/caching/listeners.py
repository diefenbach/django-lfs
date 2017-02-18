from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db.models.signals import post_save, m2m_changed, post_delete
from django.db.models.signals import pre_save
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from lfs.caching.utils import clear_cache, delete_cache, invalidate_cache_group_id
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
from lfs.core.signals import manufacturer_changed
from lfs.criteria.models import CountryCriterion, WeightCriterion, WidthCriterion, ShippingMethodCriterion, \
    PaymentMethodCriterion, LengthCriterion, HeightCriterion, CombinedLengthAndGirthCriterion, CartPriceCriterion
from lfs.customer_tax.models import CustomerTax
from lfs.marketing.models import Topseller
from lfs.order.models import OrderItem
from lfs.page.models import Page
from lfs.shipping.models import ShippingMethod
from lfs.tax.models import Tax

from reviews.signals import review_added


# Shop
@receiver(shop_changed)
def shop_changed_listener(sender, **kwargs):
    clear_cache()


# Cart
@receiver(cart_changed)
def cart_changed_listener(sender, **kwargs):
    update_cart_cache(sender)


@receiver(pre_delete, sender=Cart)
def cart_deleted_listener(sender, instance, **kwargs):
    update_cart_cache(instance)


# Category
@receiver(pre_delete, sender=Category)
def category_deleted_listener(sender, instance, **kwargs):
    update_category_cache(instance)


@receiver(pre_save, sender=Category)
def category_saved_listener(sender, instance, **kwargs):
    update_category_cache(instance)


@receiver(category_changed)
def category_changed_listener(sender, **kwargs):
    update_category_cache(sender)


@receiver(m2m_changed, sender=Category.products.through)
def product_categories_changed_listener(sender, **kwargs):
    instance = kwargs['instance']
    reverse = kwargs['reverse']
    pk_set = kwargs['pk_set']

    if reverse:
        product = instance
        delete_cache("%s-product-categories-%s-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, product.id, True))
        delete_cache("%s-product-categories-%s-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, product.id, False))
    else:
        if pk_set:
            for product in Product.objects.filter(pk__in=pk_set):
                delete_cache("%s-product-categories-%s-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, product.id, True))
                delete_cache("%s-product-categories-%s-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, product.id, False))


# Manufacturer
@receiver(manufacturer_changed)
def manufacturer_changed_listener(sender, **kwargs):
    # filtered lists of products assigned to manufacturer used at manufacturer page
    delete_cache("%s-manufacturer-products-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, sender.slug))
    # list of all manufacturer products
    delete_cache("%s-manufacturer-all-products-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, sender.pk))
    # if manufacturer assignment was changed then product navigation might be different too
    invalidate_cache_group_id('product_navigation')


# OrderItem
@receiver(pre_delete, sender=OrderItem)
@receiver(post_save, sender=OrderItem)
def order_item_listener(sender, instance, **kwargs):
    """Deletes topseller after an OrderItem has been updated. Topseller are
    calculated automatically on base of OrderItems, hence we have to take of
    that.
    """
    delete_cache("%s-topseller" % settings.CACHE_MIDDLEWARE_KEY_PREFIX)
    try:
        for category in instance.product.get_categories(with_parents=True):
            delete_cache("%s-topseller-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, category.id))
    except:
        pass  # fail silently


# Page
@receiver(post_save, sender=Page)
def page_saved_listener(sender, instance, **kwargs):
    delete_cache("%s-page-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.slug))
    delete_cache("%s-pages" % settings.CACHE_MIDDLEWARE_KEY_PREFIX)


# Product
@receiver(product_changed)
def product_changed_listener(sender, **kwargs):
    update_product_cache(sender)


@receiver(post_save, sender=Product)
def product_saved_listener(sender, instance, **kwargs):
    # update_product_cache(instance)
    update_category_cache(instance)


@receiver(post_save, sender=Product)
def product_pre_saved_listener(sender, instance, **kwargs):
    """ If product slug was changed we should have cleared slug based product cache"""
    # check if product already exists in database
    if instance.pk:
        if instance.is_variant():
            parent = instance.parent
        else:
            parent = instance

        delete_cache("%s-product-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, parent.id))

        try:
            old_product = Product.objects.get(pk=parent.pk)
        except Product.DoesNotExist:
            pass
        else:
            delete_cache("%s-product-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, old_product.slug))


# Shipping Method
@receiver(post_save, sender=ShippingMethod)
def shipping_method_saved_listener(sender, instance, **kwargs):
    delete_cache("%s-shipping-delivery-time" % settings.CACHE_MIDDLEWARE_KEY_PREFIX)
    delete_cache("%s-shipping-delivery-time-cart" % settings.CACHE_MIDDLEWARE_KEY_PREFIX)
    delete_cache("all_active_shipping_methods")


@receiver(post_delete, sender=ShippingMethod)
def shipping_method_deleted_listener(sender, instance, **kwargs):
    delete_cache("all_active_shipping_methods")


# Shop
@receiver(post_save, sender=Shop)
def shop_saved_listener(sender, instance, **kwargs):
    delete_cache("%s-shop-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.id))


# Static blocks
@receiver(post_save, sender=StaticBlock)
def static_blocks_saved_listener(sender, instance, **kwargs):
    update_static_block_cache(instance)


# Topseller
@receiver(topseller_changed)
def topseller_changed_listener(sender, **kwargs):
    update_topseller_cache(sender)


@receiver(post_save, sender=Topseller)
def topseller_saved_listener(sender, instance, **kwargs):
    update_topseller_cache(instance)


@receiver(review_added)
def review_added_listener(sender, **kwargs):
    ctype = ContentType.objects.get_for_id(sender.content_type_id)
    product = ctype.get_object_for_this_type(pk=sender.content_id)
    update_product_cache(product)


@receiver(m2m_changed, sender=CountryCriterion.value.through)
def criterion_countries_changed(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action in ('post_add', 'post_remove', 'post_clear'):
        if not reverse:
            delete_cache(u'country_values_{}'.format(instance.pk))
        else:
            for pk in pk_set:
                delete_cache(u'country_values_{}'.format(pk))


@receiver(post_save, sender=CustomerTax)
def customer_tax_created_listener(sender, instance, created, **kwargs):
    if created:
        delete_cache(u'all_customer_taxes')


@receiver(post_delete, sender=CustomerTax)
def customer_tax_deleted_listener(sender, instance, **kwargs):
    delete_cache(u'all_customer_taxes')


@receiver(post_save, sender=Tax)
def tax_rate_created_listener(sender, instance, created, **kwargs):
    delete_cache(u'tax_rate_{}'.format(instance.pk))


@receiver(post_delete, sender=Tax)
def tax_rate_deleted_listener(sender, instance, **kwargs):
    delete_cache(u'tax_rate_{}'.format(instance.pk))


#####
def update_category_cache(instance):

    # NOTE: ATM, we clear the whole cache if a category has been changed.
    # Otherwise is lasts to long when the a category has a lot of products
    # (1000s) and the shop admin changes a category.
    clear_cache()
    return
    delete_cache("%s-category-breadcrumbs-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.slug))
    delete_cache("%s-category-products-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.slug))
    delete_cache("%s-category-all-products-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.slug))
    delete_cache("%s-category-categories-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.slug))

    for category in Category.objects.all():
        delete_cache("%s-categories-portlet-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, category.slug))

    delete_cache("%s-category-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.id))
    delete_cache("%s-category-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.slug))

    delete_cache("%s-category-all-children-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.id))
    delete_cache("%s-category-children-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.id))
    delete_cache("%s-category-parents-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.id))
    delete_cache("%s-category-products-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.id))
    delete_cache("%s-category-all-products-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.id))

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

    # if product was changed then we have to clear all product_navigation caches
    invalidate_cache_group_id('product_navigation')
    invalidate_cache_group_id('properties-%s' % parent.id)
    delete_cache("%s-product-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, parent.id))
    delete_cache("%s-product-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, parent.slug))
    delete_cache("%s-product-images-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, parent.id))
    delete_cache("%s-related-products-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, parent.id))
    delete_cache("%s-product-categories-%s-False" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, parent.id))
    delete_cache("%s-product-categories-%s-True" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, parent.id))
    delete_cache("%s-default-variant-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, parent.id))
    if parent.manufacturer:
        delete_cache("%s-manufacturer-all-products-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, parent.manufacturer.pk))
        delete_cache("%s-manufacturer-products-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, parent.manufacturer.slug))

    try:
        c = cache.get("%s-shipping-delivery-time" % settings.CACHE_MIDDLEWARE_KEY_PREFIX)
        del c["%s-product-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, parent.slug)]
        cache.set("%s-shipping-delivery-time" % settings.CACHE_MIDDLEWARE_KEY_PREFIX, c)
    except (KeyError, TypeError):
        pass

    for variant in parent.get_variants():
        delete_cache("%s-product-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, variant.id))
        delete_cache("%s-product-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, parent.slug))
        delete_cache("%s-product-images-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, variant.id))
        delete_cache("%s-related-products-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, variant.id))
        delete_cache("%s-product-categories-%s-False" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, variant.id))
        delete_cache("%s-product-categories-%s-True" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, variant.id))
        delete_cache("%s-product-shipping-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, variant.slug))


def update_cart_cache(instance):
    """Deletes all cart relevant caches.
    """
    if instance.user:
        delete_cache("%s-cart-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.user.pk))

    delete_cache("%s-cart-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.session))
    delete_cache("%s-cart-items-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.id))
    delete_cache("%s-cart-costs-True-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.id))
    delete_cache("%s-cart-costs-False-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.id))
    delete_cache("%s-shipping-delivery-time-cart" % settings.CACHE_MIDDLEWARE_KEY_PREFIX)
    delete_cache("%s-shipping-delivery-time" % settings.CACHE_MIDDLEWARE_KEY_PREFIX)


def update_static_block_cache(instance):
    """Deletes all static block relevant caches.
    """
    delete_cache("%s-static-block-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, instance.id))

    for category in instance.categories.all():
        delete_cache("%s-category-inline-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, category.slug))


def update_topseller_cache(topseller):
    """Deletes all topseller relevant caches.
    """
    delete_cache("%s-topseller" % settings.CACHE_MIDDLEWARE_KEY_PREFIX)
    product = topseller.product
    for category in product.get_categories(with_parents=True):
        delete_cache("%s-topseller-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, category.id))


@receiver(post_save, sender=WeightCriterion)
@receiver(post_save, sender=CartPriceCriterion)
@receiver(post_save, sender=CombinedLengthAndGirthCriterion)
@receiver(post_save, sender=CountryCriterion)
@receiver(post_save, sender=HeightCriterion)
@receiver(post_save, sender=LengthCriterion)
@receiver(post_save, sender=PaymentMethodCriterion)
@receiver(post_save, sender=ShippingMethodCriterion)
@receiver(post_save, sender=WidthCriterion)
@receiver(pre_delete, sender=WeightCriterion)
@receiver(pre_delete, sender=CartPriceCriterion)
@receiver(pre_delete, sender=CombinedLengthAndGirthCriterion)
@receiver(pre_delete, sender=CountryCriterion)
@receiver(pre_delete, sender=HeightCriterion)
@receiver(pre_delete, sender=LengthCriterion)
@receiver(pre_delete, sender=PaymentMethodCriterion)
@receiver(pre_delete, sender=ShippingMethodCriterion)
@receiver(pre_delete, sender=WidthCriterion)
def clear_criterion_cache(sender, instance, created, **kwargs):
    cache_key = u'criteria_for_model_{}_{}'.format(instance.content_id, instance.content_type.pk)
    cache.delete(cache_key)
