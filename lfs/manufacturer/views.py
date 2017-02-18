from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.template.loader import render_to_string

from django.utils.translation import ungettext
from lfs.caching.utils import lfs_get_object_or_404
from lfs.manufacturer.models import Manufacturer
from lfs.core.utils import lfs_pagination


def manufacturers(request,
                  template_name='lfs/manufacturers/manufacturers.html'):
    """ Display list of all manufacturers
    """
    try:
        start = int((request.POST if request.method == 'POST' else request.GET).get("start", 1))
    except (ValueError, TypeError):
        start = 1

    manufacturers = Manufacturer.objects.all()

    # prepare paginator
    paginator = Paginator(manufacturers, 25)

    try:
        current_page = paginator.page(start)
    except (EmptyPage, InvalidPage):
        current_page = paginator.page(paginator.num_pages)

    pagination_data = lfs_pagination(request, current_page, url=reverse('lfs_manufacturers'))

    count = manufacturers.count()

    pagination_data['total_text'] = ungettext('%(count)d manufacturer',
                                              '%(count)d manufacturers',
                                              count) % {'count': count}

    return render(request, template_name, {
        "pagination": pagination_data,
        "manufacturers": current_page.object_list,
        "all_manufacturers": manufacturers  # pass it if someone doesn't want pagination
    })


def manufacturer_view(request, slug,
                      template_name="lfs/manufacturers/manufacturer.html"):
    """ Display manufacturer details and products
    """
    start = (request.POST if request.method == 'POST' else request.GET).get("start", 1)
    manufacturer = lfs_get_object_or_404(Manufacturer, slug=slug)
    inline = manufacturer_products(request, slug, start)

    # Set last visited manufacturer for later use, e.g. Display breadcrumbs,
    # selected menu points, etc.
    request.session["last_manufacturer"] = manufacturer

    return render(request, template_name, {
        "manufacturer": manufacturer,
        "manufacturer_inline": inline
    })


def manufacturer_products(request, slug, start=1,
                          template_name="lfs/manufacturers/products.html"):
    """Displays the products of the manufacturer with passed slug.
    """
    # Resets the product filters if the user navigates to another manufacturer.
    # TODO: Is this what a customer would expect?
    last_manufacturer = request.session.get("last_manufacturer")
    if (last_manufacturer is None) or (last_manufacturer.slug != slug):
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

    cache_key = "%s-manufacturer-products-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, slug)
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

    manufacturer = lfs_get_object_or_404(Manufacturer, slug=slug)

    # Calculates parameters for display.
    try:
        start = int(start)
    except (ValueError, TypeError):
        start = 1

    format_info = manufacturer.get_format_info()
    amount_of_rows = format_info["product_rows"]
    amount_of_cols = format_info["product_cols"]
    amount = amount_of_rows * amount_of_cols

    all_products = manufacturer.get_filtered_products(product_filter,
                                                      price_filter,
                                                      sorting)

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
            default_variant = product.get_default_variant()
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
    pagination_data = lfs_pagination(request,
                                     current_page,
                                     url=manufacturer.get_absolute_url())

    pagination_data['total_text'] = ungettext('%(count)d product',
                                              '%(count)d products',
                                              amount_of_products) % {'count': amount_of_products}

    result = render_to_string(template_name, request=request, context={
        "manufacturer": manufacturer,
        "products": products,
        "amount_of_products": amount_of_products,
        "pagination": pagination_data,
        "all_products": all_products,
    })

    temp[sub_cache_key] = result
    cache.set(cache_key, temp)
    return result
