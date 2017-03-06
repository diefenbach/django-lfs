import json
from copy import deepcopy

from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import EmptyPage
from django.db import IntegrityError
from django.forms import ModelForm, ChoiceField
from django.forms.widgets import Select
from django.http import HttpResponse
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

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
from lfs.core.utils import atof
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
    """ Variants add form.
    """
    def __init__(self, all_properties, *args, **kwargs):
        super(ProductVariantSimpleForm, self).__init__(*args, **kwargs)
        self.fields['slug'].required = False
        for prop_dict in all_properties:
            prop = prop_dict['property']
            property_group = prop_dict['property_group']
            property_group_id = property_group.pk if property_group else 0
            property_group_name = property_group.name if property_group else _('Local')
            field_label = u'<span class="property-group-label">[%s]</span> %s' % (property_group_name, prop.name)
            choices = [('all', _('All')), ('', '---')]
            choices.extend(list(prop.options.values_list('pk', 'name')))
            self.fields['property_%s_%s' % (property_group_id, prop.id)] = ChoiceField(label=field_label,
                                                                                       choices=choices,
                                                                                       required=False)
            self.initial['property_%s_%s' % (property_group_id, prop.id)] = 'all'

    class Meta:
        model = Product
        fields = ("slug", "name", "price", )


class ProductVariantCreateForm(ModelForm):
    """ Form used to create product variant for specific set of options
    """
    def __init__(self, options=None, product=None, *args, **kwargs):
        super(ProductVariantCreateForm, self).__init__(*args, **kwargs)
        self.fields['slug'].required = False
        self.options = options
        self.product = product

    def prepare_slug(self, slug):
        for option in self.options:
            property_group_id, property_id, option_id = option.split("|")
            o = PropertyOption.objects.get(pk=option_id)
            if slug:
                slug += "-"
            slug += slugify(o.name)

        product_slug = self.product.slug
        if product_slug is None:
            product_slug = ''
        if product_slug + slug.replace('-', '') == '':
            slug = ''
        else:
            slug = "%s-%s" % (product_slug, slug)
            slug = slug.rstrip('-')

        # create unique slug
        slug = slug[:80]
        new_slug = slug
        counter = 1
        while Product.objects.filter(slug=new_slug).exists():
            new_slug = '%s-%s' % (slug[:(79 - len(str(counter)))], counter)
            counter += 1
        slug = new_slug

        return slug

    def clean(self):
        cleaned_data = super(ProductVariantCreateForm, self).clean()
        slug = self.prepare_slug(cleaned_data.get('slug', ''))
        cleaned_data['slug'] = slug

        return cleaned_data

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
def manage_variants(request, product_id, as_string=False, variant_simple_form=None, template_name="manage/product/variants.html"):
    """Manages the variants of a product.
    """
    product = Product.objects.get(pk=product_id)

    all_properties = product.get_variants_properties()

    property_form = PropertyForm()
    property_option_form = PropertyOptionForm()
    if not variant_simple_form:
        variant_simple_form = ProductVariantSimpleForm(all_properties=all_properties)
    display_type_form = DisplayTypeForm(instance=product)
    default_variant_form = DefaultVariantForm(instance=product)
    category_variant_form = CategoryVariantForm(instance=product)

    pid = product.get_parent().pk
    properties_version = get_cache_group_id('global-properties-version')
    group_id = '%s-%s' % (properties_version, get_cache_group_id('properties-%s' % pid))
    cache_key = "%s-manage-properties-variants-%s-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, group_id, product_id)
    variants = cache.get(cache_key)
    # Get all properties. We need to traverse through all property / options
    # in order to select the options of the current variant.
    if variants is None:
        variants = []

        props_dicts = product.get_variants_properties()

        # for each property prepare list of its options
        all_props = [prop_dict['property'] for prop_dict in props_dicts]
        props_options = {}
        for o in PropertyOption.objects.filter(property__in=all_props):
            props_options.setdefault(o.property_id, {})
            props_options[o.property_id][str(o.pk)] = {
                "id": o.pk,
                "name": o.name,
                "selected": False
            }

        product_variants = product.variants.all().order_by("variant_position")
        selected_options = {}
        for prop_dict in props_dicts:
            prop = prop_dict['property']
            property_group = prop_dict['property_group']
            property_group_id = property_group.pk if property_group else 0

            for so in ProductPropertyValue.objects.filter(property=prop,
                                                          property_group=property_group,
                                                          product__in=product_variants,
                                                          type=PROPERTY_VALUE_TYPE_VARIANT):
                ppk = so.product_id
                selected_groups = selected_options.setdefault(ppk, {})
                selected_groups.setdefault(property_group_id, {})[so.property_id] = so.value

        for variant in product_variants:
            properties = []
            for prop_dict in props_dicts:
                prop = prop_dict['property']
                property_group = prop_dict['property_group']
                property_group_id = property_group.pk if property_group else 0

                options = deepcopy(props_options.get(prop.pk, {}))
                try:
                    sop = selected_options[variant.pk][property_group_id][prop.pk]
                    options[sop]['selected'] = True
                except KeyError:
                    pass

                properties.append({
                    "id": prop.pk,
                    "name": prop.name,
                    "options": options.values(),
                    "property_group_id": property_group.pk if property_group else 0,
                    "property_group": property_group
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

    result = render_to_string(template_name, request=request, context={
        "product": product,
        "variants": variants,
        "shop_property_groups": shop_property_groups,
        "local_properties": product.get_local_properties(),
        "all_properties": all_properties,
        "property_option_form": property_option_form,
        "property_form": property_form,
        "variant_simple_form": variant_simple_form,
        "display_type_form": display_type_form,
        "default_variant_form": default_variant_form,
        "category_variant_form": category_variant_form,
    })

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

    result = json.dumps({
        "html": html,
        "message": _(u"Property has been added."),
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


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

    result = json.dumps({
        "html": html,
        "message": _(u"Property has been deleted."),
        "close-dialog": True,
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


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

    result = json.dumps({
        "html": html,
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


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
        message = _(u'Option has been added.')
    else:
        message = _(u'Invalid data. Correct it and try again.')

    product = Product.objects.get(pk=product_id)
    product_changed.send(product)
    pid = product.get_parent().pk
    invalidate_cache_group_id('properties-%s' % pid)

    html = [["#variants", manage_variants(request, product_id, as_string=True)]]

    result = json.dumps({
        "html": html,
        "message": message,
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


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

    result = json.dumps({
        "html": html,
        "message": _(u"Property has been deleted."),
        "close-dialog": True,
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def add_variants(request, product_id):
    """Adds variants to product with passed product_id based on property/option-
    combinations passed within request body.
    """
    cache.delete("%s-variants%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, product_id))

    product = Product.objects.get(pk=product_id)
    all_properties = product.get_variants_properties()

    variant_simple_form = ProductVariantSimpleForm(all_properties=all_properties, data=request.POST)

    message = ''
    added_count = 0

    if variant_simple_form.is_valid():
        # Add variant(s)
        variants_count = product.variants.count()

        # First we need to prepare the requested properties for the use
        # with cartesian product. That means if the keyword "all" is
        # found we collect all options of this properties.
        properties = []
        for key, value in variant_simple_form.cleaned_data.items():
            if key.startswith("property"):
                _property, property_group_id, property_id = key.split("_")
                if value == "all":
                    temp = []
                    for option in PropertyOption.objects.filter(property=property_id):
                        temp.append("%s|%s|%s" % (property_group_id, property_id, option.id))
                    properties.append(temp)
                elif value == '':
                    continue
                else:
                    properties.append(["%s|%s|%s" % (property_group_id, property_id, value)])

        # Create a variant for every requested option combination
        for i, options in enumerate(manage_utils.cartesian_product(*properties)):
            if product.has_variant(options, only_active=False):
                continue

            pvcf = ProductVariantCreateForm(options=options, product=product, data=request.POST)
            if pvcf.is_valid():
                variant = pvcf.save(commit=False)
                variant.sku = "%s-%s" % (product.sku, i + 1)
                variant.parent = product
                variant.variant_position = (variants_count + i + 1) * 10
                variant.sub_type = VARIANT

                try:
                    variant.save()
                    added_count += 1
                except IntegrityError:
                    continue

                # By default we copy the property groups of the product to
                # the variants
                for property_group in product.property_groups.all():
                    variant.property_groups.add(property_group)

                # Save the value for this product and property.
                for option in options:
                    property_group_id, property_id, option_id = option.split("|")
                    # local properties are not bound to property groups
                    property_group_id = None if property_group_id == '0' else property_group_id
                    ProductPropertyValue.objects.create(product=variant,
                                                        property_group_id=property_group_id,
                                                        property_id=property_id,
                                                        value=option_id,
                                                        type=PROPERTY_VALUE_TYPE_VARIANT)
                    # By default we create also the filter values as this most of
                    # the users would expect.
                    if Property.objects.get(pk=property_id).filterable:
                        ProductPropertyValue.objects.create(product=variant,
                                                            property_group_id=property_group_id,
                                                            property_id=property_id,
                                                            value=option_id,
                                                            type=PROPERTY_VALUE_TYPE_FILTER)
            else:
                continue
        else:
            message = _(u"No variants have been added.")

            if added_count > 0:
                message = _(u"Variants have been added.")
        variant_simple_form = ProductVariantSimpleForm(all_properties=all_properties)

    html = (
        ("#selectable-products-inline", _selectable_products_inline(request, product)),
        ("#variants", manage_variants(request, product_id, as_string=True, variant_simple_form=variant_simple_form)),
    )

    result = json.dumps({
        "html": html,
        "message": message,
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def update_variants(request, product_id):
    """Updates/Deletes variants with passed ids (via request body) dependent on
    given action (also via request body).
    """
    product = lfs_get_object_or_404(Product, pk=product_id)

    message = ''
    action = request.POST.get("action")
    if action == "delete":
        message = _(u"Variants have been deleted.")
        for key in request.POST.keys():
            if key.startswith("delete-"):
                try:
                    prop_id = key.split("-")[1]
                    variant = Product.objects.get(pk=prop_id)
                except (IndexError, ObjectDoesNotExist):
                    continue
                else:
                    if product.default_variant == variant:
                        product.default_variant = None
                        product.save()
                    variant.delete()
    elif action == "update":
        # TODO: change all of these to formsets or something that will allow for error hangling/messages
        message = _(u"Variants have been saved.")
        for key, value in request.POST.items():
            if key.startswith("variant-"):
                prop_id = key.split("-")[1]
                try:
                    variant = Product.objects.get(pk=prop_id)
                except ObjectDoesNotExist:
                    continue
                else:
                    for name in ("sku", "price"):
                        value = request.POST.get("%s-%s" % (name, prop_id))
                        if value != "":
                            if name == 'price':
                                try:
                                    value = abs(atof(str(value)))
                                except (TypeError, ValueError):
                                    value = 0.0
                            setattr(variant, name, value)

                    # handle slug - ensure it is unique
                    slug = request.POST.get("slug-%s" % prop_id)
                    if variant.slug != slug:
                        counter = 1
                        new_slug = slug[:80]
                        while Product.objects.exclude(pk=variant.pk).filter(slug=new_slug).exists():
                            new_slug = '%s-%s' % (slug[:(79 - len(str(counter)))], counter)
                            counter += 1
                        variant.slug = new_slug

                    # name
                    variant.name = request.POST.get("name-%s" % prop_id)

                    # active
                    active = request.POST.get("active-%s" % prop_id)
                    if active:
                        variant.active = True
                    else:
                        variant.active = False

                    # active attributes
                    for name in ("active_price", "active_sku", "active_name"):
                        value = request.POST.get("%s-%s" % (name, prop_id))
                        if value:
                            setattr(variant, name, True)
                        else:
                            setattr(variant, name, False)

                    # position
                    position = request.POST.get("position-%s" % prop_id)
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
                # properties are marshalled as: property-variant_id|property_group_id|property_id
                temp = key.split("-")[1]
                variant_id, property_group_id, property_id = temp.split("|")
                if property_group_id == '0':  # local properties are not bound to property groups
                    property_group_id = None
                try:
                    variant = Product.objects.get(pk=variant_id)
                except Product.DoesNotExist:
                    continue
                prop = Property.objects.get(pk=property_id)
                ppv = None
                try:
                    ppv = ProductPropertyValue.objects.get(product=variant,
                                                           property_id=property_id,
                                                           property_group_id=property_group_id,
                                                           type=PROPERTY_VALUE_TYPE_VARIANT)
                except ProductPropertyValue.DoesNotExist:
                    pass

                if prop.filterable:  # it is possible that multiple values are selected for filter
                    ppv_filterables = ProductPropertyValue.objects.filter(product=variant,
                                                                          property_group_id=property_group_id,
                                                                          property_id=property_id,
                                                                          type=PROPERTY_VALUE_TYPE_FILTER)

                if value != '':
                    is_changed = True
                    if not ppv:
                        ppv = ProductPropertyValue.objects.create(product=variant,
                                                                  property_group_id=property_group_id,
                                                                  property_id=property_id,
                                                                  type=PROPERTY_VALUE_TYPE_VARIANT,
                                                                  value=value)
                    else:
                        is_changed = ppv.value != value
                        ppv.value = value
                        ppv.save()

                    if prop.filterable and is_changed:
                        ppv_filterables.delete()
                        ProductPropertyValue.objects.create(product=variant,
                                                            property_group_id=property_group_id,
                                                            property_id=property_id,
                                                            value=value,
                                                            type=PROPERTY_VALUE_TYPE_FILTER)

                elif ppv:
                    ppv.delete()
                    ppv_filterables.delete()

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

    result = json.dumps({
        "html": html,
        "message": message,
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


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

    result = json.dumps({
        "html": html,
        "message": _(u"Sub type has been saved."),
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


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

    result = json.dumps({
        "html": html,
        "message": _(u"Category variant has been saved."),
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


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
