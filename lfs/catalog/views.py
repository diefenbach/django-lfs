# python imports
import math
import urllib

# django imports
from django.conf import settings
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

# lfs imports
import lfs.catalog.utils
import lfs.core.utils
from lfs.caching.utils import lfs_get_object_or_404
from lfs.cart.views import add_to_cart
from lfs.catalog.models import Category, Property
from lfs.catalog.models import File
from lfs.catalog.models import Product
from lfs.catalog.models import ProductPropertyValue
from lfs.catalog.models import PropertyOption
from lfs.catalog.models import ProductAttachment
from lfs.catalog.settings import CATEGORY_VARIANT_CHEAPEST_PRICES
from lfs.catalog.settings import CONTENT_PRODUCTS
from lfs.catalog.settings import PRODUCT_WITH_VARIANTS
from lfs.catalog.settings import PROPERTY_VALUE_TYPE_DEFAULT
from lfs.catalog.settings import SELECT
from lfs.catalog.settings import VARIANT
from lfs.core.utils import LazyEncoder, lfs_pagination
from lfs.core.templatetags import lfs_tags
from lfs.utils import misc as lfs_utils


def file(request, language=None, id=None):
    """Delivers files to the browser.
    """
    file = lfs_get_object_or_404(File, pk=id)
    response = HttpResponse(file.file, mimetype='application/binary')
    response['Content-Disposition'] = 'attachment; filename=%s' % file.title

    return response


def select_variant(request):
    """This is called via an ajax call if the combination of properties are
    changed.
    """
    variant_id = request.POST.get("variant_id")
    variant = Product.objects.get(pk=variant_id)
    msg = _(u"The product has been changed according to your selection.")

    result = simplejson.dumps({
        "product": product_inline(request, variant),
        "message": msg,
    }, cls=LazyEncoder)

    return HttpResponse(result)


def calculate_packing(request, id, quantity=None, with_properties=False, as_string=False, template_name="lfs/catalog/packing_result.html"):
    """Calculates the actual amount of pieces to buy on base on packing
    information.
    """
    product = Product.objects.get(pk=id)

    if quantity is None:
        try:
            quantity = float(request.POST.get("quantity"))
        except (TypeError, ValueError):
            quantity = 1

    packing_amount, packing_unit = product.get_packing_info()

    try:
        packs = math.ceil(quantity / packing_amount)
        real_quantity = packs * packing_amount
        price = product.get_price_gross(request, with_properties=with_properties)
        price += _calculate_property_price(request)
        price *= real_quantity
    except TypeError:
        packs = 0.0
        real_quantity = 0.0
        price = 0.0

    html = render_to_string(template_name, RequestContext(request, {
        "price": price,
        "product": product,
        "packs": int(packs),
        "real_quantity": real_quantity,
        "unit": packing_unit,
    }))

    if as_string:
        return html

    result = simplejson.dumps({
        "html": html,
    }, cls=LazyEncoder)

    return HttpResponse(result)


def calculate_price(request, id):
    """Calculates the price of the product on base of choosen properties after
    a customer has selected a property on product view.
    """
    product = Product.objects.get(pk=id)
    property_price = _calculate_property_price(request)

    if product.for_sale:
        for_sale_standard_price = product.get_standard_price(request, with_properties=False)
        for_sale_standard_price += property_price

        for_sale_price = product.get_for_sale_price(request, with_properties=False)
        for_sale_price += property_price
    else:
        for_sale_standard_price = 0
        for_sale_price = 0

    price = product.get_price(request, with_properties=False)
    price += property_price

    result = simplejson.dumps({
        "price": lfs_tags.currency(price, request),
        "for-sale-standard-price": lfs_tags.currency(for_sale_standard_price),
        "for-sale-price": lfs_tags.currency(for_sale_price),
        "packing-result": calculate_packing(request, id, as_string=True),
        "message": _("Price has been changed according to your selection."),
    }, cls=LazyEncoder)

    return HttpResponse(result)


def select_variant_from_properties(request):
    """
    This is called via an ajax call if the combination of properties are
    changed.
    """
    product_id = request.POST.get("product_id")

    try:
        variant = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return HttpResponse("")
    else:
        product = variant.parent

    options = lfs_utils.parse_properties(request)
    variant = product.get_variant(options)

    if variant is None:
        msg = _(u"The choosen combination of properties is not deliverable.")
        variant = product.get_default_variant()
    else:
        msg = _(u"The product has been changed according to your selection.")

    result = simplejson.dumps({
        "product": product_inline(request, variant),
        "message": msg,
    }, cls=LazyEncoder)

    return HttpResponse(result)


def set_filter(request, category_slug, property_id, value=None, min=None, max=None):
    """Saves the given filter to session. Redirects to the category with given
    slug.
    """
    product_filter = request.session.get("product-filter", {})

    if value is not None:
        product_filter[property_id] = value
    else:
        product_filter[property_id] = (min, max)

    request.session["product-filter"] = product_filter

    url = reverse("lfs_category", kwargs={"slug": category_slug})
    return HttpResponseRedirect(url)


def set_price_filter(request, category_slug):
    """Saves the given price filter to session. Redirects to the category with
    given slug.
    """
    min = request.REQUEST.get("min", "0")
    max = request.REQUEST.get("max", "99999")

    try:
        float(min)
    except (TypeError, ValueError):
        min = "0"

    try:
        float(max)
    except (TypeError, ValueError):
        max = "0"

    request.session["price-filter"] = {"min": min, "max": max}

    url = reverse("lfs_category", kwargs={"slug": category_slug})
    return HttpResponseRedirect(url)


def reset_price_filter(request, category_slug):
    """Resets the price filter. Redirects to the category with given slug.
    """
    if "price-filter" in request.session:
        del request.session["price-filter"]

    url = reverse("lfs_category", kwargs={"slug": category_slug})
    return HttpResponseRedirect(url)


def reset_filter(request, category_slug, property_id):
    """Resets product filter with given property id. Redirects to the category
    with given slug.
    """
    if "product-filter" in request.session:
        if property_id in request.session["product-filter"]:
            del request.session["product-filter"][property_id]
            request.session["product-filter"] = request.session["product-filter"]

    url = reverse("lfs_category", kwargs={"slug": category_slug})
    return HttpResponseRedirect(url)


def reset_all_filter(request, category_slug):
    """Resets all product filter. Redirects to the category with given slug.
    """
    if "product-filter" in request.session:
        del request.session["product-filter"]

    if "price-filter" in request.session:
        del request.session["price-filter"]

    url = reverse("lfs_category", kwargs={"slug": category_slug})
    return HttpResponseRedirect(url)


def set_sorting(request):
    """Saves the given sortings (by request body) to session.
    """
    sorting = request.POST.get("sorting", "")
    if sorting == "" and "sorting" in request.session:
        del request.session["sorting"]
    else:
        request.session["sorting"] = sorting

    # lfs_sorting_changed.send(category_id)
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def category_view(request, slug, template_name="lfs/catalog/category_base.html"):
    """
    """
    start = request.REQUEST.get("start", 1)
    category = lfs_get_object_or_404(Category, slug=slug)
    if category.get_content() == CONTENT_PRODUCTS:
        inline = category_products(request, slug, start)
    else:
        inline = category_categories(request, slug)
    # Set last visited category for later use, e.g. Display breadcrumbs,
    # selected menu points, etc.
    request.session["last_category"] = category

    # TODO: Factor top_category out to a inclusion tag, so that people can
    # omit if they don't need it.

    return render_to_response(template_name, RequestContext(request, {
        "category": category,
        "category_inline": inline,
        "top_category": lfs.catalog.utils.get_current_top_category(request, category),
    }))


def category_categories(request, slug, start=0, template_name="lfs/catalog/categories/category/default.html"):
    """Displays the child categories of the category with passed slug.

    This view is called if the user chooses a template that is situated in settings.CATEGORY_PATH ".
    """
    cache_key = "%s-category-categories-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, slug)

    result = cache.get(cache_key)
    if result is not None:
        return result

    category = lfs_get_object_or_404(Category, slug=slug)

    format_info = category.get_format_info()
    amount_of_cols = format_info["category_cols"]

    categories = []
    row = []
    for i, children in enumerate(category.get_children()):
        row.append(children)
        if (i + 1) % amount_of_cols == 0:
            categories.append(row)
            row = []

    if len(row) > 0:
        categories.append(row)
    render_template = category.get_template_name()

    if render_template != None:
        template_name = render_template

    result = render_to_string(template_name, RequestContext(request, {
        "category": category,
        "categories": categories,
    }))

    cache.set(cache_key, result)
    return result


def category_products(request, slug, start=1, template_name="lfs/catalog/categories/product/default.html"):
    """Displays the products of the category with passed slug.

    This view is called if the user chooses a template that is situated in settings.PRODUCT_PATH ".
    """
    # Resets the product filters if the user navigates to another category.
    # TODO: Is this what a customer would expect?
    last_category = request.session.get("last_category")
    if (last_category is None) or (last_category.slug != slug):
        if "product-filter" in request.session:
            del request.session["product-filter"]
        if "price-filter" in request.session:
            del request.session["price-filter"]

    try:
        default_sorting = settings.LFS_PRODUCTS_SORTING
    except AttributeError:
        default_sorting = "price"

    sorting = request.session.get("sorting", default_sorting)
    product_filter = request.session.get("product-filter", {})
    product_filter = product_filter.items()

    cache_key = "%s-category-products-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, slug)
    sub_cache_key = "%s-start-%s-sorting-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, start, sorting)

    filter_key = ["%s-%s" % (i[0], i[1]) for i in product_filter]
    if filter_key:
        sub_cache_key += "-%s" % "-".join(filter_key)

    price_filter = request.session.get("price-filter")
    if price_filter:
        sub_cache_key += "-%s-%s" % (price_filter["min"], price_filter["max"])

    temp = cache.get(cache_key)
    if temp is not None:
        try:
            return temp[sub_cache_key]
        except KeyError:
            pass
    else:
        temp = dict()

    category = lfs_get_object_or_404(Category, slug=slug)

    # Calculates parameters for display.
    try:
        start = int(start)
    except (ValueError, TypeError):
        start = 1

    format_info = category.get_format_info()
    amount_of_rows = format_info["product_rows"]
    amount_of_cols = format_info["product_cols"]
    amount = amount_of_rows * amount_of_cols

    all_products = lfs.catalog.utils.get_filtered_products_for_category(
        category, product_filter, price_filter, sorting)

    # prepare paginator
    paginator = Paginator(all_products, amount)

    try:
        current_page = paginator.page(start)
    except (EmptyPage, InvalidPage):
        current_page = paginator.page(paginator.num_pages)

    # Calculate products
    row = []
    products = []
    for i, product in enumerate(current_page.object_list):
        if product.is_product_with_variants():
            default_variant = product.get_variant_for_category(request)
            if default_variant:
                product = default_variant

        image = None
        product_image = product.get_image()
        if product_image:
            image = product_image.image
        row.append({
            "obj": product,
            "slug": product.slug,
            "name": product.get_name(),
            "image": image,
            "price_unit": product.price_unit,
            "price_includes_tax": product.price_includes_tax(request),
        })
        if (i + 1) % amount_of_cols == 0:
            products.append(row)
            row = []

    if len(row) > 0:
        products.append(row)

    amount_of_products = all_products.count()

    # Calculate urls
    pagination_data = lfs_pagination(request, current_page, url=category.get_absolute_url())

    render_template = category.get_template_name()
    if render_template != None:
        template_name = render_template

    result = render_to_string(template_name, RequestContext(request, {
        "category": category,
        "products": products,
        "amount_of_products": amount_of_products,
        "pagination": pagination_data,
        "all_products": all_products,
    }))

    temp[sub_cache_key] = result
    cache.set(cache_key, temp)
    return result


def product_view(request, slug, template_name="lfs/catalog/product_base.html"):
    """Main view to display a product.
    """
    product = lfs_get_object_or_404(Product, slug=slug)

    if (request.user.is_superuser or product.is_active()) == False:
        raise Http404()

    # Store recent products for later use
    recent = request.session.get("RECENT_PRODUCTS", [])
    if slug in recent:
        recent.remove(slug)
    recent.insert(0, slug)
    if len(recent) > settings.LFS_RECENT_PRODUCTS_LIMIT:
        recent = recent[:settings.LFS_RECENT_PRODUCTS_LIMIT + 1]
    request.session["RECENT_PRODUCTS"] = recent

    result = render_to_response(template_name, RequestContext(request, {
        "product_inline": product_inline(request, product),
        "product": product,
    }))

    return result


def product_inline(request, product, template_name="lfs/catalog/products/product_inline.html"):
    """
    Part of the product view, which displays the actual data of the product.

    This is factored out to be able to better cached and in might in future used
    used to be updated via ajax requests.
    """
    cache_key = "%s-product-inline-%s-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, request.user.is_superuser, product.id)
    result = cache.get(cache_key)
    if result is not None:
        return result

    # Switching to default variant
    if product.is_product_with_variants():
        temp = product.get_default_variant()
        product = temp if temp else product

    properties = []
    variants = []

    display_variants_list = True
    if product.is_variant():
        parent = product.parent
        if parent.variants_display_type == SELECT:
            display_variants_list = False
            # Get all properties (sorted). We need to traverse through all
            # property/options to select the options of the current variant.
            for property in parent.get_property_select_fields():
                options = []
                for property_option in property.options.all():
                    if product.has_option(property, property_option):
                        selected = True
                    else:
                        selected = False
                    options.append({
                        "id": property_option.id,
                        "name": property_option.name,
                        "selected": selected,
                    })
                properties.append({
                    "id": property.id,
                    "name": property.name,
                    "title": property.title,
                    "unit": property.unit,
                    "options": options,
                })
        else:
            properties = parent.get_property_select_fields()
            variants = parent.get_variants()

    elif product.is_configurable_product():
        for property in product.get_configurable_properties():
            options = []
            try:
                ppv = ProductPropertyValue.objects.get(product=product, property=property, type=PROPERTY_VALUE_TYPE_DEFAULT)
                ppv_value = ppv.value
            except ProductPropertyValue.DoesNotExist:
                ppv = None
                ppv_value = ""

            for property_option in property.options.all():
                if ppv_value == str(property_option.id):
                    selected = True
                else:
                    selected = False

                options.append({
                    "id": property_option.id,
                    "name": property_option.name,
                    "price": property_option.price,
                    "selected": selected,
                })
            properties.append({
                "obj": property,
                "id": property.id,
                "name": property.name,
                "title": property.title,
                "unit": property.unit,
                "display_price": property.display_price,
                "options": options,
                "value": ppv_value,
            })

    if product.get_template_name() != None:
        template_name = product.get_template_name()

    if product.get_active_packing_unit():
        packing_result = calculate_packing(request, product.id, 1, True, True)
    else:
        packing_result = ""

    # attachments
    attachments = product.get_attachments()

    result = render_to_string(template_name, RequestContext(request, {
        "product": product,
        "variants": variants,
        "product_accessories": product.get_accessories(),
        "properties": properties,
        "packing_result": packing_result,
        "attachments": attachments,
        "quantity": product.get_clean_quantity(1),
        "price_includes_tax": product.price_includes_tax(request),
        "price_unit": product.get_price_unit(),
        "unit": product.get_unit(),
        "display_variants_list": display_variants_list,
        "for_sale": product.for_sale,
    }))

    cache.set(cache_key, result)
    return result


def product_form_dispatcher(request):
    """Dispatches to the added-to-cart view or to the selected variant.

    This is needed as the product form can have several submit buttons:
       - The add-to-cart button
       - The switch to the selected variant button (only in the case the
         variants of of the product are displayed as select box. This may change
         in future, when the switch may made with an ajax request.)
    """
    if request.REQUEST.get("add-to-cart") is not None:
        return add_to_cart(request)
    else:
        product_id = request.POST.get("product_id")
        product = lfs_get_object_or_404(Product, pk=product_id)

        options = lfs_utils.parse_properties(request)
        variant = product.get_variant(options)

        if variant is None:
            variant = product.get_default_variant()

            return lfs.core.utils.set_message_cookie(
                variant.get_absolute_url(),
                msg=_(u"The choosen combination of properties is not deliverable.")
            )

        return HttpResponseRedirect(variant.get_absolute_url())


def _calculate_property_price(request):
    """
    Calculates the price of the currently selected properties.
    """
    property_price = 0
    for key, option_id in request.POST.items():
        if key.startswith("property"):
            try:
                property_id = int(key.split('-')[1])
                property = Property.objects.get(pk=property_id)
                if property.is_select_field:
                    po = PropertyOption.objects.get(property=property, pk=option_id)
                    if property.add_price:
                        po_price = float(po.price)
                        property_price += po_price
            except (IndexError, ValueError, TypeError, PropertyOption.DoesNotExist, Property.DoesNotExist):
                pass
    return property_price
