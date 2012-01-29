# python imports
import math
import locale

# django imports
from django import template
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.template import Node, TemplateSyntaxError
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

# lfs imports
import lfs.catalog.utils
import lfs.utils.misc
from lfs.caching.utils import lfs_get_object_or_404
from lfs.catalog.models import Category
from lfs.catalog.settings import PRODUCT_WITH_VARIANTS
from lfs.catalog.settings import STANDARD_PRODUCT
from lfs.catalog.settings import CONFIGURABLE_PRODUCT
from lfs.catalog.models import Product
from lfs.catalog.models import PropertyOption
from lfs.catalog.settings import PRODUCT_TYPE_LOOKUP
import lfs.core.utils
from lfs.core.models import Shop
from lfs.core.models import Action
from lfs.page.models import Page
from lfs.shipping import utils as shipping_utils

register = template.Library()


@register.inclusion_tag('lfs/portlets/category_children.html', takes_context=True)
def category_children(context, categories):
    """
    """
    return {"categories": categories}


@register.inclusion_tag('lfs/shop/google_analytics_tracking.html', takes_context=True)
def google_analytics_tracking(context):
    """Returns google analytics tracking code which has been entered to the
    shop.
    """
    shop = lfs_get_object_or_404(Shop, pk=1)
    return {
        "ga_site_tracking": shop.ga_site_tracking,
        "google_analytics_id": shop.google_analytics_id,
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
    if clear_session and "order" in request.session:
        del request.session["order"]

    if "voucher" in request.session:
        del request.session["voucher"]

    return {
        "order": order,
        "ga_ecommerce_tracking": shop.ga_ecommerce_tracking,
        "google_analytics_id": shop.google_analytics_id,
    }


def _get_shipping(context, product):
    request = context.get("request")
    if product.is_deliverable() == False:
        return {
            "deliverable": False,
            "delivery_time": shipping_utils.get_product_delivery_time(request, product.slug)
        }
    else:
        return {
            "deliverable": True,
            "delivery_time": shipping_utils.get_product_delivery_time(request, product.slug)
        }


@register.inclusion_tag('lfs/shipping/shipping_tag.html', takes_context=True)
def shipping(context, variant):
    return _get_shipping(context, variant)


@register.inclusion_tag('lfs/catalog/sorting.html', takes_context=True)
def sorting(context):
    """
    """
    request = context.get("request")
    return {"current": request.session.get("sorting")}


@register.inclusion_tag('lfs/catalog/breadcrumbs.html', takes_context=True)
def breadcrumbs(context, obj):
    """
    """
    if isinstance(obj, Category):
        cache_key = "%s-category-breadcrumbs-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, obj.slug)
        objects = cache.get(cache_key)
        if objects is not None:
            return objects

        objects = []
        while obj is not None:
            objects.insert(0, {
                "name": obj.name,
                "url": obj.get_absolute_url(),
            })
            obj = obj.parent

        result = {
            "objects": objects,
            "STATIC_URL": context.get("STATIC_URL"),
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
            category = obj.get_current_category(request)
            if category is None:
                return []
            else:
                objects = [{
                    "name": obj.get_name(),
                    "url": obj.get_absolute_url(),
                }]
                while category is not None:
                    objects.insert(0, {
                        "name": category.name,
                        "url": category.get_absolute_url(),
                    })
                    category = category.parent

        result = {
            "objects": objects,
            "STATIC_URL": context.get("STATIC_URL"),
        }

    elif isinstance(obj, Page):
        objects = []
        objects.append({
            "name": _(u"Information"),
            "get_absolute_url": reverse("lfs_pages")}),
        objects.append({"name": obj.title})

        result = {
            "objects": objects,
            "STATIC_URL": context.get("STATIC_URL"),
        }
    else:
        result = {
            "objects": ({"name": obj},),
            "STATIC_URL": context.get("STATIC_URL"),
        }

    return result


@register.inclusion_tag('lfs/catalog/product_navigation.html', takes_context=True)
def product_navigation(context, product):
    """Provides previous and next product links.
    """
    request = context.get("request")
    sorting = request.session.get("sorting", "price")
    if sorting == "":
        sorting = "price"

    slug = product.slug

    cache_key = "%s-product-navigation-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, slug)
    temp = None  # cache.get(cache_key)

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

    category = product.get_current_category(request)
    if category is None:
        return {"display": False}
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
                categories__in=categories,
                sub_type__in=(STANDARD_PRODUCT, PRODUCT_WITH_VARIANTS, CONFIGURABLE_PRODUCT),
            ).order_by(sorting)
        else:
            products = Product.objects.filter(
                categories__in=categories,
                sub_type__in=(STANDARD_PRODUCT, PRODUCT_WITH_VARIANTS, CONFIGURABLE_PRODUCT),
                active=True,
            ).order_by(sorting)

        product_slugs = [p.slug for p in products]
        product_index = product_slugs.index(slug)

        if product_index > 0:
            previous = product_slugs[product_index - 1]
        else:
            previous = None

        total = len(product_slugs)
        if product_index < total - 1:
            next = product_slugs[product_index + 1]
        else:
            next = None

        result = {
            "display": True,
            "previous": previous,
            "next": next,
            "current": product_index + 1,
            "total": total,
            "STATIC_URL": context.get("STATIC_URL"),
        }

        temp[sorting] = result
        cache.set(cache_key, temp)

        return result


class ActionsNode(Node):
    def __init__(self, group_name):
        self.group_name = group_name

    def render(self, context):
        request = context.get("request")
        context["actions"] = Action.objects.filter(active=True, group__name=self.group_name)
        return ''


def do_actions(parser, token):
    """Returns the actions for the group with the given id.
    """
    bits = token.contents.split()
    len_bits = len(bits)
    if len_bits != 2:
        raise TemplateSyntaxError(_('%s tag needs group id as argument') % bits[0])

    return ActionsNode(bits[1])
register.tag('actions', do_actions)


@register.inclusion_tag('lfs/shop/tabs.html', takes_context=True)
def tabs(context, obj=None):
    """
    """
    if obj is None:
        obj = context.get("product") or context.get("category")

    request = context.get("request")
    tabs = Action.objects.filter(active=True, group=1)
    if isinstance(obj, (Product, Category)):
        top_category = lfs.catalog.utils.get_current_top_category(request, obj)
        if top_category:
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
        "tabs": tabs,
        "STATIC_URL": context.get("STATIC_URL"),
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
            "url": category.get_absolute_url(),
            "name": category.name,
            "current": current,
        })

    return {
        "categories": categories,
    }


class TopLevelCategory(Node):
    """Calculates the current top level category.
    """
    def render(self, context):
        request = context.get("request")
        obj = context.get("product") or context.get("category")

        top_level_category = lfs.catalog.utils.get_current_top_category(request, obj)
        context["top_level_category"] = top_level_category.name
        return ''


def do_top_level_category(parser, token):
    """Calculates the current top level category.
    """
    bits = token.contents.split()
    len_bits = len(bits)
    if len_bits != 1:
        raise TemplateSyntaxError(_('%s tag needs no argument') % bits[0])

    return TopLevelCategory()
register.tag('top_level_category', do_top_level_category)


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
            amount_of_items = cart.get_amount_of_items()
            price = cart.get_price_gross(request, total=True)

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
            product.get_current_category(request)
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
def currency(value, grouping=True):
    """
    e.g.
    import locale
    locale.setlocale(locale.LC_ALL, 'de_CH.UTF-8')
    currency(123456.789)  # Fr. 123'456.79
    currency(-123456.789) # <span class="negative">Fr. -123'456.79</span>
    """
    if not value:
        value = 0.0

    shop = lfs.core.utils.get_default_shop()
    result = locale.currency(value, grouping=grouping, international=shop.use_international_currency_code)
    # add css class if value is negative
    if value < 0:
        # replace the minus symbol if needed
        if result[-1] == '-':
            length = len(locale.nl_langinfo(locale.CRNCYSTR))
            result = '%s-%s' % (result[0:length], result[length:-1])
        return mark_safe('<span class="negative">%s</span>' % result)
    return result

@register.filter
def decimal_l10n(value):
    """Returns the decimal value of value based on current locale.
    """
    return locale.format_string("%.2f", value)


@register.filter
def quantity(quantity):
    """Removes the decimal places when they are zero.

    Means "1.0" is transformed to "1", whereas "1.1" is not transformed at all.
    """
    if str(quantity).find(".0") == -1:
        return quantity
    else:
        return int(float(quantity))


@register.filter
def sub_type_name(sub_type, arg=None):
    """Returns the sub type name for the sub type with passed sub_type id.
    """
    try:
        return PRODUCT_TYPE_LOOKUP[sub_type]
    except KeyError:
        return ""


@register.filter
def multiply(score, pixel):
    """Returns the result of score * pixel
    """
    return score * pixel


@register.filter
def option_name(option_id):
    """Returns the option name for option with passed id.
    """
    try:
        option_id = int(float(option_id))
    except ValueError:
        pass

    try:
        option = PropertyOption.objects.get(pk=option_id)
    except (PropertyOption.DoesNotExist, ValueError):
        return option_id
    else:
        return option.name


@register.filter
def option_name_for_property_value(property_value):
    """Returns the value or the option name for passed property_value
    """
    if property_value.property.is_select_field:
        try:
            option_id = int(float(property_value.value))
        except ValueError:
            return property_value.value

        try:
            option = PropertyOption.objects.get(pk=option_id)
        except (PropertyOption.DoesNotExist, ValueError):
            return option_id
        else:
            return option.name

    return property_value.value


@register.filter
def packages(cart_item):
    """Returns the packages based on product's package unit and cart items
    amount.
    """
    cart_item = cart_item.get("obj")
    if cart_item.product.packing_unit:
        return int(math.ceil(cart_item.amount / cart_item.product.packing_unit))
    return 0


@register.filter(name='get_price')
def get_price(product, request):
    return product.get_price(request)


@register.filter(name='get_for_sale_price')
def get_for_sale_price(product, request):
    return product.get_for_sale_price(request)

@register.filter(name='get_standard_price')
def get_standard_price(product, request):
    return product.get_standard_price(request)
