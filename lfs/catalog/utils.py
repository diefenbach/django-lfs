# python imports
import math

# django imports
from django.conf import settings
from django.core.cache import cache
from django.db import connection

# import lfs
import lfs.catalog.models
from lfs.catalog.settings import CONFIGURABLE_PRODUCT
from lfs.catalog.settings import STANDARD_PRODUCT
from lfs.catalog.settings import PRODUCT_WITH_VARIANTS
from lfs.catalog.settings import PROPERTY_VALUE_TYPE_FILTER

# Load logger
import logging
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


def get_current_product_category(request, product):
    """Returns product category based on actual categories of the given product
    and the last visited category.

    This is needed if the category has more than one category to display
    breadcrumbs, selected menu points, etc. appropriately.
    """
    logger.info("Decprecated: lfs.catalog.utils: the function 'get_current_product_category' is deprecated. Please use 'get_current_category'of the Product class.")
    return product.get_current_category(request)


def get_property_groups(category):
    """Returns all property groups for given category
    """
    logger.info("Decprecated: lfs.catalog.utils: the function 'get_property_groups' is deprecated. Please use 'get_property_groups'of the Category class.")
    return category.get_property_groups()


def get_price_filters(category, product_filter, price_filter):
    """Creates price filter links based on the min and max price of the
    categorie's products.
    """
    # Base are the filtered products
    products = get_filtered_products_for_category(category, product_filter, price_filter, None)
    if not products:
        return []

    # And their variants
    all_products = []
    for product in products:
        all_products.extend(product.variants.filter(active=True))
        if product.is_product_with_variants():
            all_products.extend(product.variants.filter(active=True))
        else:
            all_products.append(product)

    product_ids = [p.id for p in all_products]

    # If a price filter is set we return just this.
    if price_filter:
        min = price_filter["min"]
        max = price_filter["max"]
        products = lfs.catalog.models.Product.objects.filter(
            effective_price__range=(min, max), pk__in=product_ids)

        return {
            "show_reset": True,
            "show_quantity": False,
            "items": [{"min": float(min), "max": float(max)}],
            }

    product_ids_str = ", ".join([str(p.id) for p in all_products])
    cursor = connection.cursor()
    cursor.execute("""SELECT min(effective_price), max(effective_price)
                      FROM catalog_product
                      WHERE id IN (%s)""" % product_ids_str)

    pmin, pmax = cursor.fetchall()[0]
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
        min = i + 1
        max = i + step
        products = lfs.catalog.models.Product.objects.filter(effective_price__range=(min, max), pk__in=product_ids)
        result.append({
            "min": min,
            "max": max,
            "quantity": len(products),
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


def get_product_filters(category, product_filter, price_filter, sorting):
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

    cache_key = "%s-productfilters-%s-%s-%s-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX,
        category.slug, ck_product_filter, ck_price_filter, sorting)

    result = cache.get(cache_key)
    if result is not None:
        return result

    properties_mapping = get_property_mapping()
    options_mapping = get_option_mapping()

    # The base for the calulation of the next filters are the filtered products
    products = get_filtered_products_for_category(
        category, product_filter, price_filter, sorting)
    if not products:
        return []

    # ... and their variants
    all_products = []
    for product in products:
        all_products.append(product)
        all_products.extend(product.variants.filter(active=True))

    # Get the ids for use within the customer SQL
    product_ids = ", ".join([str(p.id) for p in all_products])

    # Create dict out of already set filters
    set_filters = dict(product_filter)

    cursor = connection.cursor()
    cursor.execute("""SELECT DISTINCT property_id
                      FROM catalog_productpropertyvalue""")

    property_ids = ", ".join([str(p[0]) for p in cursor.fetchall()])

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
                      GROUP BY property_id""" % (PROPERTY_VALUE_TYPE_FILTER, product_ids, property_ids))

    for row in cursor.fetchall():

        property = properties_mapping[row[0]]

        if property.is_number_field == False:
            continue

        if property.filterable == False:
            continue

        # If the filter for a property is already set, we display only the
        # set filter.
        if str(row[0]) in set_filters.keys():
            values = set_filters[str(row[0])]
            result.append({
                "id": row[0],
                "position": property.position,
                "object": property,
                "name": property.name,
                "title": property.title,
                "unit": property.unit,
                "items": [{"min": float(values[0]), "max": float(values[1])}],
                "show_reset": True,
                "show_quantity": False,
            })
            continue

        # Otherwise we display all steps.
        items = _calculate_steps(product_ids, property, row[1], row[2])

        result.append({
            "id": row[0],
            "position": property.position,
            "object": property,
            "name": property.name,
            "title": property.title,
            "unit": property.unit,
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
                      AND property_id IN (%s)""" % (PROPERTY_VALUE_TYPE_FILTER, product_ids, property_ids))

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
                      GROUP BY property_id, value""" % (product_ids, property_ids, PROPERTY_VALUE_TYPE_FILTER))

    # Group properties and values (for displaying)
    set_filters = dict(product_filter)
    properties = {}
    for row in cursor.fetchall():

        property = properties_mapping[row[0]]

        if property.is_number_field:
            continue

        if property.filterable == False:
            continue

        if row[0] in properties == False:
            properties[row[0]] = []

        # If the property is a select field we want to display the name of the
        # option instead of the id.
        if property.is_select_field:
            try:
                name = options_mapping[row[1]].name
            except KeyError:
                name = row[1]
        elif property.is_number_field:
            value = float(row[1])
        else:
            name = row[1]

        # Transform to float for later sorting, see below
        if property.is_number_field:
            value = float(row[1])
        else:
            value = row[1]

        # if the property within the set filters we just show the selected value
        if str(row[0]) in set_filters.keys():
            if str(row[1]) in set_filters.values():
                properties[row[0]] = [{
                    "id": row[0],
                    "value": value,
                    "name": name,
                    "quantity": amount[row[0]][row[1]],
                    "show_quantity": False,
                }]
            continue
        else:
            if not properties.has_key(row[0]):
                properties[row[0]] = []
            properties[row[0]].append({
                "id": row[0],
                "value": value,
                "name": name,
                "quantity": amount[row[0]][row[1]],
                "show_quantity": True,
            })

    # Transform the group properties into a list of dicts
    set_filter_keys = set_filters.keys()

    for property_id, values in properties.items():

        property = properties_mapping[property_id]

        # Sort the values. NOTE: This has to be done here (and not via SQL) as
        # the value field of the property is a char field and can't ordered
        # properly for numbers.
        values.sort(lambda a, b: cmp(a["value"], b["value"]))

        result.append({
            "id": property_id,
            "position": property.position,
            "unit": property.unit,
            "show_reset": str(property_id) in set_filter_keys,
            "name": property.name,
            "title": property.title,
            "items": values,
        })

    result.sort(lambda a, b: cmp(a["position"], b["position"]))
    cache.set(cache_key, result)

    return result


# TODO: Implement this as a method of Category
def get_filtered_products_for_category(category, filters, price_filter, sorting):
    """Returns products for given categories and current filters sorted by
    current sorting.
    """
    if filters:
        if category.show_all_products:
            products = category.get_all_products()
        else:
            products = category.get_products()

        # Generate ids for collected products
        product_ids = [str(p.id) for p in products]
        product_ids = ", ".join(product_ids)

        # Generate filter
        temp = []
        for f in filters:
            if not isinstance(f[1], (list, tuple)):
                temp.append("property_id='%s' AND value='%s'" % (f[0], f[1]))
            else:
                temp.append("property_id='%s' AND value_as_float BETWEEN '%s' AND '%s'" % (f[0], f[1][0], f[1][1]))

        fstr = " OR ".join(temp)

        # TODO: Will this work with every DB?

        # Get all product ids with matching filters. The idea behind this SQL
        # query is: If for every filter (property=value) for a product id exists
        # a "product property value" the product matches.
        cursor = connection.cursor()
        cursor.execute("""
            SELECT product_id, count(*)
            FROM catalog_productpropertyvalue
            WHERE product_id IN (%s) and (%s) and type=%s
            GROUP BY product_id
            HAVING count(*)=%s""" % (product_ids, fstr, PROPERTY_VALUE_TYPE_FILTER, len(filters)))

        matched_product_ids = [row[0] for row in cursor.fetchall()]

        # All variants of category products
        all_variants = lfs.catalog.models.Product.objects.filter(parent__in=products)

        if all_variants:
            all_variant_ids = [str(p.id) for p in all_variants]
            all_variant_ids = ", ".join(all_variant_ids)

            # Variants with matching filters
            cursor.execute("""
                SELECT product_id, count(*)
                FROM catalog_productpropertyvalue
                WHERE product_id IN (%s) and %s and type=%s
                GROUP BY product_id
                HAVING count(*)=%s""" % (all_variant_ids, fstr, PROPERTY_VALUE_TYPE_FILTER, len(filters)))

            # Get the parent ids of the variants as the "product with variants"
            # should be displayed and not the variants.
            variant_ids = [str(row[0]) for row in cursor.fetchall()]
            if variant_ids:
                variant_ids = ", ".join(variant_ids)

                cursor.execute("""
                    SELECT parent_id
                    FROM catalog_product
                    WHERE id IN (%s)""" % variant_ids)

                parent_ids = [str(row[0]) for row in cursor.fetchall()]
                matched_product_ids.extend(parent_ids)

        # As we factored out the ids of all matching products now, we get the
        # product instances in the correct order
        products = lfs.catalog.models.Product.objects.filter(pk__in=matched_product_ids).distinct()
    else:
        categories = [category]
        if category.show_all_products:
            categories.extend(category.get_all_children())
        products = lfs.catalog.models.Product.objects.filter(
            active=True,
            categories__in=categories,
            sub_type__in=[STANDARD_PRODUCT, PRODUCT_WITH_VARIANTS, CONFIGURABLE_PRODUCT]).distinct()

    if price_filter:
        matched_product_ids = []

        # Get all variants of the products
        variants = lfs.catalog.models.Product.objects.filter(parent__in=products)

        # Filter the variants by price
        variants = variants.filter(effective_price__range=[price_filter["min"], price_filter["max"]])

        # Get the parent ids of the variants as the "product with variants"
        # should be displayed and not the variants.
        if variants:
            variant_ids = [str(r.id) for r in variants]
            variant_ids = ", ".join(variant_ids)

            cursor = connection.cursor()
            cursor.execute("""
                SELECT parent_id
                FROM catalog_product
                WHERE id IN (%s)""" % variant_ids)

            parent_ids = [str(row[0]) for row in cursor.fetchall()]
            matched_product_ids.extend(parent_ids)

        # Filter the products
        products = products.filter(effective_price__range=[price_filter["min"], price_filter["max"]])

        # Merge the results
        matched_product_ids.extend([p.id for p in products])

        # And get a new query set of all products
        products = lfs.catalog.models.Product.objects.filter(pk__in=matched_product_ids)

    if sorting:
        products = products.order_by(sorting)

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


def calculate_packages(product, quantity):
    """Returns amount of packages passed on passes product and quantity.
    DEPRECATED.
    """
    logger.info("Decprecated: lfs.catalog.utils: the function 'calculate_packages' is deprecated.")
    return math.ceil(quantity / product.packing_unit)


def calculate_real_amount(product, quantity):
    """Returns the amount of pieces in package units. DEPRECATED.
    """
    logger.info("Decprecated: lfs.catalog.utils: the function 'calculate_real_amount' is deprecated. Please use 'get_amount_by_packages'of the Product class.")
    return product.get_amount_by_packages(quantity)
