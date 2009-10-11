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
from lfs.catalog.models import Product
from lfs.catalog.settings import PRODUCT_WITH_VARIANTS, VARIANT
from lfs.catalog.settings import SELECT
from lfs.catalog.settings import CONTENT_PRODUCTS
from lfs.core.utils import LazyEncoder
from lfs.utils import misc as lfs_utils

def select_variant(request):
    """This is called via an ajax call if the combination of properties are
    changed.
    """
    variant_id = request.POST.get("variant_id")
    msg = _(u"The product has been changed according to your selection.")

    result = simplejson.dumps({
        "product" : product_inline(request, variant_id),
        "message" : msg,
    }, cls = LazyEncoder)

    return HttpResponse(result)

def select_variant_from_properties(request):
    """This is called via an ajax call if the combination of properties are
    changed.
    """
    product_id = request.POST.get("product_id")
    
    try:
        product = Product.objects.get(pk = product_id)
    except Product.DoesNotExist:
        return HttpResponse("")

    options = lfs_utils.parse_properties(request)
    variant = product.get_variant(options)

    if variant is None:
        msg = _(u"The choosen combination of properties is not deliverable.")
        variant = product.get_default_variant()
    else:
        msg = _(u"The product has been changed according to your selection.")

    result = simplejson.dumps({
        "product" : product_inline(request, variant.id),
        "message" : msg,
    }, cls = LazyEncoder)

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

    url = reverse("lfs_category", kwargs={"slug" : category_slug, "start" : 0})
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

    request.session["price-filter"] = {"min" : min, "max": max}

    url = reverse("lfs_category", kwargs={"slug" : category_slug, "start" : 0})
    return HttpResponseRedirect(url)

def reset_price_filter(request, category_slug):
    """Resets the price filter. Redirects to the category with given slug.
    """
    if request.session.has_key("price-filter"):
        del request.session["price-filter"]

    url = reverse("lfs_category", kwargs={"slug" : category_slug, "start" : 0})
    return HttpResponseRedirect(url)

def reset_filter(request, category_slug, property_id):
    """Resets product filter with given property id. Redirects to the category
    with given slug.
    """
    if request.session.has_key("product-filter"):
        if request.session["product-filter"].has_key(property_id):
            del request.session["product-filter"][property_id]
            request.session["product-filter"] = request.session["product-filter"]

    url = reverse("lfs_category", kwargs={"slug" : category_slug, "start" : 0})
    return HttpResponseRedirect(url)

def reset_all_filter(request, category_slug):
    """Resets all product filter. Redirects to the category with given slug.
    """
    if request.session.has_key("product-filter"):
        del request.session["product-filter"]

    if request.session.has_key("price-filter"):
        del request.session["price-filter"]

    url = reverse("lfs_category", kwargs={"slug" : category_slug, "start" : 0})
    return HttpResponseRedirect(url)

def set_sorting(request):
    """Saves the given sortings (by request body) to session.
    """
    sorting = request.POST.get("sorting", "")
    if sorting == "" and request.session.has_key("sorting"):
        del request.session["sorting"]
    else:
        request.session["sorting"] = sorting

    # lfs_sorting_changed.send(category_id)
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

def category_view(request, slug, start=0, template_name="lfs/catalog/category_base.html"):
    """
    """
    category = lfs_get_object_or_404(Category, slug=slug)

    if category.content == CONTENT_PRODUCTS:
        inline = category_products(request, slug, start)
    else:
        inline = category_categories(request, slug)

    # Set last visited category for later use, e.g. Display breadcrumbs,
    # selected menu points, etc.
    request.session["last_category"] = category

    # TODO: Factor top_category out to a inclusion tag, so that people can
    # omit if they don't need it.

    return render_to_response(template_name, RequestContext(request, {
        "category" : category,
        "category_inline" : inline,
        "top_category" : lfs.catalog.utils.get_current_top_category(request, category),
    }))

def category_categories(request, slug, template_name="lfs/catalog/category_categories.html"):
    """Displays the child categories of the category with passed slug.

    This is displayed if the category's content attribute is set to categories".
    """
    cache_key = "category-categories-%s" % slug

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
        if (i+1) % amount_of_cols == 0:
            categories.append(row)
            row = []

    if len(row) > 0:
        categories.append(row)

    result = render_to_string(template_name, RequestContext(request, {
        "category" : category,
        "categories" : categories,
    }))

    cache.set(cache_key, result)
    return result

def category_products(request, slug, start=0, template_name="lfs/catalog/category_products.html"):
    """Displays the products of the category with passed slug.

    This is displayed if the category's content attribute is set to products.
    """
    # Resets the product filters if the user navigates to another category.
    # TODO: Is this what a customer would expect?
    last_category = request.session.get("last_category")
    if (last_category is None) or (last_category.slug != slug):
        if request.session.has_key("product-filter"):
            del request.session["product-filter"]
        if request.session.has_key("price-filter"):
            del request.session["price-filter"]

    sorting = request.session.get("sorting", "price")
    product_filter = request.session.get("product-filter", {})
    product_filter = product_filter.items()

    cache_key = "category-products-%s" % slug
    sub_cache_key = "start-%s-sorting-%s" % (start, sorting)

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
    except ValueError:
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
    for i, product in enumerate(all_products[start:start+amount]):
        # Switch to default variant if product is a "product with variants".
        if product.is_product_with_variants() and product.has_variants():
            product = product.get_default_variant()
        row.append(product)
        if (i+1) % amount_of_cols == 0:
            products.append(row)
            row = []

    if len(row) > 0:
        products.append(row)

    amount_of_products = all_products.count()

    # Calculate urls
    pages = []
    for i in range(0, amount_of_products/amount+1):
        page_start = i*amount
        pages.append({
            "name" : i+1,
            "start" : page_start,
            "selected" : start == page_start,
        })

    if (start + amount) < amount_of_products:
        next_url = "%s/%s" % (category.get_absolute_url(), start + amount)
    else:
        next_url = None

    if (start - amount) >= 0:
        previous_url = "%s/%s" % (category.get_absolute_url(), start - amount)
    else:
        previous_url = None

    result = render_to_string(template_name, RequestContext(request, {
        "category" : category,
        "products" : products,
        "next_url" : next_url,
        "previous_url" : previous_url,
        "amount_of_products" : amount_of_products,
        "pages" : pages,
        "show_pages" : amount_of_products > amount,
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
        recent = recent[:settings.LFS_RECENT_PRODUCTS_LIMIT+1]
    request.session["RECENT_PRODUCTS"] = recent

    # TODO: Factor top_category out to a inclusion tag, so that people can
    # omit if they don't need it.

    return render_to_response(template_name, RequestContext(request, {
        "product_inline" : product_inline(request, product.id),
        "product" : product,
        "top_category" : lfs.catalog.utils.get_current_top_category(request, product),
    }))

def product_inline(request, id, template_name="lfs/catalog/product_inline.html"):
    """Part of the prduct view, which displays the actual data of the product.

    This is factored out to be able to better cached and in might in future used
    used to be updated via ajax requests.
    """
    cache_key = "product-inline-%s-%s" % (request.user.is_superuser, id)
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
    if product.variants_display_type == SELECT:
        # Get all properties (sorted). We need to traverse through all
        # property/options to select the options of the current variant.
        for property in product.get_properties():
            options = []
            for property_option in property.options.all():
                if variant.has_option(property, property_option):
                    selected = True
                else:
                    selected = False
                options.append({
                    "id"   : property_option.id,
                    "name" : property_option.name,
                    "selected" : selected
                })
            properties.append({
                "id" : property.id,
                "name" : property.name,
                "options" : options
            })
    else:
        properties = product.get_properties()
        variants = product.get_variants()

    # Reviews

    result = render_to_string(template_name, RequestContext(request, {
        "product" : product,
        "variant" : variant,
        "variants" : variants,
        "product_accessories" : variant.get_accessories(),
        "properties" : properties
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
        product = Product.objects.get(pk=product_id)

        options = lfs_utils.parse_properties(request)
        variant = product.get_variant(options)

        if variant is None:
            variant = product.get_default_variant()

            return lfs.core.utils.set_message_cookie(
                variant.get_absolute_url(),
                msg = _(u"The choosen combination of properties is not deliverable.")
            )

        return HttpResponseRedirect(variant.get_absolute_url())

# NOT used at moment
def get_category_nodes(request):
    """Returns the category tree as JSON for extJS.
    """
    categories = []
    for category in Category.objects.filter(parent = None):
        temp = _get_children_nodes(category)
        categories.append({
            "id" : category.slug,
            "text" : category.name,
            "leaf" : len(temp) == 0,
            "children" : temp
        })

    return HttpResponse(simplejson.dumps(categories))

def _get_children_nodes(category):
    """
    """
    children = []
    for category in category.category_set.all():
        temp = _get_children_nodes(category)
        children.append({
            "id" : category.slug,
            "text" : category.name,
            "leaf" : len(temp) == 0,
            "children" : temp,
        })

    return children
