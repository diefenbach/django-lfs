# python imports
from copy import deepcopy

# django imports
from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.forms import ModelForm
from django.forms.widgets import Select
from django.http import HttpResponse
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.caching.utils import lfs_get_object_or_404, get_cache_group_id, invalidate_cache_group_id
from lfs.core.signals import product_changed
from lfs.catalog.models import Product
from lfs.catalog.models import ProductPropertyValue
from lfs.catalog.models import ProductsPropertiesRelation
from lfs.catalog.models import Property
from lfs.catalog.models import PropertyGroup
from lfs.catalog.models import PropertyOption
from lfs.catalog.settings import CATEGORY_VARIANT_CHOICES
from lfs.catalog.settings import PROPERTY_VALUE_TYPE_FILTER
from lfs.catalog.settings import PROPERTY_VALUE_TYPE_VARIANT
from lfs.catalog.settings import VARIANT, PROPERTY_SELECT_FIELD
from lfs.core.utils import LazyEncoder
from lfs.manage import utils as manage_utils


class PropertyOptionForm(ModelForm):
    """Form to add/edit property options.
    """
    class Meta:
        model = PropertyOption
        fields = ("name", )


class PropertyForm(ModelForm):
    """Form to add/edit properties.
    """
    class Meta:
        model = Property
        fields = ("name", )


class ProductVariantSimpleForm(ModelForm):
    """Form to add/edit variants options.
    """
    class Meta:
        model = Product
        fields = ("slug", "name", "price", )


class CategoryVariantForm(ModelForm):
    """
    """
    def __init__(self, *args, **kwargs):
        super(CategoryVariantForm, self).__init__(*args, **kwargs)
        product = kwargs.get("instance")

        choices = []
        for cv in CATEGORY_VARIANT_CHOICES:
            choices.append(cv)

        for variant in Product.objects.filter(parent=product):
            choices.append([variant.id, "%s (%s)" % (variant.get_name(), variant.variant_position)])

        self.fields["category_variant"].widget = Select(choices=choices)

    class Meta:
        model = Product
        fields = ("category_variant", )

class DisplayTypeForm(ModelForm):
    """Form to add/edit product's sub types.
    """
    class Meta:
        model = Product
        fields = ("variants_display_type", )


class DefaultVariantForm(ModelForm):
    """Form to edit the default variant.
    """
    def __init__(self, *args, **kwargs):
        super(DefaultVariantForm, self).__init__(*args, **kwargs)
        instance = kwargs.get("instance")

        choices = [("", "------")]
        choices.extend([(v.id, "%s (%s)" % (v.get_name(), v.variant_position)) for v in instance.variants.all()])

        self.fields["default_variant"].choices = choices

    class Meta:
        model = Product
        fields = ("default_variant", )


@permission_required("core.manage_shop")
def manage_variants(request, product_id, as_string=False, template_name="manage/product/variants.html"):
    """Manages the variants of a product.
    """
    product = Product.objects.get(pk=product_id)

    property_form = PropertyForm()
    property_option_form = PropertyOptionForm()
    variant_simple_form = ProductVariantSimpleForm()
    display_type_form = DisplayTypeForm(instance=product)
    default_variant_form = DefaultVariantForm(instance=product)
    category_variant_form = CategoryVariantForm(instance=product)

    pid = product.get_parent().pk
    group_id = get_cache_group_id('properties-%s' % pid)
    cache_key = "%s-manage-properties-variants-%s-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, group_id, product_id)
    variants = cache.get(cache_key)
    # Get all properties. We need to traverse through all property / options
    # in order to select the options of the current variant.
    if variants is None:
        variants = []
        
        # performance enhancement
        props = product.get_property_select_fields()
        props_options = {}
        for o in PropertyOption.objects.filter(property__in=props):
            props_options.setdefault(o.property_id, {})
            props_options[o.property_id][str(o.pk)] = {
                "id": o.pk,
                "name": o.name,
                "selected": False
            }

        product_variants = product.variants.all().order_by("variant_position")
        selected_options = {}
        for so in ProductPropertyValue.objects.filter(property__in=props, \
                        product__in=product_variants, type=PROPERTY_VALUE_TYPE_VARIANT):
            ppk = so.product_id
            selected_options.setdefault(ppk, {})[so.property_id] = so.value


        for variant in product_variants:
            properties = []
            for prop in props:
                options = deepcopy(props_options.get(prop.pk, {}))
                try:
                    sop = selected_options[variant.pk][prop.pk]
                    options[sop]['selected'] = True
                except KeyError:
                    pass

                properties.append({
                    "id": prop.pk,
                    "name": prop.name,
                    "options": options.values()
                })

            variants.append({
                "id": variant.id,
                "active": variant.active,
                "slug": variant.slug,
                "sku": variant.sku,
                "name": variant.name,
                "price": variant.price,
                "active_price": variant.active_price,
                "active_sku": variant.active_sku,
                "active_name": variant.active_name,
                "position": variant.variant_position,
                "properties": properties
            })

        cache.set(cache_key, variants)

    # Generate list of all property groups; used for group selection
    product_property_group_ids = [p.id for p in product.property_groups.all()]
    shop_property_groups = []
    for property_group in PropertyGroup.objects.all():

        shop_property_groups.append({
            "id": property_group.id,
            "name": property_group.name,
            "selected": property_group.id in product_property_group_ids,
        })

    result = render_to_string(template_name, RequestContext(request, {
        "product": product,
        "variants": variants,
        "shop_property_groups": shop_property_groups,
        "local_properties": product.get_local_properties(),
        "all_properties": product.get_property_select_fields(),
        "property_option_form": property_option_form,
        "property_form": property_form,
        "variant_simple_form": variant_simple_form,
        "display_type_form": display_type_form,
        "default_variant_form": default_variant_form,
        "category_variant_form": category_variant_form,
    }))

    if as_string:
        return result
    else:
        return HttpResponse(result)


# Actions
@permission_required("core.manage_shop")
def add_property(request, product_id):
    """Adds a new property to the product with given product id.
    """
    product = Product.objects.get(pk=product_id)
    property_form = PropertyForm(data=request.POST)
    if property_form.is_valid():
        property = property_form.save(commit=False)
        property.title = property.name
        property.type = PROPERTY_SELECT_FIELD
        property.local = True

        # it doesn't make sense to filter by local properties as every local
        # property has an own id. Maybe we can do this with an grouping id or
        # something like that
        property.filterable = False

        property.save()
        product_property = ProductsPropertiesRelation(product=product, property=property, position=999)
        product_property.save()

        # Refresh positions
        for i, product_property in enumerate(product.productsproperties.all()):
            product_property.position = i
            product_property.save()

    product_changed.send(product)
    pid = product.get_parent().pk
    invalidate_cache_group_id('properties-%s' % pid)

    html = [["#variants", manage_variants(request, product_id, as_string=True)]]

    result = simplejson.dumps({
        "html": html,
        "message": _(u"Property has been added."),
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop")
def delete_property(request, product_id, property_id):
    """Deletes property with passed property id.
    """
    try:
        property = Property.objects.get(pk=property_id)
        product = Product.objects.get(pk=product_id)
    except ObjectDoesNotExist:
        pass
    else:
        property.delete()
        product_changed.send(product)
        pid = product.get_parent().pk
        invalidate_cache_group_id('properties-%s' % pid)

    html = (("#variants", manage_variants(request, product_id, as_string=True)),)

    result = simplejson.dumps({
        "html": html,
        "message": _(u"Property has been deleted."),
        "close-dialog": True,
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop")
def change_property_position(request):
    """Changes property position based on parameters passed by request body.
    """
    product_id = request.GET.get("product_id")
    property_id = int(request.GET.get("property_id"))
    direction = request.GET.get("direction")

    try:
        product_property = ProductsPropertiesRelation.objects.get(product=product_id, property=property_id)
    except ObjectDoesNotExist:
        pass
    else:
        if direction == "up":
            product_property.position -= 3
        else:
            product_property.position += 3

        product_property.save()

    _refresh_property_positions(product_id)
    pid = Product.objects.get(pk=product_id).get_parent().pk
    invalidate_cache_group_id('properties-%s' % pid)

    html = (("#variants", manage_variants(request, product_id, as_string=True)),)

    result = simplejson.dumps({
        "html": html,
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop")
def add_property_option(request, product_id):
    """Adds a new option to the property with given property id.

    NOTE: The reason why to pass the product id here is to be able to redirect
    to the product. Properties can belong to more than one product.

    TODO: Do this with REFERER
    """
    property_option_form = PropertyOptionForm(data=request.POST)
    if property_option_form.is_valid():
        names = request.POST.get("name").split(",")
        position = 999
        property_id = request.POST.get("property_id")
        for name in names:
            property_option = PropertyOption(name=name)
            property_option.property_id = property_id
            property_option.position = position
            property_option.save()
            position += 1

        # Refresh positions
        for i, option in enumerate(PropertyOption.objects.filter(property=property_id)):
            option.position = i
            option.save()

    product = Product.objects.get(pk=product_id)
    product_changed.send(product)
    pid = product.get_parent().pk
    invalidate_cache_group_id('properties-%s' % pid)

    html = [["#variants", manage_variants(request, product_id, as_string=True)]]

    result = simplejson.dumps({
        "html": html,
        "message": _(u"Option has been added."),
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop")
def delete_property_option(request, product_id, option_id):
    """Deletes property option with passed option id.
    """
    try:
        property_option = PropertyOption.objects.get(pk=option_id)
        product = Product.objects.get(pk=product_id)
    except ObjectDoesNotExist:
        pass
    else:
        property_option.delete()
        product_changed.send(product)
        pid = product.get_parent().pk
        invalidate_cache_group_id('properties-%s' % pid)

    html = (("#variants", manage_variants(request, product_id, as_string=True)),)

    result = simplejson.dumps({
        "html": html,
        "message": _(u"Property has been deleted."),
        "close-dialog": True,
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop")
def add_variants(request, product_id):
    """Adds variants to product with passed product_id based on property/option-
    combinations passed within request body.
    """
    cache.delete("%s-variants%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, product_id))

    product = Product.objects.get(pk=product_id)

    # Add variant(s)
    #variant_simple_form = ProductVariantSimpleForm(data=request.POST)

    # We don't have to check whether the form is valid. If the fields
    # are empty we create default ones.

    variants_count = product.variants.count()

    # First we need to prepare the requested properties for the use
    # with cartesian product. That means if the keyword "all" is
    # found we collect all options of this properties.
    properties = []
    for key, value in request.POST.items():
        if key.startswith("property"):
            property_id = key.split("_")[1]
            if value == "all":
                temp = []
                for option in PropertyOption.objects.filter(property=property_id):
                    temp.append("%s|%s" % (property_id, option.id))
                properties.append(temp)
            else:
                properties.append(["%s|%s" % (property_id, value)])

    # Create a variant for every requested option combination
    for i, options in enumerate(manage_utils.cartesian_product(*properties)):

        if product.has_variant(options):
            continue

        name = request.POST.get("name")
        price = request.POST.get("price")
        slug = request.POST.get("slug")

        for option in options:
            property_id, option_id = option.split("|")
            o = PropertyOption.objects.get(pk=option_id)
            if slug:
                slug += "-"
            slug += slugify(o.name)

        slug = "%s-%s" % (product.slug, slug)
        sku = "%s-%s" % (product.sku, i + 1)

        variant = None
        # need to validate the amalgamated slug to make sure it is not already in use
        try:
            variant = Product.objects.get(slug=slug)
            message = _(u"That slug is already in use. Please use another.")
        except Product.MultipleObjectsReturned:
            message = _(u"That slug is already in use. Please use another.")
        except Product.DoesNotExist:
            variant = Product(name=name, slug=slug, sku=sku, parent=product, price=price,
                              variant_position=(variants_count + i + 1) * 10, sub_type=VARIANT)
            try:
                variant.save()
            except IntegrityError:
                continue
            else:
                # By default we copy the property groups of the product to
                # the variants
                for property_group in product.property_groups.all():
                    variant.property_groups.add(property_group)

            # Save the value for this product and property.
            for option in options:
                property_id, option_id = option.split("|")
                ProductPropertyValue.objects.create(product=variant, property_id=property_id, value=option_id, type=PROPERTY_VALUE_TYPE_VARIANT)
                # By default we create also the filter values as this most of
                # the users would expect.
                if Property.objects.get(pk=property_id).filterable:
                    ProductPropertyValue.objects.create(product=variant, property_id=property_id, value=option_id, type=PROPERTY_VALUE_TYPE_FILTER)

            message = _(u"Variants have been added.")

    html = (
        ("#selectable-products-inline", _selectable_products_inline(request, product)),
        ("#variants", manage_variants(request, product_id, as_string=True)),
    )

    result = simplejson.dumps({
        "html": html,
        "message": message,
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop")
def update_variants(request, product_id):
    """Updates/Deletes variants with passed ids (via request body) dependent on
    given action (also via request body).
    """
    product = lfs_get_object_or_404(Product, pk=product_id)

    action = request.POST.get("action")
    if action == "delete":
        message = _(u"Variants have been deleted.")
        for key in request.POST.keys():
            if key.startswith("delete-"):
                try:
                    id = key.split("-")[1]
                    variant = Product.objects.get(pk=id)
                except (IndexError, ObjectDoesNotExist):
                    continue
                else:
                    if product.default_variant == variant:
                        product.default_variant = None
                        product.save()
                    variant.delete()
    elif action == "update":
        message = _(u"Variants have been saved.")
        for key, value in request.POST.items():
            if key.startswith("variant-"):
                id = key.split("-")[1]
                try:
                    variant = Product.objects.get(pk=id)
                except ObjectDoesNotExist:
                    continue
                else:
                    for name in ("slug", "sku", "price"):
                        value = request.POST.get("%s-%s" % (name, id))
                        if value != "":
                            setattr(variant, name, value)

                    # name
                    variant.name = request.POST.get("name-%s" % id)

                    # active
                    active = request.POST.get("active-%s" % id)
                    if active:
                        variant.active = True
                    else:
                        variant.active = False

                    # active attributes
                    for name in ("active_price", "active_sku", "active_name"):
                        value = request.POST.get("%s-%s" % (name, id))
                        if value:
                            setattr(variant, name, True)
                        else:
                            setattr(variant, name, False)

                    # position
                    position = request.POST.get("position-%s" % id)
                    try:
                        variant.variant_position = int(position)
                    except ValueError:
                        variant.variant_position = 10

                    # default variant
                    try:
                        product.default_variant_id = int(request.POST.get("default_variant"))
                    except TypeError:
                        pass
                    else:
                        product.save()
                
                variant.save()

            elif key.startswith("property"):
                # properties are marshalled as: property-variant_id|property_id
                temp = key.split("-")[1]
                variant_id, property_id = temp.split("|")
                variant = Product.objects.get(pk=variant_id)
                property = Property.objects.get(pk=property_id)
                ppv = None
                ppv_filterable = None
                try:
                    ppv = ProductPropertyValue.objects.get(product=variant,
                                                           property_id=property_id,
                                                           type=PROPERTY_VALUE_TYPE_VARIANT)
                    if property.filterable:
                        ppv_filterable = ProductPropertyValue.objects.get(product=variant,
                                                                          property_id=property_id,
                                                                          type=PROPERTY_VALUE_TYPE_FILTER)
                except ProductPropertyValue.DoesNotExist:
                    pass

                if value != '':
                    if not ppv:
                        ppv = ProductPropertyValue.objects.create(product=variant,
                                                                  property_id=property_id,
                                                                  type=PROPERTY_VALUE_TYPE_VARIANT,
                                                                  value=value)
                        if property.filterable:
                            ProductPropertyValue.objects.create(product=variant, property_id=property_id,
                                                                value=value,
                                                                type=PROPERTY_VALUE_TYPE_FILTER)
                    else:
                        ppv.value = value
                        ppv.save()
                        if ppv_filterable:
                            ppv_filterable.value = value
                            ppv_filterable.save()
                elif ppv:
                    ppv.delete()
                    if ppv_filterable:
                        ppv_filterable.delete()

    # Refresh variant positions
    for i, variant in enumerate(product.variants.order_by("variant_position")):
        variant.variant_position = (i + 1) * 10
        variant.save()

    # Send a signal to update cache
    product_changed.send(product)
    pid = product.get_parent().pk
    invalidate_cache_group_id('properties-%s' % pid)

    html = (
        ("#variants", manage_variants(request, product_id, as_string=True)),
        ("#selectable-products-inline", _selectable_products_inline(request, product)),
    )

    result = simplejson.dumps({
        "html": html,
        "message": message,
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop")
def edit_sub_type(request, product_id):
    """Edits the sub type of the variant with given product slug.
    """
    product = Product.objects.get(pk=product_id)

    form = DisplayTypeForm(data=request.POST)
    if form.is_valid():
        product.variants_display_type = request.POST.get("variants_display_type")
        product.save()

    # Send a signal to update cache
    product_changed.send(product)

    html = (("#variants", manage_variants(request, product_id, as_string=True)),)

    result = simplejson.dumps({
        "html": html,
        "message": _(u"Sub type has been saved."),
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop")
def update_category_variant(request, product_id):
    """
    Updates the category variant of the product with passed product_id.
    """
    product = Product.objects.get(pk=product_id)

    form = CategoryVariantForm(instance=product, data=request.POST)
    if form.is_valid():
        form.save()

    # Send a signal to update cache
    product_changed.send(product)

    html = (("#variants", manage_variants(request, product_id, as_string=True)),)

    result = simplejson.dumps({
        "html": html,
        "message": _(u"Category variant has been saved."),
    }, cls=LazyEncoder)

    return HttpResponse(result)


def _refresh_property_positions(product_id):
    """
    """
    # Refresh positions
    for i, product_property in enumerate(ProductsPropertiesRelation.objects.filter(product=product_id)):
        product_property.position = i * 2
        product_property.save()


def _selectable_products_inline(request, product):
    """Updates the product navigation on the left when variants added or
    updated.
    """
    # Somewhat ugly but it works for now. This is will be updated if the
    # planned refactoring of the whole product management takes place
    from lfs.manage.product.product import selectable_products_inline
    from lfs.manage.product.product import _get_filtered_products_for_product_view
    from lfs.manage.product.product import get_current_page
    from django.core.paginator import Paginator
    AMOUNT = 20
    products = _get_filtered_products_for_product_view(request)
    paginator = Paginator(products, AMOUNT)
    temp = product.get_parent()
    page = get_current_page(request, products, temp, AMOUNT)

    try:
        page = paginator.page(page)
    except EmptyPage:
        page = paginator.page(1)

    return selectable_products_inline(request, page, paginator, product.id)

