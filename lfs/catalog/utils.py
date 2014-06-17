# python imports
import locale
import math

# django imports
from django.db import connection
from django.core.exceptions import FieldError

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


# DEPRECATED 0.6
def get_current_product_category(request, product):
    """Returns product category based on actual categories of the given product
    and the last visited category.

    This is needed if the category has more than one category to display
    breadcrumbs, selected menu points, etc. appropriately.
    """
    logger.info("Decprecated: lfs.catalog.utils: the function 'get_current_product_category' is deprecated. Please use 'get_current_category'of the Product class.")
    return product.get_current_category(request)


# DEPRECATED 0.6
def get_property_groups(category):
    """Returns all property groups for given category
    """
    logger.info("Decprecated: lfs.catalog.utils: the function 'get_property_groups' is deprecated. Please use 'get_property_groups'of the Category class.")
    return category.get_property_groups()


def get_price_filters(category, product_filter, price_filter):
    """Creates price filter based on the min and max prices of the category's
    products.
    """
    # If a price filter is set we return just this.
    if price_filter:
        return {
            "show_reset": True,
            "min": locale.format("%.2f", price_filter["min"]),
            "max": locale.format("%.2f", price_filter["max"]),
            "disabled": False,
        }

    # Otherwise we calculated min and max based on the current product filters
    products = []
    for product in get_filtered_products_for_category(category, product_filter, None, None):
        products.append(product)
        products.extend(product.variants.filter(active=True))
    product_ids = ", ".join([str(p.id) for p in products])

    cursor = connection.cursor()
    cursor.execute("""SELECT min(effective_price), max(effective_price)
                      FROM catalog_product
                      WHERE id IN (%s)""" % product_ids)
    row = cursor.fetchall()[0]

    try:
        min = locale.format("%.2f", float(row[0]))
    except TypeError:
        min = 0.0
    try:
        max = locale.format("%.2f", float(row[1]))
    except TypeError:
        max = 0.0

    return {
        "show_reset": False,
        "min": min,
        "max": max,
        "disabled": (row[0] and row[1]) is None,
    }


def get_product_filters(category, product_filter, price_filter, sorting):
    """Returns the next product filters based on products which are in the given
    category and within the result set of the current filters.
    """
    properties_mapping = get_property_mapping()
    options_mapping = get_option_mapping()
    property_ids = _get_property_ids()
    product_ids = _get_product_ids(category)
    set_filters = dict(product_filter)

    ########## Number Fields ###################################################
    number_fields = []
    cursor = connection.cursor()
    cursor.execute("""SELECT property_id, min(value_as_float), max(value_as_float)
                      FROM catalog_productpropertyvalue
                      WHERE type=%s
                      AND product_id IN (%s)
                      AND property_id IN (%s)
                      GROUP BY property_id""" % (PROPERTY_VALUE_TYPE_FILTER, product_ids, property_ids))

    for row in cursor.fetchall():
        prop = properties_mapping[row[0]]
        if prop.is_select_field or prop.is_text_field or not prop.filterable:
            continue
        if product_filter.get("number-filter", {}).get(str(prop.id)):
            min, max = product_filter.get("number-filter").get(str(prop.id))[0:2]
            show_reset = True
        else:
            min, max = row[1:3]
            show_reset = False

        try:
            min = locale.format("%.2f", float(min))
        except TypeError:
            min = 0.0
        try:
            max = locale.format("%.2f", float(max))
        except TypeError:
            max = 0.0

        number_fields.append({
            "id": row[0],
            "position": prop.position,
            "object": prop,
            "name": prop.name,
            "title": prop.title,
            "unit": prop.unit,
            "show_reset": show_reset,
            "show_quantity": True,
            "items": {"min": min, "max": max},
        })

    ########## Select Fields & Text Fields #####################################
    result = []
    cursor = connection.cursor()
    cursor.execute("""SELECT property_id, value
                      FROM catalog_productpropertyvalue
                      WHERE type=%s
                      AND product_id IN (%s)
                      AND property_id IN (%s)
                      GROUP BY property_id, value""" % (PROPERTY_VALUE_TYPE_FILTER, product_ids, property_ids))

    properties = {}
    for row in cursor.fetchall():
        prop = properties_mapping[row[0]]

        if prop.is_number_field or not prop.filterable:
            continue

        if prop.is_select_field:
            name = options_mapping[row[1]].name
            position = options_mapping[row[1]].position
        else:
            name = row[1]
            position = 10

        if row[0] not in properties:
            properties[row[0]] = []
        properties[row[0]].append({
            "id": row[0],
            "value": row[1],
            "name": name,
            "title": prop.title,
            "position": position,
            "show_quantity": True,
        })

    # Creates the filters to count the existing products per property option,
    # which is used within the filter portlet
    new_product_filter = {}
    if product_filter.get("number-filter"):
        new_product_filter["number-filter"] = product_filter["number-filter"]

    for prop, options in properties.items():
        for option in options:
            # The option in question is used at any rate
            new_product_filter["select-filter"] = {str(prop): option["value"]}

            # All checked options of all other properties is also used
            for f0, f1 in product_filter.get("select-filter", {}).items():
                if f0 != str(prop):
                    new_product_filter["select-filter"][f0] = f1

                # Tests if the option is checked
                if (f0 == str(prop)) and (option["value"] in f1.split("|")):
                    option["checked"] = True

            option["quantity"] = len(get_filtered_products_for_category(category, new_product_filter, price_filter, None))

    # Transform the group properties into a list of dicts
    for property_id, items in properties.items():
        property = properties_mapping[property_id]
        items.sort(lambda a, b: cmp(a["position"], b["position"]))

        # Move items with zero quantity to the end of the list
        for x in range(0, len(items)):
            if items[x]["quantity"] == 0:
                items.insert(len(items), items.pop(x))

        result.append({
            "id": property_id,
            "position": property.position,
            "unit": property.unit,
            "show_reset": str(property_id) in set_filters.keys(),
            "name": property.name,
            "title": property.title,
            "items": items,
        })

    result.sort(lambda a, b: cmp(a["position"], b["position"]))

    return {
        "select_fields": result,
        "number_fields": number_fields,
    }


def _get_property_ids():
    cursor = connection.cursor()
    cursor.execute("""SELECT DISTINCT property_id
                      FROM catalog_productpropertyvalue""")
    return ", ".join([str(p[0]) for p in cursor.fetchall()])


def _get_product_ids(category):
    all_products = []
    for product in category.get_all_products():
        all_products.append(product)
        all_products.extend(product.variants.filter(active=True))
    return ", ".join([str(p.id) for p in all_products])


def _get_filtered_product_ids(category, product_filter, price_filter):
    products = []
    for product in get_filtered_products_for_category(category, product_filter, price_filter, None):
        products.append(product)
        products.extend(product.variants.filter(active=True))
    return ", ".join([str(p.id) for p in products])


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
        for prop, value in filters.get("select-filter", {}).items():
            if value.find("|") == -1:
                temp.append("((property_id='%s') AND (value='%s'))" % (prop, value))
            else:
                options = []
                for option in value.split("|"):
                    options.append("(value='%s')" % option)
                option_str = " OR ".join(options)
                temp.append("((property_id='%s') AND (%s))" % (prop, option_str))
        for prop, values in filters.get("number-filter", {}).items():
            temp.append("((property_id='%s') AND (value_as_float BETWEEN '%s' AND '%s'))" % (prop, values[0], values[1]))
        fstr = " OR ".join(temp)

        logger.debug("Property Filter String: %s" % fstr)

        # Get all product ids with matching filters. The idea behind this SQL
        # query is: If for every filter (property=value) for a product id exists
        # a "product property value" the product matches.
        length = len(filters.get("select-filter", {}).items()) + len(filters.get("number-filter", {}).items())
        cursor = connection.cursor()
        cursor.execute("""
            SELECT product_id, count(*)
            FROM catalog_productpropertyvalue
            WHERE product_id IN (%s) and (%s) and type=%s
            GROUP BY product_id
            HAVING count(*)=%s""" % (product_ids, fstr, PROPERTY_VALUE_TYPE_FILTER, length))

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
                HAVING count(*)=%s""" % (all_variant_ids, fstr, PROPERTY_VALUE_TYPE_FILTER, length))

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
        variants = lfs.catalog.models.Product.objects.filter(parent__in=products, active=True)

        # Filter the variants by price
        variants = variants.filter(effective_price__range=[price_filter["min"], price_filter["max"]], active=True)

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
        products = products.filter(effective_price__range=[price_filter["min"], price_filter["max"]], active=True)

        # Merge the results
        matched_product_ids.extend([p.id for p in products])

        # And get a new query set of all products
        products = lfs.catalog.models.Product.objects.filter(pk__in=matched_product_ids)

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


# DEPRECATED 0.6
def calculate_packages(product, quantity):
    """Returns amount of packages passed on passes product and quantity.
    DEPRECATED.
    """
    logger.info("Decprecated: lfs.catalog.utils: the function 'calculate_packages' is deprecated.")
    return math.ceil(quantity / product.packing_unit)


# DEPRECATED 0.6
def calculate_real_amount(product, quantity):
    """Returns the amount of pieces in package units. DEPRECATED.
    """
    logger.info("Decprecated: lfs.catalog.utils: the function 'calculate_real_amount' is deprecated. Please use 'get_amount_by_packages'of the Product class.")
    return product.get_amount_by_packages(quantity)
