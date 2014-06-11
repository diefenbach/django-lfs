# python imports
import math

# django imports
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.core.exceptions import FieldError
from django.db.models import Q, Count, Min, Max

# import lfs
import lfs.catalog.models
from lfs.catalog.settings import CONFIGURABLE_PRODUCT
from lfs.catalog.settings import STANDARD_PRODUCT
from lfs.catalog.settings import PRODUCT_WITH_VARIANTS
from lfs.catalog.settings import PROPERTY_VALUE_TYPE_FILTER

# Load logger
import logging
from lfs.manufacturer.models import Manufacturer

logger = logging.getLogger("default")


# TODO: Add unit test
def get_current_top_category(request, obj):
    """
    Returns the current top category of a product.
    """
    if obj.__class__.__name__.lower() == "product":
        category = obj.get_current_category(request)
    else:
        category = obj

    if category is None:
        return category

    while category.parent is not None:
        category = category.parent

    return category


def get_price_filters(category, product_filter, price_filter, manufacturer_filter):
    """Creates price filter links based on the min and max price of the
    categorie's products.
    """
    # Base are the filtered products
    products = get_filtered_products_for_category(category, product_filter, price_filter, None, manufacturer_filter)
    if not products:
        return []

    # And their variants
    # product_ids = []
    # for product in products:
    #     if product.is_product_with_variants():
    #         product_ids.extend(product.variants.filter(active=True).values_list('id', flat=True))
    #     else:
    #         product_ids.append(product.pk)
    #product_ids = lfs.catalog.models.Product.objects.filter(Q(pk__in=products) | Q(parent__in=products)).values_list('id', flat=True)

    #product_ids_str = ", ".join(map(str, product_ids))

    # If a price filter is set we return just this.
    if price_filter:
        pmin = price_filter["min"]
        pmax = price_filter["max"]
        # products = lfs.catalog.models.Product.objects.filter(effective_price__range=(pmin, pmax), pk__in=product_ids)

        return {
            "show_reset": True,
            "show_quantity": False,
            "items": [{"min": float(pmin), "max": float(pmax)}],
        }

    #cursor = connection.cursor()
    #cursor.execute("""SELECT min(effective_price), max(effective_price)
    #                  FROM catalog_product
    #                  WHERE id IN (%s)""" % product_ids_str)

    all_products = lfs.catalog.models.Product.objects.filter(Q(pk__in=products) | (Q(parent__in=products) & Q(active=True)))
    res = all_products.aggregate(min_price=Min('effective_price'), max_price=Max('effective_price'))

    pmin, pmax = res['min_price'] or 0, res['max_price'] or 0
    if pmax == pmin:
        step = pmax
    else:
        diff = pmax - pmin
        step = diff / 3

    if step >= 0 and step < 3:
        step = 3
    elif step >= 3 and step < 6:
        step = 5
    elif step >= 6 and step < 11:
        step = 10
    elif step >= 11 and step < 51:
        step = 50
    elif step >= 51 and step < 101:
        step = 100
    elif step >= 101 and step < 501:
        step = 500
    elif step >= 501 and step < 1001:
        step = 1000
    elif step >= 1000 and step < 5001:
        step = 500
    elif step >= 5001 and step < 10001:
        step = 1000

    result = []
    for n, i in enumerate(range(0, int(pmax), step)):
        if i > pmax:
            break
        pmin = i + 1
        pmax = i + step
        result.append({
            "min": pmin,
            "max": pmax,
            "quantity": all_products.filter(effective_price__range=(pmin, pmax)).count(),
        })

    # return result
    new_result = []
    for n, f in enumerate(result):
        if f["quantity"] == 0:
            try:
                result[n + 1]["min"] = f["min"]
            except IndexError:
                pass
            continue
        new_result.append(f)

    return {
        "show_reset": False,
        "show_quantity": True,
        "items": new_result,
    }


def get_manufacturer_filters(category, product_filter, price_filter, manufacturer_filter):
    """Creates manufacturer filter links based on the manufacturers bound to the products in category
    """
    # Base are the filtered products
    products = get_filtered_products_for_category(category, product_filter, price_filter, None, None)
    if not products:
        return []

    all_products = lfs.catalog.models.Product.objects.filter(Q(pk__in=products) | (Q(parent__in=products) & Q(active=True)))

    # And their parents
    # product_ids = []
    # for product in products:
    #     if product.parent:
    #         product_ids.append(product.parent_id)
    #     else:
    #         product_ids.append(product.pk)

    out = {"show_reset": False}
    if manufacturer_filter:
        out = {
            "show_reset": True
        }
    else:
        manufacturer_filter = []

    qs = Manufacturer.objects.filter(products__in=all_products).annotate(products_count=Count('products'))
    out['items'] = [{'obj': obj, 'selected': obj.pk in manufacturer_filter} for obj in qs]
    return out


def get_product_filters(category, product_filter, price_filter, manufacturer_filter, sorting):
    """Returns the next product filters based on products which are in the given
    category and within the result set of the current filters.
    """
    if price_filter:
        ck_price_filter = "%s|%s" % (price_filter["min"], price_filter["max"])
    else:
        ck_price_filter = ""

    if product_filter:
        ck_product_filter = ""
        for pf in product_filter:
            ck_product_filter += pf[0] + "|"
            ck_product_filter += "|".join(pf[1])
    else:
        ck_product_filter = ""

    cache_key = "%s-productfilters-%s-%s-%s-%s-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX,
        category.slug, ck_product_filter, ck_price_filter, sorting, manufacturer_filter)

    result = cache.get(cache_key)
    if result is not None:
        return result

    properties_mapping = get_property_mapping()
    options_mapping = get_option_mapping()

    # The base for the calulation of the next filters are the filtered products
    products = get_filtered_products_for_category(
        category, product_filter, price_filter, sorting, manufacturer_filter)
    if not products:
        return []

    # ... and their variants
    # product_ids = []
    # for product in products:
    #     product_ids.append(product.pk)
    #     product_ids.extend(product.variants.filter(active=True).values_list('id', flat=True))
    all_products = lfs.catalog.models.Product.objects.filter(Q(pk__in=products) | (Q(parent__in=products) & Q(active=True)))
    product_ids = all_products.values_list('id', flat=True)

    # Get the ids for use within the customer SQL
    product_ids_str = ", ".join(map(str, product_ids))

    # Create dict out of already set filters
    set_filters = dict(product_filter)

    property_ids = lfs.catalog.models.ProductPropertyValue.objects.distinct().values_list('property_id', flat=True)
    property_ids_str = ", ".join(map(str, property_ids))

    # if there is either no products or no property ids there can also be no
    # product filters.
    if not product_ids or not property_ids:
        return []

    result = []
    ########## Number Fields ###################################################

    cursor = connection.cursor()
    cursor.execute("""SELECT property_id, min(value_as_float), max(value_as_float)
                      FROM catalog_productpropertyvalue
                      WHERE type=%s
                      AND product_id IN (%s)
                      AND property_id IN (%s)
                      GROUP BY property_id""" % (PROPERTY_VALUE_TYPE_FILTER, product_ids_str, property_ids_str))

    for row in cursor.fetchall():
        prop = properties_mapping[row[0]]

        if not prop.is_number_field or not prop.filterable:
            continue

        # If the filter for a property is already set, we display only the
        # set filter.
        if str(row[0]) in set_filters.keys():
            values = set_filters[str(row[0])]
            result.append({
                "id": row[0],
                "position": prop.position,
                "object": prop,
                "name": prop.name,
                "title": prop.title,
                "unit": prop.unit,
                "items": [{"min": float(values[0]), "max": float(values[1])}],
                "show_reset": True,
                "show_quantity": False,
            })
            continue

        # Otherwise we display all steps.
        items = _calculate_steps(product_ids_str, prop, row[1], row[2])

        result.append({
            "id": row[0],
            "position": prop.position,
            "object": prop,
            "name": prop.name,
            "title": prop.title,
            "unit": prop.unit,
            "show_reset": False,
            "show_quantity": True,
            "items": items,
        })

    ########## Select Fields ###################################################
    # Count entries for current filter
    cursor = connection.cursor()
    cursor.execute("""SELECT property_id, value, parent_id
                      FROM catalog_productpropertyvalue
                      WHERE type=%s
                      AND product_id IN (%s)
                      AND property_id IN (%s)""" % (PROPERTY_VALUE_TYPE_FILTER, product_ids_str, property_ids_str))

    already_count = {}
    amount = {}
    for row in cursor.fetchall():
        # We count a property/value pair just one time per *product*. For
        # "products with variants" this could be stored several times within the
        # catalog_productpropertyvalue. Imagine a variant with two properties
        # color and size:
        #   v1 = color:red / size: s
        #   v2 = color:red / size: l
        # But we want to count color:red just one time. As the product with
        # variants is displayed at not the variants.

        if "%s%s%s" % (row[2], row[0], row[1]) in already_count:
            continue
        already_count["%s%s%s" % (row[2], row[0], row[1])] = 1

        if row[0] not in amount:
            amount[row[0]] = {}

        if row[1] not in amount[row[0]]:
            amount[row[0]][row[1]] = 0

        amount[row[0]][row[1]] += 1

    cursor.execute("""SELECT property_id, value
                      FROM catalog_productpropertyvalue
                      WHERE product_id IN (%s)
                      AND property_id IN (%s)
                      AND type=%s
                      GROUP BY property_id, value""" % (product_ids_str, property_ids_str, PROPERTY_VALUE_TYPE_FILTER))

    # Group properties and values (for displaying)
    set_filters = dict(product_filter)
    properties = {}
    for row in cursor.fetchall():
        prop = properties_mapping[row[0]]

        if prop.is_number_field or not prop.filterable or not row[1]:
            continue

        if row[0] in properties == False:
            properties[row[0]] = []

        # If the property is a select field we want to display the name of the
        # option instead of the id.
        position = 1
        if prop.is_select_field:
            try:
                name = options_mapping[row[1]].name
                position = options_mapping[row[1]].position
            except KeyError:
                name = row[1]
        else:
            name = row[1]

        value = row[1]

        # if the property within the set filters we just show the selected value
        if str(row[0]) in set_filters.keys():
            if str(row[1]) in set_filters.values():
                properties[row[0]] = [{
                    "id": row[0],
                    "value": value,
                    "name": name,
                    "position": position,
                    "quantity": amount[row[0]][row[1]],
                    "show_quantity": False,
                }]
            continue
        else:
            if not row[0] in properties:
                properties[row[0]] = []
            properties[row[0]].append({
                "id": row[0],
                "value": value,
                "name": name,
                "position": position,
                "quantity": amount[row[0]][row[1]],
                "show_quantity": True,
            })

    # Transform the group properties into a list of dicts
    set_filter_keys = set_filters.keys()

    for property_id, values in properties.items():
        prop = properties_mapping[property_id]

        # Sort the values. NOTE: This has to be done here (and not via SQL) as
        # the value field of the property is a char field and can't ordered
        # properly for numbers.
        values.sort(lambda a, b: cmp(a["position"], b["position"]))

        result.append({
            "id": property_id,
            "position": prop.position,
            "unit": prop.unit,
            "show_reset": str(property_id) in set_filter_keys,
            "name": prop.name,
            "title": prop.title,
            "items": values,
        })

    result.sort(lambda a, b: cmp(a["position"], b["position"]))
    cache.set(cache_key, result)

    return result


# TODO: Implement this as a method of Category
def get_filtered_products_for_category(category, filters, price_filter, sorting, manufacturers_filter=None):
    """Returns products for given categories and current filters sorted by
    current sorting.
    """
    from lfs.catalog.models import Product, ProductPropertyValue
    if filters:
        if category.show_all_products:
            products = category.get_all_products()
        else:
            products = category.get_products()

        # All variants of category products
        all_variants = Product.objects.filter(parent__in=products)

        # Generate filter
        filters_query = None
        for f in filters:
            if not isinstance(f[1], (list, tuple)):
                q = Q(property_id=f[0], value=f[1])
            else:
                q = Q(property_id=f[0], value_as_float__range=(f[1][0], f[1][1]))
            if filters_query is None:
                filters_query = q
            else:
                filters_query |= q

        # The idea behind SQL query generated below is: If for every filter (property=value) for a product id exists
        # a "product property value" the product matches.
        #
        # Example ValuesListQuerySet built by statements below is:
        #
        # ProductPropertyValue.objects.filter(Q(property_id=1, value='1') | Q(property_id=2, value='1'),
        #                                     product__in=products,
        #                                     type=PROPERTY_VALUE_TYPE_FILTER) \
        #                             .values('product_id') \
        #                             .annotate(cnt=Count('id')).filter(cnt=2).values_list('product_id', flat=True)
        #
        # it evaluates to:
        #
        # SELECT "catalog_productpropertyvalue"."product_id"
        #   FROM "catalog_productpropertyvalue"
        #  WHERE ((
        #          ("catalog_productpropertyvalue"."value" = 1  AND "catalog_productpropertyvalue"."property_id" = 1 )
        #          OR
        #          ("catalog_productpropertyvalue"."value" = 1  AND "catalog_productpropertyvalue"."property_id" = 2 )
        #        )
        #    AND "catalog_productpropertyvalue"."type" = 0
        #    AND "catalog_productpropertyvalue"."product_id" IN (SELECT U0."id"
        #                                                          FROM "catalog_product" U0
        #                                                         WHERE U0."name" LIKE %da% ESCAPE '\' ))
        #  GROUP BY "catalog_productpropertyvalue"."product_id"
        # HAVING COUNT("catalog_productpropertyvalue"."id") = 2

        # PRODUCTS - get all products with matching filters.
        matching_product_ids = ProductPropertyValue.objects.filter(product__in=products,
                                                                   type=PROPERTY_VALUE_TYPE_FILTER)
        if filters_query is not None:
            matching_product_ids = matching_product_ids.filter(filters_query)
        matching_product_ids = matching_product_ids.values('product_id').annotate(cnt=Count('id')) \
                                                   .filter(cnt=len(filters)).values_list('product_id', flat=True)

        # VARIANTS - get matching variants and then their parents as we're interested in products with variants,
        # not variants itself
        matching_variant_ids = ProductPropertyValue.objects.filter(product__in=all_variants,
                                                                   type=PROPERTY_VALUE_TYPE_FILTER)
        if filters_query is not None:
            matching_variant_ids = matching_variant_ids.filter(filters_query)
        matching_variant_ids = matching_variant_ids.values('product_id').annotate(cnt=Count('id')) \
                                                   .filter(cnt=len(filters)).values_list('product_id', flat=True)
        variant_products = Product.objects.filter(pk__in=matching_variant_ids)

        # Merge results
        products = Product.objects.filter(Q(pk__in=matching_product_ids) |
                                          Q(pk__in=variant_products.values_list('parent_id', flat=True))).distinct()
    else:
        categories = [category]
        if category.show_all_products:
            categories.extend(category.get_all_children())
        products = lfs.catalog.models.Product.objects.filter(
            active=True,
            categories__in=categories,
            sub_type__in=[STANDARD_PRODUCT, PRODUCT_WITH_VARIANTS, CONFIGURABLE_PRODUCT]).distinct()

    # TODO: It might be more effective to move price filters directly into if/else clause above
    if price_filter:
        # Get all variants of the products
        variants = lfs.catalog.models.Product.objects.filter(parent__in=products)
        # Filter the variants by price
        variants = variants.filter(effective_price__range=[price_filter["min"],
                                                           price_filter["max"]])
        # Filter the products
        filtered_products = products.filter(effective_price__range=[price_filter["min"],
                                                                    price_filter["max"]])
        # merge the result and get a new query set of all products
        # We get the parent ids of the variants as the "product with variants"
        # should be displayed and not the variants.
        products = lfs.catalog.models.Product.objects.filter(
            Q(pk__in=filtered_products) | Q(pk__in=variants.values_list('parent_id', flat=True)))

    if manufacturers_filter:
        # Get all variants of the products
        variants = lfs.catalog.models.Product.objects.filter(parent__in=products)
        # Filter the variants by manufacturer
        variants = variants.filter(manufacturer__in=manufacturers_filter)
        # Filter the products
        filtered_products = products.filter(manufacturer__in=manufacturers_filter)

        # merge the result and get a new query set of all products
        # We get the parent ids of the variants as the "product with variants"
        # should be displayed and not the variants.
        products = lfs.catalog.models.Product.objects.filter(
            Q(pk__in=filtered_products) | Q(pk__in=variants.values_list('parent_id', flat=True)))

    if sorting:
        try:
            products = products.order_by(sorting)
        except FieldError:
            # ignore invalid sort order which may be stored in the session
            pass

    return products


def get_option_mapping():
    """Returns a dictionary with option id to property name.
    """
    options = {}
    for option in lfs.catalog.models.PropertyOption.objects.all():
        options[str(option.id)] = option
    return options


def get_property_mapping():
    """Returns a dictionary with property id to property name.
    """
    properties = {}
    for property in lfs.catalog.models.Property.objects.all():
        properties[property.id] = property

    return properties


def _calculate_steps(product_ids, property, min, max):
    """Calculates filter steps.

    **Parameters**

    product_ids
        The product_ids for which the steps are calculated. List of ids.

    property
        The property for which the steps are calculated. Instance of Property.

    min / max
        The min and max value of all steps. Must be a Float.

    """
    try:
        min = float(min)
        max = float(max)
    except TypeError:
        return []

    result = []

    filter_steps = lfs.catalog.models.FilterStep.objects.filter(property=property.id)
    if property.is_steps_step_type:
        for i, step in enumerate(filter_steps[:len(filter_steps) - 1]):
            min = step.start
            if i != 0:
                min += 1.0
            max = filter_steps[i + 1].start

            result.append({
                "min": min,
                "max": max,
                "quantity": _calculate_quantity(product_ids, property.id, min, max)
            })
    else:
        if property.is_automatic_step_type:
            if max == min:
                step = max
            else:
                diff = max - min
                step = diff / 3         # TODO: Should this be variable?

            if step >= 0 and step < 2:
                step = 1
            elif step >= 2 and step < 6:
                step = 5
            elif step >= 6 and step < 11:
                step = 10
            elif step >= 11 and step < 51:
                step = 50
            elif step >= 51 and step < 101:
                step = 100
            elif step >= 101 and step < 501:
                step = 500
            elif step >= 501 and step < 1001:
                step = 1000
            elif step >= 1000 and step < 5001:
                step = 500
            elif step >= 5001 and step < 10001:
                step = 1000
        else:
            step = property.step

        for n, i in enumerate(range(0, int(max), step)):
            if i > max:
                break
            min = i + 1
            max = i + step

            result.append({
                "min": min,
                "max": max,
                "quantity": _calculate_quantity(product_ids, property.id, min, max),
            })

    if property.display_no_results:
        return result
    else:
        # Remove entries with zero products
        new_result = []
        for n, f in enumerate(result):
            if f["quantity"] == 0:
                try:
                    result[n + 1]["min"] = f["min"]
                except IndexError:
                    pass
                continue
            new_result.append(f)

        return new_result


def _calculate_quantity(product_ids, property_id, min, max):
    """Calculate the amount of products for given parameters.
    """
    # Count entries for current filter
    cursor = connection.cursor()
    cursor.execute("""SELECT property_id, value, parent_id
                      FROM catalog_productpropertyvalue
                      WHERE product_id IN (%s)
                      AND property_id = %s
                      AND value_as_float BETWEEN %s AND %s""" % (product_ids, property_id, min, max))

    already_count = {}
    amount = 0
    for row in cursor.fetchall():
        # We count a property/value pair just one time per *product*. For
        # "products with variants" this could be stored several times within the
        # catalog_productpropertyvalue. Imagine a variant with two properties
        # color and size:
        #   v1 = color:red / size: s
        #   v2 = color:red / size: l
        # But we want to count color:red just one time. As the product with
        # variants is displayed at not the variants.

        if "%s%s%s" % (row[2], row[0], row[1]) in already_count:
            continue
        already_count["%s%s%s" % (row[2], row[0], row[1])] = 1

        amount += 1

    return amount
