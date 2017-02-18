import locale
import math
import json

from django.conf import settings
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _, ungettext
from django.views.decorators.csrf import csrf_exempt

import lfs.catalog.utils
import lfs.core.utils
import lfs.utils.misc
from lfs.caching.utils import lfs_get_object_or_404, get_cache_group_id
from lfs.cart.views import add_to_cart
from lfs.catalog.models import Category, Property
from lfs.catalog.models import File
from lfs.catalog.models import Product
from lfs.catalog.models import ProductPropertyValue
from lfs.catalog.models import PropertyOption
from lfs.catalog.settings import CONTENT_PRODUCTS
from lfs.catalog.settings import PROPERTY_VALUE_TYPE_DEFAULT
from lfs.catalog.settings import SELECT
from lfs.core.utils import LazyEncoder, lfs_pagination
from lfs.core.templatetags import lfs_tags
from lfs.manufacturer.models import Manufacturer


def file_download(request, language=None, file_id=None):
    """Delivers files to the browser.
    """
    download_file = lfs_get_object_or_404(File, pk=file_id)
    response = HttpResponse(download_file.file, content_type='application/binary')
    response['Content-Disposition'] = 'attachment; filename=%s' % download_file.title

    return response


def select_variant(request):
    """This is called via an ajax call if the combination of properties are
    changed.
    """
    variant_id = request.POST.get("variant_id")
    variant = Product.objects.get(pk=variant_id)
    msg = _(u"The product has been changed according to your selection.")

    result = json.dumps({
        "product": product_inline(request, variant),
        "message": msg,
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


def calculate_packing(request, id, quantity=None, with_properties=False, as_string=False, template_name="lfs/catalog/packing_result.html"):
    """Calculates the actual amount of pieces to buy on base on packing
    information.
    """
    product = Product.objects.get(pk=id)

    if quantity is None:
        try:
            quantity = request.POST.get("quantity")
            if isinstance(quantity, unicode):
                # atof() on unicode string fails in some environments, like Czech
                quantity = quantity.encode("utf-8")
            quantity = locale.atof(quantity)
        except (AttributeError, TypeError, ValueError):
            quantity = 1

    packing_amount, packing_unit = product.get_packing_info()

    try:
        packs = math.ceil(quantity / packing_amount)
        real_quantity = packs * packing_amount
        price = product.get_price_gross(request, with_properties=with_properties, amount=quantity)
        price += _calculate_property_price(request)
        price *= real_quantity
    except TypeError:
        packs = 0.0
        real_quantity = 0.0
        price = 0.0

    html = render_to_string(template_name, request=request, context={
        "price": price,
        "product": product,
        "packs": int(packs),
        "real_quantity": real_quantity,
        "unit": packing_unit,
    })

    if as_string:
        return html

    result = json.dumps({
        "html": html,
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


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

    if product.get_active_packing_unit():
        packing_result = calculate_packing(request, id, with_properties=True, as_string=True)
    else:
        packing_result = ""

    result = json.dumps({
        "price": lfs_tags.currency(price, request),
        "for-sale-standard-price": lfs_tags.currency(for_sale_standard_price),
        "for-sale-price": lfs_tags.currency(for_sale_price),
        "packing-result": packing_result,
        "message": _("Price has been changed according to your selection."),
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


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

    options = lfs.utils.misc.parse_properties(request)
    variant = product.get_variant(options)

    if variant is None:
        msg = _(u"The choosen combination of properties is not deliverable.")
        variant = product.get_default_variant()
    else:
        msg = _(u"The product has been changed according to your selection.")

    result = json.dumps({
        "product": product_inline(request, variant),
        "message": msg,
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


def set_number_filter(request):
    product_filter = request.session.get("product-filter", {})
    if product_filter.get("number-filter") is None:
        product_filter["number-filter"] = {}

    pmin = lfs.core.utils.atof(request.POST.get("min", 1))
    pmax = lfs.core.utils.atof(request.POST.get("max", 1))

    property_id = request.POST.get("property_id")
    property_group_id = request.POST.get("property_group_id")
    category_slug = request.POST.get("category_slug")

    key = '{0}_{1}'.format(property_group_id, property_id)

    product_filter["number-filter"][key] = {'property_id': property_id,
                                            'property_group_id': property_group_id,
                                            'value': (pmin, pmax)}
    request.session["product-filter"] = product_filter

    url = reverse("lfs_category", kwargs={"slug": category_slug})
    return HttpResponseRedirect(url)


def set_filter(request, category_slug, property_group_id, property_id, value=None, min=None, max=None):
    """Saves the given filter to session. Redirects to the category with given
    slug.
    """
    product_filter = request.session.get("product-filter", {})
    if product_filter.get("select-filter") is None:
        product_filter["select-filter"] = {}

    key = '{0}_{1}'.format(property_group_id, property_id)
    if key in product_filter["select-filter"].keys():
        filter_dict = product_filter["select-filter"][key]
        options = filter_dict['value'].split("|")
        if value in options:
            options.remove(value)
        else:
            options.append(value)

        if options:
            product_filter["select-filter"][key]['value'] = "|".join(options)
        else:
            del product_filter["select-filter"][key]
    else:
        product_filter["select-filter"][key] = {'value': value,
                                                'property_id': property_id,
                                                'property_group_id': property_group_id}

    if not product_filter.get("select-filter"):
        del product_filter["select-filter"]

    request.session["product-filter"] = product_filter

    url = reverse("lfs_category", kwargs={"slug": category_slug})
    return HttpResponseRedirect(url)


def set_price_filter(request, category_slug):
    """Saves the given price filter to session. Redirects to the category with
    given slug.
    """
    req = request.POST if request.method == 'POST' else request.GET
    try:
        min_val = lfs.core.utils.atof(req.get("min", "0"))
    except (ValueError):
        min_val = 0

    try:
        max_val = lfs.core.utils.atof(req.get("max", "99999"))
    except:
        max_val = 0

    try:
        float(min_val)
    except (TypeError, ValueError):
        min_val = "0"

    try:
        float(max_val)
    except (TypeError, ValueError):
        max_val = "0"

    request.session["price-filter"] = {"min": min_val, "max": max_val}

    url = reverse("lfs_category", kwargs={"slug": category_slug})
    return HttpResponseRedirect(url)


def set_manufacturer_filter(request, category_slug, manufacturer_id):
    """ Saves the given manufacturer filter to session. Redirects to the category with given slug.
    """
    try:
        manufacturer_id = int(manufacturer_id)
        if Manufacturer.objects.filter(pk=manufacturer_id).exists():
            mf = request.session.get("manufacturer-filter", [])
            if manufacturer_id not in mf:
                mf.append(manufacturer_id)
            request.session["manufacturer-filter"] = mf
    except (ValueError, TypeError):
        pass

    url = reverse("lfs_category", kwargs={"slug": category_slug})
    return HttpResponseRedirect(url)


def reset_price_filter(request, category_slug):
    """Resets the price filter. Redirects to the category with given slug.
    """
    if "price-filter" in request.session:
        del request.session["price-filter"]

    url = reverse("lfs_category", kwargs={"slug": category_slug})
    return HttpResponseRedirect(url)


def reset_filter(request, category_slug, property_group_id, property_id):
    """Resets product filter with given property id. Redirects to the category
    with given slug.
    """
    if "product-filter" in request.session:
        key = '{0}_{1}'.format(property_group_id, property_id)
        select_filter = request.session["product-filter"].get('select-filter', {})
        if key in select_filter:
            del select_filter[key]
            request.session["product-filter"] = request.session["product-filter"]

    url = reverse("lfs_category", kwargs={"slug": category_slug})
    return HttpResponseRedirect(url)


def reset_manufacturer_filter(request, category_slug, manufacturer_id):
    if "manufacturer-filter" in request.session:
        if int(manufacturer_id) in request.session["manufacturer-filter"]:
            request.session["manufacturer-filter"].remove(int(manufacturer_id))
            request.session["manufacturer-filter"] = request.session["manufacturer-filter"]

    url = reverse("lfs_category", kwargs={"slug": category_slug})
    return HttpResponseRedirect(url)


def reset_all_manufacturer_filter(request, category_slug):
    if "manufacturer-filter" in request.session:
        del request.session["manufacturer-filter"]

    url = reverse("lfs_category", kwargs={"slug": category_slug})
    return HttpResponseRedirect(url)


def reset_number_filter(request, category_slug, property_group_id, property_id):
    """Resets product filter with given property id. Redirects to the category
    with given slug.
    """
    key = '{0}_{1}'.format(property_group_id, property_id)
    try:
        product_filter = request.session.get("product-filter")
        del product_filter["number-filter"][key]
    except KeyError:
        pass
    else:
        if product_filter["number-filter"] == {}:
            del product_filter["number-filter"]

    request.session["product-filter"] = product_filter

    url = reverse("lfs_category", kwargs={"slug": category_slug})
    return HttpResponseRedirect(url)


def reset_all_filter(request, category_slug):
    """Resets all product filter. Redirects to the category with given slug.
    """
    if "product-filter" in request.session:
        del request.session["product-filter"]

    if "price-filter" in request.session:
        del request.session["price-filter"]

    if "manufacturer-filter" in request.session:
        del request.session["manufacturer-filter"]

    url = reverse("lfs_category", kwargs={"slug": category_slug})
    return HttpResponseRedirect(url)


@csrf_exempt
def set_sorting(request):
    """Saves the given sortings (by request body) to session.
    """
    sorting = request.POST.get("sorting", "")
    if sorting == "" and "sorting" in request.session:
        del request.session["sorting"]
    else:
        request.session["sorting"] = sorting

    # lfs_sorting_changed.send(category_id)
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", '/'))


def category_view(request, slug, template_name="lfs/catalog/category_base.html"):
    """
    """
    start = (request.POST if request.method == 'POST' else request.GET).get("start", 1)
    category = lfs_get_object_or_404(Category, slug=slug)
    if category.get_content() == CONTENT_PRODUCTS:
        inline_dict = category_products(request, slug, start)
    else:
        inline_dict = category_categories(request, slug)

    inline = inline_dict['html']
    pagination_data = inline_dict['pagination_data']
    # Set last visited category for later use, e.g. Display breadcrumbs,
    # selected menu points, etc.
    request.session["last_category"] = category
    if "last_manufacturer" in request.session:
        del(request.session["last_manufacturer"])

    # TODO: Factor top_category out to a inclusion tag, so that people can
    # omit if they don't need it.

    return render(request, template_name, {
        "category": category,
        "category_inline": inline,
        "top_category": lfs.catalog.utils.get_current_top_category(request, category),
        "pagination": (request.POST if request.method == 'POST' else request.GET).get("start", 0),
        'pagination_data': pagination_data
    })


def category_categories(request, slug, start=0, template_name="lfs/catalog/categories/category/default.html"):
    """Displays the child categories of the category with passed slug.

    This view is called if the user chooses a template that is situated in settings.CATEGORY_PATH ".
    """
    cache_key = "%s-category-categories-2-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, slug)

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

    if render_template is not None:
        template_name = render_template

    result_html = render_to_string(template_name, request=request, context={
        "category": category,
        "categories": categories,
    })

    result = {'pagination_data': {'current_page': 1, 'total_pages': 1, 'getparam': 'start'}, 'html': result_html}

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
        if "manufacturer-filter" in request.session:
            del request.session["manufacturer-filter"]

    try:
        default_sorting = settings.LFS_PRODUCTS_SORTING
    except AttributeError:
        default_sorting = "effective_price"
    sorting = request.session.get("sorting", default_sorting)

    product_filter = request.session.get("product-filter", {})

    cache_key = "%s-category-products-2-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, slug)
    sub_cache_key = "%s-2-start-%s-sorting-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, start, sorting)

    filter_key = ["%s-%s" % (i[0], i[1]) for i in product_filter.items()]
    if filter_key:
        sub_cache_key += "-%s" % "-".join(filter_key)

    price_filter = request.session.get("price-filter")
    if price_filter:
        sub_cache_key += "-%s-%s" % (price_filter["min"], price_filter["max"])

    manufacturer_filter = request.session.get("manufacturer-filter")
    if manufacturer_filter:
        sub_cache_key += "-%s" % ','.join(map(str, manufacturer_filter))

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
        category, product_filter, price_filter, sorting, manufacturer_filter)
    all_products = all_products.select_related('parent')

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
            "price_unit": product.get_price_unit(),
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

    pagination_data['total_text'] = ungettext('%(count)d product',
                                              '%(count)d products',
                                              amount_of_products) % {'count': amount_of_products}

    render_template = category.get_template_name()
    if render_template is not None:
        template_name = render_template

    template_data = {
        "category": category,
        "products": products,
        "amount_of_products": amount_of_products,
        "pagination": pagination_data
    }

    result_html = render_to_string(template_name, request=request, context=template_data)

    result = {'pagination_data': pagination_data, 'html': result_html}

    temp[sub_cache_key] = result
    cache.set(cache_key, temp)

    return result


def product_view(request, slug, template_name="lfs/catalog/product_base.html"):
    """Main view to display a product.
    """
    product = lfs_get_object_or_404(Product, slug=slug)

    if (request.user.is_superuser or product.is_active()) is False:
        raise Http404()

    # Store recent products for later use
    recent = request.session.get("RECENT_PRODUCTS", [])
    if slug in recent:
        recent.remove(slug)
    recent.insert(0, slug)
    if len(recent) > settings.LFS_RECENT_PRODUCTS_LIMIT:
        recent = recent[:settings.LFS_RECENT_PRODUCTS_LIMIT + 1]
    request.session["RECENT_PRODUCTS"] = recent

    if product.is_variant():
        variant_canonical = product.parent.get_variant_for_category(request)
    else:
        variant_canonical = product

    result = render(request, template_name, {
        "product_inline": product_inline(request, product),
        "variant_canonical": variant_canonical,
        "product": product,
    })

    return result


def product_inline(request, product, template_name="lfs/catalog/products/product_inline.html"):
    """
    Part of the product view, which displays the actual data of the product.

    This is factored out to be able to better cached and in might in future used
    used to be updated via ajax requests.
    """
    pid = product.get_parent().pk
    properties_version = get_cache_group_id('global-properties-version')
    group_id = '%s-%s' % (properties_version, get_cache_group_id('properties-%s' % pid))
    cache_key = "%s-%s-product-inline-%s-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, group_id,
                                                request.user.is_superuser, product.id)
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
        properties = parent.get_all_properties(variant=product)

        if parent.variants_display_type != SELECT:
            variants = parent.get_variants()
        else:
            display_variants_list = False

    elif product.is_configurable_product():
        for property_dict in product.get_configurable_properties():
            property_group = property_dict['property_group']
            prop = property_dict['property']
            options = []
            try:
                ppv = ProductPropertyValue.objects.get(product=product, property_group=property_group,
                                                       property=prop, type=PROPERTY_VALUE_TYPE_DEFAULT)
                ppv_value = ppv.value
            except ProductPropertyValue.DoesNotExist:
                ppv = None
                ppv_value = ""

            for property_option in prop.options.all():
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
                "obj": prop,
                "id": prop.id,
                "name": prop.name,
                "title": prop.title,
                "unit": prop.unit,
                "display_price": prop.display_price,
                "options": options,
                "value": ppv_value,
                "property_group": property_group,
                "property_group_id": property_group.id if property_group else 0
            })

    if product.get_template_name() is not None:
        template_name = product.get_template_name()

    if product.get_active_packing_unit():
        packing_result = calculate_packing(request, product.id, 1, True, True)
    else:
        packing_result = ""

    # attachments
    attachments = product.get_attachments()

    result = render_to_string(template_name, request=request, context={
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
        "for_sale": product.get_for_sale(),
    })

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
    if (request.POST if request.method == 'POST' else request.GET).get("add-to-cart") is not None:
        return add_to_cart(request)
    else:
        product_id = request.POST.get("product_id")
        product = lfs_get_object_or_404(Product, pk=product_id)

        options = lfs.utils.misc.parse_properties(request)
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
                property_group_id, property_id = map(int, key.split('-')[1:])
                prop = Property.objects.get(pk=property_id)
                if prop.is_select_field:
                    po = PropertyOption.objects.get(property=property, pk=option_id)
                    if prop.add_price:
                        po_price = float(po.price)
                        property_price += po_price
            except (IndexError, ValueError, TypeError, PropertyOption.DoesNotExist, Property.DoesNotExist):
                pass
    return property_price
