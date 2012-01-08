# django imports
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST

# lfs imports
import lfs.core.utils
from lfs.core.utils import LazyEncoder
from lfs.core.signals import property_type_changed
from lfs.catalog.models import Property
from lfs.catalog.models import PropertyOption
from lfs.catalog.models import FilterStep


class PropertyAddForm(ModelForm):
    """Form to add a property.
    """
    class Meta:
        model = Property
        fields = ["name"]


class PropertyDataForm(ModelForm):
    """Form to manage core data of a property.
    """
    class Meta:
        model = Property
        fields = ["position", "name", "title", "unit", "filterable", "display_no_results",
            "configurable", "required", "display_on_product", "display_price"]


class PropertyTypeForm(ModelForm):
    """Form to manage property type.
    """
    class Meta:
        model = Property
        fields = ["type"]


class StepTypeForm(ModelForm):
    """Form to manage the step type of a property.
    """
    class Meta:
        model = Property
        fields = ["step_type"]


class SelectFieldForm(ModelForm):
    """Form to manage attributes for select field.
    """
    class Meta:
        model = Property
        fields = ["add_price"]


class NumberFieldForm(ModelForm):
    """Form to manage the number field.
    """
    class Meta:
        model = Property
        fields = ["decimal_places", "unit_min", "unit_max", "unit_step"]


class StepRangeForm(ModelForm):
    """Form to manage step range.
    """
    class Meta:
        model = Property
        fields = ["step"]


@permission_required("core.manage_shop", login_url="/login/")
def manage_properties(request):
    """The main view to manage properties.
    """
    try:
        property = Property.objects.filter(local=False)[0]
        url = reverse("lfs_manage_shop_property", kwargs={"id": property.id})
    except IndexError:
        url = reverse("lfs_add_shop_property")

    return HttpResponseRedirect(url)


@permission_required("core.manage_shop", login_url="/login/")
def manage_property(request, id, template_name="manage/properties/property.html"):
    """The main view to manage the property with passed id.
    """
    property = get_object_or_404(Property, pk=id)
    if request.method == "POST":
        form = PropertyDataForm(instance=property, data=request.POST)
        if form.is_valid():
            new_property = form.save()
            _update_property_positions()
            return lfs.core.utils.set_message_cookie(
                url=reverse("lfs_manage_shop_property", kwargs={"id": property.id}),
                msg=_(u"Property type has been saved."),
            )

    else:
        form = PropertyDataForm(instance=property)

    display_step_form = property.is_number_field and property.filterable

    return render_to_response(template_name, RequestContext(request, {
        "property": property,
        "properties": Property.objects.filter(local=False),
        "form": form,
        "type_form": PropertyTypeForm(instance=property),
        "current_id": int(id),
        "options": options_inline(request, id),
        "steps": steps_inline(request, id),
        "number_field": number_field(request, property),
        "select_field": select_field(request, property),
        "display_step_form": display_step_form,
      }))


@require_POST
@permission_required("core.manage_shop", login_url="/login/")
def update_property_type(request, id):
    """Updates the type of the property.

    This is separated from the data, because a change of type causes a deletion
    of product property values
    """
    property = get_object_or_404(Property, pk=id)
    old_type = property.type
    form = PropertyTypeForm(instance=property, data=request.POST)
    new_property = form.save()

    # Send signal only when the type changed as all values are deleted.
    if old_type != new_property.type:
        property_type_changed.send(property)

    return lfs.core.utils.set_message_cookie(
        url=reverse("lfs_manage_shop_property", kwargs={"id": property.id}),
        msg=_(u"Property type has been changed."),
    )


@permission_required("core.manage_shop", login_url="/login/")
def select_field(request, property, template_name="manage/properties/property_select_field.html"):
    """Displays the form of the select field propery type.
    """
    form = SelectFieldForm(instance=property)

    return render_to_string(template_name, RequestContext(request, {
        "property": property,
        "form": form,
    }))


@require_POST
def save_select_field(request, property_id):
    """Saves the data of a property select field.
    """
    property = get_object_or_404(Property, pk=property_id)

    form = SelectFieldForm(instance=property, data=request.POST)
    property = form.save()

    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@permission_required("core.manage_shop", login_url="/login/")
def number_field(request, property, template_name="manage/properties/property_number_field.html"):
    """Displays the form of the input field propery type
    """
    number_field_form = NumberFieldForm(instance=property)

    return render_to_string(template_name, RequestContext(request, {
        "property": property,
        "number_field_form": number_field_form,
    }))


@require_POST
@permission_required("core.manage_shop", login_url="/login/")
def save_number_field_validators(request, property_id):
    """Saves the validators for the property with passed property_id.
    """
    property = get_object_or_404(Property, pk=property_id)

    form = NumberFieldForm(instance=property, data=request.POST)
    property = form.save()

    response = HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    return lfs.core.utils.set_message_to(response, _(u"Validators have been saved."))


@permission_required("core.manage_shop", login_url="/login/")
def steps_inline(request, property_id, template_name="manage/properties/step_inline.html"):
    """Display the steps of a property. Factored out for Ajax requests.
    """
    property = get_object_or_404(Property, pk=property_id)

    step_form = StepRangeForm(instance=property)
    step_type_form = StepTypeForm(instance=property)

    return render_to_string(template_name, RequestContext(request, {
        "property": property,
        "step_form": step_form,
        "step_type_form": step_type_form,
    }))


@require_POST
@permission_required("core.manage_shop", login_url="/login/")
def save_step_range(request, property_id):
    """Save the steps of the property with given id.
    """
    property = get_object_or_404(Property, pk=property_id)

    form = StepRangeForm(instance=property, data=request.POST)
    property = form.save()

    result = simplejson.dumps({
        "message": _(u"Step range has been saved."),
    }, cls=LazyEncoder)

    return HttpResponse(result)


@require_POST
@permission_required("core.manage_shop", login_url="/login/")
def save_step_type(request, property_id):
    """Save the step type of the property with given id.
    """
    property = get_object_or_404(Property, pk=property_id)

    form = StepTypeForm(instance=property, data=request.POST)
    property = form.save()

    html = [["#steps", steps_inline(request, property_id)]]
    result = simplejson.dumps({
        "html": html,
        "message": _(u"Step type has been saved."),
    }, cls=LazyEncoder)
    return HttpResponse(result)


@require_POST
@permission_required("core.manage_shop", login_url="/login/")
def add_step(request, property_id):
    """Adds a step to property with passed property id resp. updates steps of
    property with passed property id dependent on the given action parameter.
    """
    property = get_object_or_404(Property, pk=property_id)

    if request.POST.get("action") == "add":
        start = request.POST.get("start", "")
        if start != "":
            option = FilterStep.objects.create(start=start, property_id=property_id)
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
        message = _(u"Steps have been updated.")

    html = [["#steps", steps_inline(request, property_id)]]
    result = simplejson.dumps({
        "html": html,
        "message": message,
    }, cls=LazyEncoder)
    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
def delete_step(request, id):
    """Deletes step with given id.
    """
    try:
        step = FilterStep.objects.get(pk=id)
    except FilterStep.DoesNotExist:
        url = request.META.get("HTTP_REFERER", reverse("lfs_manage_shop_property"))
    else:
        property = step.property
        url = reverse("lfs_manage_shop_property", kwargs={"id": property.id})
        step.delete()

    response = HttpResponseRedirect(url)
    return lfs.core.utils.set_message_to(response, _(u"The step has been saved."))


@permission_required("core.manage_shop", login_url="/login/")
def options_inline(request, property_id, template_name="manage/properties/options_inline.html"):
    """Display the options of a propety. Factored out for Ajax requests.
    """
    property = get_object_or_404(Property, pk=property_id)
    return render_to_string(template_name, RequestContext(request, {
        "property": property,
    }))


@permission_required("core.manage_shop", login_url="/login/")
def add_property(request, template_name="manage/properties/add_property.html"):
    """Adds a new property.
    """
    if request.method == "POST":
        form = PropertyAddForm(data=request.POST)
        if form.is_valid():
            property = form.save()
            property.position = 1000
            property.save()
            _update_property_positions()
            return lfs.core.utils.set_message_cookie(
                url=reverse("lfs_manage_shop_property", kwargs={"id": property.id}),
                msg=_(u"Property has been added."),
            )
    else:
        form = PropertyAddForm()

    return render_to_response(template_name, RequestContext(request, {
        "form": form,
        "properties": Property.objects.filter(local=False),
    }))


@require_POST
@permission_required("core.manage_shop", login_url="/login/")
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
        url = reverse("lfs_manage_shop_properties")

    return HttpResponseRedirect(url)


@require_POST
@permission_required("core.manage_shop", login_url="/login/")
def add_option(request, property_id):
    """Adds option to property with passed property id.
    """
    property = get_object_or_404(Property, pk=property_id)

    if request.POST.get("action") == "add":
        name = request.POST.get("name", "")
        price = request.POST.get("price", "")
        try:
            price = float(price)
        except ValueError:
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
                    price = float(request.POST.get("price-%s" % option_id, ""))
                except ValueError:
                    price = 0.0

                option.position = request.POST.get("position-%s" % option_id, 99)
                option.name = request.POST.get("name-%s" % option_id, "")
                option.price = price
                option.save()
        message = _(u"Options have been update.")

    _update_positions(property)

    html = [["#options", options_inline(request, property_id)]]
    result = simplejson.dumps({
        "html": html,
        "message": message
    }, cls=LazyEncoder)
    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
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
