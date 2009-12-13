# django imports
from django import template
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.template import Library, Node, TemplateSyntaxError
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

# lfs imports
import lfs.catalog.utils
import lfs.utils.misc
from lfs.caching.utils import lfs_get_object_or_404
from lfs.cart import utils as cart_utils
from lfs.catalog.models import Category
from lfs.catalog.settings import PRODUCT_WITH_VARIANTS
from lfs.catalog.settings import STANDARD_PRODUCT
from lfs.page.models import Page
from lfs.catalog.models import Product
from lfs.catalog.models import PropertyOption
from lfs.catalog.settings import PRODUCT_TYPE_LOOKUP
from lfs.core.models import Shop
from lfs.core.models import Action
from lfs.core.settings import ACTION_PLACE_TABS
from lfs.shipping import utils as shipping_utils

register = template.Library()

@register.inclusion_tag('lfs/portlets/category_children.html', takes_context=True)
def category_children(context, categories):
    """
    """
    return {
        "categories" : categories,
    }

@register.inclusion_tag('lfs/shop/google_analytics_tracking.html', takes_context=True)
def google_analytics_tracking(context):
    """Returns google analytics tracking code which has been entered to the
    shop.
    """
    shop = lfs_get_object_or_404(Shop, pk=1)
    return {
        "ga_site_tracking" : shop.ga_site_tracking,
        "google_analytics_id" : shop.google_analytics_id,
    }

@register.inclusion_tag('lfs/shop/google_analytics_ecommerce.html', takes_context=True)
def google_analytics_ecommerce(context, clear_session=True):
    """Returns google analytics e-commerce tracking code. This should be
    displayed on the thank-you page.
    """
    request = context.get("request")
    order = request.session.get("order")
    shop = lfs_get_object_or_404(Shop, pk=1)

    # The order is removed from the session. It has been added after the order
    # has been payed within the checkout process. See order.utils for more.
    if clear_session and request.session.has_key("order"):
        del request.session["order"]

    if request.session.has_key("voucher"):
        del request.session["voucher"]

    return {
        "order" : order,
        "ga_ecommerce_tracking" : shop.ga_ecommerce_tracking,
        "google_analytics_id" : shop.google_analytics_id,
    }

def _get_shipping(context, product):
    request = context.get("request")
    if product.deliverable == False:
        return {
            "deliverable" : False,
            "delivery_time" : shipping_utils.get_product_delivery_time(request, product.slug)
        }
    else:
        return {
            "deliverable" : True,
            "delivery_time" : shipping_utils.get_product_delivery_time(request, product.slug)
        }

@register.inclusion_tag('lfs/shipping/shipping_tag.html', takes_context=True)
def shipping(context, variant):
    return _get_shipping(context, variant)

@register.inclusion_tag('lfs/catalog/sorting.html', takes_context=True)
def sorting(context):
    """
    """
    request = context.get("request")
    return {"current" : request.session.get("sorting")}

@register.inclusion_tag('lfs/catalog/breadcrumbs.html', takes_context=True)
def breadcrumbs(context, obj):
    """
    """
    if isinstance(obj, Category):
        cache_key = "category-breadcrumbs-%s" % obj.slug
        objects = cache.get(cache_key)
        if objects is not None:
            return objects

        objects = []
        while obj is not None:
            objects.insert(0, {
                "name" : obj.name,
                "url"  : obj.get_absolute_url(),
            })
            obj = obj.parent

        result = {
            "objects" : objects,
            "MEDIA_URL" : context.get("MEDIA_URL"),
        }
        cache.set(cache_key, result)

    elif isinstance(obj, Product):
        try:
            if obj.is_variant():
                parent_product = obj.parent
            else:
                parent_product = obj
        except ObjectDoesNotExist:
            return []
        else:
            request = context.get("request")
            category = lfs.catalog.utils.get_current_product_category(request, obj)
            if category is None:
                return []
            else:
                objects = [{
                    "name" : obj.get_name(),
                    "url"  : obj.get_absolute_url(),
                }]
                while category is not None:
                    objects.insert(0, {
                        "name" : category.name,
                        "url" : category.get_absolute_url(),
                    })
                    category = category.parent

        result = {
            "objects" : objects,
            "MEDIA_URL" : context.get("MEDIA_URL"),
        }

    elif isinstance(obj, Page):
        objects = []
        objects.append({
            "name": _(u"Information"),
            "get_absolute_url" : reverse("lfs_pages")})
        objects.append({"name": obj.title})

        result = {
            "objects" : objects,
            "MEDIA_URL" : context.get("MEDIA_URL"),
        }
    else:
        result = {
            "objects" : ({ "name" : obj }, ),
            "MEDIA_URL" : context.get("MEDIA_URL"),
        }

    return result

@register.inclusion_tag('lfs/catalog/filter_navigation.html', takes_context=True)
def filter_navigation(context, category):
    """Displays the filter navigation portlet.
    """
    request = context.get("request")
    sorting = request.session.get("sorting")

    # Get saved filters
    set_product_filters = request.session.get("product-filter", {})
    set_product_filters = set_product_filters.items()
    set_price_filters = request.session.get("price-filter")

    # calculate filters
    product_filters = lfs.catalog.utils.get_product_filters(category,
        set_product_filters, set_price_filters, sorting)

    price_filters = lfs.catalog.utils.get_price_filters(category,
        set_product_filters, set_price_filters)

    return {
        "category" : category,
        "product_filters" : product_filters,
        "set_price_filters" : set_price_filters,
        "price_filters" : price_filters,
    }

@register.inclusion_tag('lfs/catalog/product_navigation.html', takes_context=True)
def product_navigation(context, product):
    """Provides previous and next product links.
    """
    request = context.get("request")
    sorting = request.session.get("sorting", "price")

    slug = product.slug

    cache_key = "product-navigation-%s" % slug
    temp = None # cache.get(cache_key)
    if temp is not None:
        try:
            return temp[sorting]
        except KeyError:
            pass
    else:
        temp = dict()

    # To calculate the position we take only STANDARD_PRODUCT into account.
    # That means if the current product is a VARIANT we switch to its parent
    # product.
    if product.is_variant():
        product = product.parent
        slug = product.slug

    category = lfs.catalog.utils.get_current_product_category(request, product)
    if category is None:
        return {"display" : False }
    else:
        # First we collect all sub categories. This and using the in operator makes
        # batching more easier
        categories = [category]

        if category.show_all_products:
            categories.extend(category.get_all_children())

        # This is necessary as we display non active products to superusers.
        # So we have to take care for the product navigation too.
        if request.user.is_superuser:
            products = Product.objects.filter(
                categories__in = categories,
                sub_type__in = (STANDARD_PRODUCT, PRODUCT_WITH_VARIANTS),
            ).order_by(sorting)
        else:
            products = Product.objects.filter(
                categories__in = categories,
                sub_type__in = (STANDARD_PRODUCT, PRODUCT_WITH_VARIANTS),
                active = True,
            ).order_by(sorting)

        product_slugs = [p.slug for p in products]
        product_index = product_slugs.index(slug)

        if product_index > 0:
            previous = product_slugs[product_index-1]
        else:
            previous = None

        total = len(product_slugs)
        if product_index < total-1:
            next = product_slugs[product_index+1]
        else:
            next = None

        result = {
            "display" : True,
            "previous" : previous,
            "next" : next,
            "current" : product_index+1,
            "total" : total,
            "MEDIA_URL" : context.get("MEDIA_URL"),
        }

        temp[sorting] = result
        cache.set(cache_key, temp)

        return result

@register.inclusion_tag('lfs/catalog/sorting_portlet.html', takes_context=True)
def sorting_portlet(context):
    request = context.get("request")
    return {
        "current" : request.session.get("sorting"),
        "MEDIA_URL" : context.get("MEDIA_URL"),
    }

@register.inclusion_tag('lfs/shop/tabs.html', takes_context=True)
def tabs(context, obj=None):
    """
    """
    request = context.get("request")
    tabs = Action.objects.filter(active=True, place=ACTION_PLACE_TABS)
    if isinstance(obj, (Product, Category)):
        top_category = lfs.catalog.utils.get_current_top_category(request, obj)
        for tab in tabs:
            if top_category.get_absolute_url().find(tab.link) != -1:
                tab.selected = True
                break
    else:
        for tab in tabs:
            if request.path.find(tab.link) != -1:
                tab.selected = True
                break

    return {
        "tabs" : tabs,
        "MEDIA_URL" : context.get("MEDIA_URL"),
    }

@register.inclusion_tag('lfs/catalog/top_level_categories.html', takes_context=True)
def top_level_categories(context):
    """Displays the top level categories.
    """
    request = context.get("request")
    obj = context.get("product") or context.get("category")

    categories = []
    top_category = lfs.catalog.utils.get_current_top_category(request, obj)

    for category in Category.objects.filter(parent=None)[:4]:

        if top_category:
            current = top_category.id == category.id
        else:
            current = False

        categories.append({
            "url" : category.get_absolute_url(),
            "name" : category.name,
            "current" : current,
        })

    return {
        "categories" : categories,
    }

@register.inclusion_tag('lfs/shop/menu.html', takes_context=True)
def menu(context):
    """
    """
    request = context.get("request")
    current_categories = get_current_categories(request)

    categories = []
    for category in Category.objects.filter(parent = None):
        categories.append({
            "id" : category.id,
            "slug" : category.slug,
            "name" : category.name,
            "selected" : category in current_categories
        })

    return {
        "categories" : categories,
        "MEDIA_URL" : context.get("MEDIA_URL"),
    }

class CartInformationNode(Node):
    """
    """
    def render(self, context):
        request = context.get("request")
        cart = lfs.cart.utils.get_cart(request)
        if cart is None:
            amount_of_items = 0
            price = 0.0
        else:
            amount_of_items = cart.amount_of_items
            price = lfs.cart.utils.get_cart_price(request, cart, total=True)

        context["cart_amount_of_items"] = amount_of_items
        context["cart_price"] = price
        return ''

def do_cart_information(parser, token):
    """Calculates cart informations.
    """
    bits = token.contents.split()
    len_bits = len(bits)
    if len_bits != 1:
        raise TemplateSyntaxError(_('%s tag needs no argument') % bits[0])

    return CartInformationNode()

register.tag('cart_information', do_cart_information)

class CurrentCategoryNode(Node):
    """
    """
    def render(self, context):
        request = context.get("request")
        product = context.get("product")

        context["current_category"] = \
            lfs.catalog.utils.get_current_product_category(request, product)
        return ''

def do_current_category(parser, token):
    """Calculates current category.
    """
    bits = token.contents.split()
    len_bits = len(bits)
    if len_bits != 2:
        raise TemplateSyntaxError(_('%s tag needs product as argument') % bits[0])

    return CurrentCategoryNode()

register.tag('current_category', do_current_category)

# TODO: Move this to shop utils or similar
def get_slug_from_request(request):
    """Returns the slug of the currently displayed category.
    """
    slug = request.path.split("/")[-1]
    try:
        int(slug)
    except ValueError:
        pass
    else:
        slug = request.path.split("/")[-2]

    return slug

@register.filter
def currency(price, arg=None):
    """
    """
    if not price:
        price = 0.0

    # TODO: optimize
    price = lfs.utils.misc.FormatWithCommas("%.2f", price)
    shop = lfs_get_object_or_404(Shop, pk=1)

    if shop.default_country.code == "de":
        # replace . and , for german format
        a, b = price.split(".")
        a = a.replace(",", ".")
        price = "%s,%s EUR" % (a, b)
    else:
        price = "%s %s" % (price, shop.default_currency)

    return price

@register.filter
def number(price, arg=None):
    """
    """
    # TODO: optimize
    price = lfs.utils.misc.FormatWithCommas("%.2f", price)
    shop = lfs_get_object_or_404(Shop, pk=1)

    if shop.default_country.code == "de":
        # replace . and , for german format
        a, b = price.split(".")
        a = a.replace(",", ".")
        price = "%s,%s" % (a, b)

    return price

@register.filter
def quantity(quantity):
    """Removes the decimal places when they are zero.

    Means "1.0" is transformed to "1", whereas "1.1" is not transformed at all.
    """
    if str(quantity).find(".") == -1:
        return quantity
    else:
        return int(quantity)

@register.filter
def sub_type_name(sub_type, arg=None):
    """
    """
    try:
        return PRODUCT_TYPE_LOOKUP[sub_type]
    except KeyError:
        return ""

@register.filter
def multiply(score, pixel):
    """
    """
    return score * pixel

@register.filter
def option_name(option_id):
    """
    """
    try:
        option = PropertyOption.objects.get(pk=option_id)
    except (PropertyOption.DoesNotExist, ValueError):
        return option_id
    else:
        return option.name