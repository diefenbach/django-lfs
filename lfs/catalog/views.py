# python imports
import math
import urllib

# django imports
from django.conf import settings
from django.core.cache import cache
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
from lfs.catalog.models import Category
from lfs.catalog.models import File
from lfs.catalog.models import Product
from lfs.catalog.models import ProductPropertyValue
from lfs.catalog.models import PropertyOption
from lfs.catalog.settings import PRODUCT_WITH_VARIANTS
from lfs.catalog.settings import VARIANT
from lfs.catalog.settings import PROPERTY_VALUE_TYPE_DEFAULT
from lfs.catalog.settings import SELECT
from lfs.catalog.settings import CONTENT_PRODUCTS
from lfs.core.utils import LazyEncoder
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
    msg = _(u"The product has been changed according to your selection.")

    result = simplejson.dumps({
        "product": product_inline(request, variant_id),
        "message": msg,
    }, cls=LazyEncoder)

    return HttpResponse(result)


def calculate_packing(request, id, quantity=None, as_string=False, template_name="lfs/catalog/packing_result.html"):
    """Calculates the actual amount of pieces to buy on base on packing
    information.
    """
    product = Product.objects.get(pk=id)

    if quantity is None:
        quantity = float(request.POST.get("quantity"))

    packing_amount, packing_unit = product.get_packing_info()

    packs = math.ceil(quantity / packing_amount)
    real_quantity = packs * packing_amount
    price = real_quantity * product.get_price(request)

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

    property_price = 0
    for key, option_id in request.POST.items():
        if key.startswith("property"):
            try:
                po = PropertyOption.objects.get(pk=option_id)
            except (ValueError, PropertyOption.DoesNotExist):
                pass
            else:
                if po.property.add_price:
                    try:
                        po_price = float(po.price)
                    except (TypeError, ValueError):
                        pass
                    else:
                        property_price += po_price

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
        "price": lfs_tags.currency(price),
        "for-sale-standard-price": lfs_tags.currency(for_sale_standard_price),
        "for-sale-price": lfs_tags.currency(for_sale_price),
        "message": _("Price has been changed according to your selection."),
    }, cls=LazyEncoder)

    return HttpResponse(result)


def select_variant_from_properties(request):
    """This is called via an ajax call if the combination of properties are
    changed.
    """
    product_id = request.POST.get("product_id")

    try:
        product = Product.objects.get(pk=product_id)
    except:  # Product.DoesNotExist:
        return HttpResponse("")

    options = lfs_utils.parse_properties(request)
    variant = product.get_variant(options)

    if variant is None:
        msg = _(u"The choosen combination of properties is not deliverable.")
        variant = product.get_default_variant()
    else:
        msg = _(u"The product has been changed according to your selection.")

    result = simplejson.dumps({
        "product": product_inline(request, variant.id),
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
    except TypeError:
        min = "0"

    try:
        float(max)
    except TypeError:
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
    start = request.REQUEST.get("start", 0)
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


def category_products(request, slug, start=0, template_name="lfs/catalog/categories/product/default.html"):
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
        start = 0

    format_info = category.get_format_info()
    amount_of_rows = format_info["product_rows"]
    amount_of_cols = format_info["product_cols"]
    amount = amount_of_rows * amount_of_cols

    all_products = lfs.catalog.utils.get_filtered_products_for_category(
        category, product_filter, price_filter, sorting)

    # Calculate products
    row = []
    products = []
    for i, product in enumerate(all_products[start:start + amount]):
        # Switch to default variant if product is a "product with variants".
        # if product.is_product_with_variants() and product.has_variants():
        #    product = product.get_default_variant()
        image = None
        product_image = product.get_image()
        if product_image:
            image = product_image.image
        row.append({
            "obj": product,
            "slug": product.slug,
            "name": product.get_name(),
            "image": image,
            "price": product.get_price(request),
            "standard_price": product.get_standard_price(request),
            "for_sale_price": product.for_sale_price,
            "get_for_sale": product.get_for_sale(),
            "price_unit": product.price_unit,
            "price_includes_tax": product.price_includes_tax,
        })
        if (i + 1) % amount_of_cols == 0:
            products.append(row)
            row = []

    if len(row) > 0:
        products.append(row)

    amount_of_products = all_products.count()

    # Calculate urls
    pages = []
    for i in range(0, amount_of_products / amount + 1):
        page_start = i * amount
        pages.append({
            "name": i + 1,
            "start": page_start,
            "selected": start == page_start,
        })

    if (start + amount) < amount_of_products:
        next_url = "%s?start=%s" % (category.get_absolute_url(), start + amount)
    else:
        next_url = None

    if (start - amount) >= 0:
        previous_url = "%s?start=%s" % (category.get_absolute_url(), start - amount)
    else:
        previous_url = None

    render_template = category.get_template_name()
    if render_template != None:
        template_name = render_template

    result = render_to_string(template_name, RequestContext(request, {
        "category": category,
        "products": products,
        "next_url": next_url,
        "previous_url": previous_url,
        "amount_of_products": amount_of_products,
        "pages": pages,
        "show_pages": amount_of_products > amount,
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
        "product_inline": product_inline(request, product.id),
        "product": product,
    }))

    return result


def product_inline(request, id, template_name="lfs/catalog/products/product_inline.html"):
    """Part of the prduct view, which displays the actual data of the product.

    This is factored out to be able to better cached and in might in future used
    used to be updated via ajax requests.
    """
    cache_key = "%s-product-inline-%s-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, request.user.is_superuser, id)
    result = cache.get(cache_key)
    if result is not None:
        return result

    # Get product in question
    product = lfs_get_object_or_404(Product, pk=id)

    if product.sub_type == PRODUCT_WITH_VARIANTS:
        variant = product.get_default_variant()
        if variant is None:
            variant = product
    elif product.sub_type == VARIANT:
        variant = product
        product = product.parent
    else:
        variant = product

    properties = []
    variants = []

    if product.is_product_with_variants():
        if product.variants_display_type == SELECT:
            # Get all properties (sorted). We need to traverse through all
            # property/options to select the options of the current variant.
            for property in product.get_property_select_fields():
                options = []
                for property_option in property.options.all():
                    if variant.has_option(property, property_option):
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
            properties = product.get_property_select_fields()
            variants = product.get_variants()

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

    if variant.active_packing_unit:
        packing_result = calculate_packing(request, variant.id, 1, True)
    else:
        packing_result = ""

    result = render_to_string(template_name, RequestContext(request, {
        "product": product,
        "standard_price": variant.get_standard_price(request),
        "price": variant.get_price(request),
        "variant": variant,
        "variants": variants,
        "product_accessories": variant.get_accessories(),
        "properties": properties,
        "packing_result": packing_result,
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
