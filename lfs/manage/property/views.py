import json

# django imports
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator, EmptyPage
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST

# lfs imports
from lfs.caching.listeners import invalidate_cache_group_id
import lfs.core.utils
from lfs.core.utils import LazyEncoder
from lfs.core.utils import atof
from lfs.core.signals import property_type_changed
from lfs.catalog.models import Property
from lfs.catalog.models import PropertyOption
from lfs.catalog.models import FilterStep
from lfs.manage.property.forms import PropertyAddForm
from lfs.manage.property.forms import PropertyDataForm
from lfs.manage.property.forms import PropertyTypeForm
from lfs.manage.property.forms import StepTypeForm
from lfs.manage.property.forms import SelectFieldForm
from lfs.manage.property.forms import NumberFieldForm
from lfs.manage.property.forms import StepRangeForm


# Views
from lfs.manage.utils import get_current_page


@permission_required("core.manage_shop")
def manage_properties(request):
    """The main view to manage properties.
    """
    try:
        prop = Property.objects.filter(local=False)[0]
        url = reverse("lfs_manage_shop_property", kwargs={"id": prop.pk})
    except IndexError:
        url = reverse("lfs_manage_no_shop_properties")

    return HttpResponseRedirect(url)


@permission_required("core.manage_shop")
def pages_inline(request, page, paginator, property_id, template_name="manage/properties/pages_inline.html"):
    """
    Displays the page navigation.
    """
    return render_to_string(template_name, request=request, context={
        "page": page,
        "paginator": paginator,
        "property_id": property_id,
    })


@permission_required("core.manage_shop")
def manage_property(request, id, template_name="manage/properties/property.html"):
    """The main view to manage the property with passed id.
    """
    prop = get_object_or_404(Property, pk=id)
    if request.method == "POST":
        form = PropertyDataForm(instance=prop, data=request.POST)
        if form.is_valid():
            form.save()
            _update_property_positions()
            return lfs.core.utils.set_message_cookie(
                url=reverse("lfs_manage_shop_property", kwargs={"id": prop.id}),
                msg=_(u"Property type has been saved."),
            )

    else:
        form = PropertyDataForm(instance=prop)

    display_step_form = prop.is_number_field and prop.filterable

    properties = _get_filtered_properties_for_property_view(request)
    paginator = Paginator(properties, 25)
    page = get_current_page(request, properties, prop, 25)

    try:
        page = paginator.page(page)
    except EmptyPage:
        page = paginator.page(1)

    return render(request, template_name, {
        "property": prop,
        "form": form,
        "type_form": PropertyTypeForm(instance=prop),
        "current_id": int(id),
        "options": options_inline(request, id),
        "steps": steps_inline(request, id),
        "number_field": number_field(request, prop),
        "select_field": select_field(request, prop),
        "display_step_form": display_step_form,

        "selectable_properties": selectable_properties_inline(request, page, paginator, id),
        # pagination data:
        "properties": properties,
        "pages_inline": pages_inline(request, page, paginator, id),
        "name_filter_value": request.session.get("property_filters", {}).get("property_name", ""),
    })


# Private Methods
def _get_filtered_properties_for_property_view(request):
    """
    Returns a query set with filtered properties based on saved name filter
    and ordering within the current session.
    """
    properties = Property.objects.filter(local=False)
    property_ordering = request.session.get("property-ordering", "name")
    property_ordering_order = request.session.get("property-ordering-order", "")

    # Filter
    property_filters = request.session.get("property_filters", {})
    name = property_filters.get("property_name", "")
    if name != "":
        properties = properties.filter(Q(name__icontains=name) | Q(title__icontains=name))

    properties = properties.order_by("%s%s" % (property_ordering_order, property_ordering))
    return properties


@permission_required("core.manage_shop")
def selectable_properties_inline(request, page, paginator, property_id,
                                 template_name="manage/properties/selectable_properties_inline.html"):
    """
    Displays the selectable properties for the property view.
    """
    try:
        prop = Property.objects.get(pk=property_id)
    except Property.DoesNotExist:
        return ""

    return render_to_string(template_name, request=request, context={
        "paginator": paginator,
        "page": page,
        "current_property": prop
    })


@permission_required("core.manage_shop")
def set_name_filter(request):
    """
    Sets property filters given by passed request.
    """
    req = request.POST if request.method == 'POST' else request.GET
    property_filters = request.session.get("property_filters", {})

    if request.POST.get("name", "") != "":
        property_filters["property_name"] = request.POST.get("name")
    else:
        if property_filters.get("property_name"):
            del property_filters["property_name"]

    request.session["property_filters"] = property_filters

    properties = _get_filtered_properties_for_property_view(request)
    paginator = Paginator(properties, 25)
    page = paginator.page(req.get("page", 1))

    property_id = req.get("property-id", 0)

    html = (
        ("#selectable-properties-inline", selectable_properties_inline(request, page, paginator, property_id)),
        ("#pages-inline", pages_inline(request, page, paginator, property_id)),
    )

    result = json.dumps({
        "html": html,
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def set_properties_page(request):
    """
    Sets the displayed property page.
    """
    property_id = request.GET.get("property-id")

    # property view
    properties = _get_filtered_properties_for_property_view(request)
    amount = 25

    paginator = Paginator(properties, amount)
    page = paginator.page((request.POST if request.method == 'POST' else request.GET).get("page", 1))

    html = (
        ("#pages-inline", pages_inline(request, page, paginator, property_id)),
        ("#selectable-properties-inline", selectable_properties_inline(request, page, paginator, property_id)),
    )

    return HttpResponse(
        json.dumps({"html": html}, cls=LazyEncoder), content_type='application/json')


@permission_required("core.manage_shop")
def no_properties(request, template_name="manage/properties/no_properties.html"):
    """Displays that no properties exist.
    """
    return render(request, template_name, {})


# Actions
@permission_required("core.manage_shop")
@require_POST
def update_property_type(request, id):
    """Updates the type of the property.

    This is separated from the data, because a change of type causes a deletion
    of product property values
    """
    prop = get_object_or_404(Property, pk=id)
    old_type = prop.type
    form = PropertyTypeForm(instance=prop, data=request.POST)
    new_property = form.save()

    # Send signal only when the type changed as all values are deleted.
    if old_type != new_property.type:
        property_type_changed.send(prop)

    # invalidate global properties version number (all product property caches will be invalidated)
    invalidate_cache_group_id('global-properties-version')

    return lfs.core.utils.set_message_cookie(
        url=reverse("lfs_manage_shop_property", kwargs={"id": prop.id}),
        msg=_(u"Property type has been changed."),
    )


@permission_required("core.manage_shop")
def select_field(request, property, template_name="manage/properties/property_select_field.html"):
    """Displays the form of the select field propery type.
    """
    form = SelectFieldForm(instance=property)

    return render_to_string(template_name, request=request, context={
        "property": property,
        "form": form,
    })


@permission_required("core.manage_shop")
@require_POST
def save_select_field(request, property_id):
    """Saves the data of a property select field.
    """
    property = get_object_or_404(Property, pk=property_id)

    form = SelectFieldForm(instance=property, data=request.POST)
    property = form.save()

    # invalidate global properties version number (all product property caches will be invalidated)
    invalidate_cache_group_id('global-properties-version')

    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@permission_required("core.manage_shop")
def number_field(request, property, template_name="manage/properties/property_number_field.html"):
    """Displays the form of the input field propery type
    """
    number_field_form = NumberFieldForm(instance=property)

    return render_to_string(template_name, request=request, context={
        "property": property,
        "number_field_form": number_field_form,
    })


@permission_required("core.manage_shop")
@require_POST
def save_number_field_validators(request, property_id):
    """Saves the validators for the property with passed property_id.
    """
    property = get_object_or_404(Property, pk=property_id)

    form = NumberFieldForm(instance=property, data=request.POST)
    property = form.save()

    # invalidate global properties version number (all product property caches will be invalidated)
    invalidate_cache_group_id('global-properties-version')

    response = HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    return lfs.core.utils.set_message_to(response, _(u"Validators have been saved."))


@permission_required("core.manage_shop")
def steps_inline(request, property_id, template_name="manage/properties/step_inline.html"):
    """Display the steps of a property. Factored out for Ajax requests.
    """
    property = get_object_or_404(Property, pk=property_id)

    step_form = StepRangeForm(instance=property)
    step_type_form = StepTypeForm(instance=property)

    return render_to_string(template_name, request=request, context={
        "property": property,
        "step_form": step_form,
        "step_type_form": step_type_form,
    })


@permission_required("core.manage_shop")
@require_POST
def save_step_range(request, property_id):
    """Save the steps of the property with given id.
    """
    property = get_object_or_404(Property, pk=property_id)

    form = StepRangeForm(instance=property, data=request.POST)
    property = form.save()

    # invalidate global properties version number (all product property caches will be invalidated)
    invalidate_cache_group_id('global-properties-version')

    result = json.dumps({
        "message": _(u"Step range has been saved."),
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
@require_POST
def save_step_type(request, property_id):
    """Save the step type of the property with given id.
    """
    property = get_object_or_404(Property, pk=property_id)

    form = StepTypeForm(instance=property, data=request.POST)
    property = form.save()

    # invalidate global properties version number (all product property caches will be invalidated)
    invalidate_cache_group_id('global-properties-version')

    html = [["#steps", steps_inline(request, property_id)]]
    result = json.dumps({
        "html": html,
        "message": _(u"Step type has been saved."),
    }, cls=LazyEncoder)
    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
@require_POST
def add_step(request, property_id):
    """Adds a step to property with passed property id resp. updates steps of
    property with passed property id dependent on the given action parameter.
    """
    if request.POST.get("action") == "add":
        start = request.POST.get("start", "")
        if start != "":
            FilterStep.objects.create(start=start, property_id=property_id)
        message = _(u"Step has been added.")
    else:
        for step_id in request.POST.getlist("step"):

            try:
                step = FilterStep.objects.get(pk=step_id)
            except FilterStep.DoesNotExist:
                pass
            else:
                step.start = request.POST.get("start-%s" % step_id, "")
                step.save()
                # invalidate global properties version number (all product property caches will be invalidated)
                invalidate_cache_group_id('global-properties-version')
        message = _(u"Steps have been updated.")

    html = [["#steps", steps_inline(request, property_id)]]
    result = json.dumps({
        "html": html,
        "message": message,
    }, cls=LazyEncoder)
    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def delete_step(request, id):
    """Deletes step with given id.
    """
    try:
        step = FilterStep.objects.get(pk=id)
    except FilterStep.DoesNotExist:
        url = request.META.get("HTTP_REFERER", reverse("lfs_manage_shop_property"))
    else:
        prop = step.property
        url = reverse("lfs_manage_shop_property", kwargs={"id": prop.id})
        step.delete()
        # invalidate global properties version number (all product property caches will be invalidated)
        invalidate_cache_group_id('global-properties-version')

    response = HttpResponseRedirect(url)
    return lfs.core.utils.set_message_to(response, _(u"The step has been saved."))


@permission_required("core.manage_shop")
def options_inline(request, property_id, template_name="manage/properties/options_inline.html"):
    """Display the options of a propety. Factored out for Ajax requests.
    """
    property = get_object_or_404(Property, pk=property_id)
    return render_to_string(template_name, request=request, context={
        "property": property,
    })


@permission_required("core.manage_shop")
def add_property(request, template_name="manage/properties/add_property.html"):
    """Adds a new property.
    """
    if request.method == "POST":
        form = PropertyAddForm(data=request.POST)
        if form.is_valid():
            property = form.save()
            property.position = 1000
            property.title = property.name
            property.save()
            _update_property_positions()
            return lfs.core.utils.set_message_cookie(
                url=reverse("lfs_manage_shop_property", kwargs={"id": property.id}),
                msg=_(u"Property has been added."),
            )
    else:
        form = PropertyAddForm()

    return render(request, template_name, {
        "form": form,
        "properties": Property.objects.filter(local=False),
        "came_from": (request.POST if request.method == 'POST' else request.GET).get("came_from",
                                                                                     reverse("lfs_manage_shop_properties")),
    })


@permission_required("core.manage_shop")
@require_POST
def delete_property(request, id):
    """Deletes the property with given id.
    """
    try:
        property = Property.objects.get(pk=id)
    except Property.DoesNotExist:
        url = request.META.get("HTTP_REFERER", reverse("lfs_manage_shop_property"))
    else:
        property.delete()
        _update_property_positions()
        # invalidate global properties version number (all product property caches will be invalidated)
        invalidate_cache_group_id('global-properties-version')
        url = reverse("lfs_manage_shop_properties")

    return HttpResponseRedirect(url)


@permission_required("core.manage_shop")
@require_POST
def add_option(request, property_id):
    """Adds option to property with passed property id.
    """
    property = get_object_or_404(Property, pk=property_id)

    if request.POST.get("action") == "add":
        name = request.POST.get("name", "")
        price = request.POST.get("price", "")
        try:
            price = abs(atof(str(price)))
        except (TypeError, ValueError):
            price = 0.0

        if name != "":
            option = PropertyOption.objects.create(name=name, price=price, property_id=property_id)
            message = _(u"Option has been added.")
        else:
            message = _(u"Option could not be added.")
    else:
        for option_id in request.POST.getlist("option"):
            try:
                option = PropertyOption.objects.get(pk=option_id)
            except PropertyOption.DoesNotExist:
                pass
            else:
                try:
                    price = abs(atof(str(request.POST.get("price-%s" % option_id, ""))))
                except (TypeError, ValueError):
                    price = 0.0

                try:
                    position = int(request.POST.get("position-%s" % option_id, 99))
                except ValueError:
                    position = 99

                option.position = position
                option.name = request.POST.get("name-%s" % option_id, "")
                option.price = price
                option.save()
        message = _(u"Options have been updated.")

    _update_positions(property)
    # invalidate global properties version number (all product property caches will be invalidated)
    invalidate_cache_group_id('global-properties-version')

    html = [["#options", options_inline(request, property_id)]]
    result = json.dumps({
        "html": html,
        "message": message
    }, cls=LazyEncoder)
    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def delete_option(request, id):
    """Deletes option with given id.
    """
    try:
        option = PropertyOption.objects.get(pk=id)
    except option.DoesNotExist:
        url = request.META.get("HTTP_REFERER", reverse("lfs_manage_shop_property"))
    else:
        property = option.property
        url = reverse("lfs_manage_shop_property", kwargs={"id": property.id})
        option.delete()
        _update_positions(property)
        # invalidate global properties version number (all product property caches will be invalidated)
        invalidate_cache_group_id('global-properties-version')

    return HttpResponseRedirect(url)


def _update_property_positions():
    """Updates position of options of given property.
    """
    for i, property in enumerate(Property.objects.exclude(local=True)):
        property.position = (i + 1) * 10
        property.save()


def _update_positions(property):
    """Updates position of options of given property.
    """
    for i, option in enumerate(property.options.all()):
        option.position = (i + 1) * 10
        option.save()
