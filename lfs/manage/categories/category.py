import json

from django.contrib.auth.decorators import permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.utils.translation import ugettext_lazy as _

from lfs.caching.utils import lfs_get_object_or_404
from lfs.catalog.models import Category
from lfs.core.utils import LazyEncoder
from lfs.core.utils import set_category_levels
from lfs.core.widgets.image import LFSImageInput
from lfs.manage import utils as manage_utils
from lfs.manage.categories.view import category_view
from lfs.manage.categories.portlet import manage_categories_portlet
from lfs.manage.seo.views import SEOView
from lfs.manage.views.lfs_portlets import portlets_inline


class CategoryAddForm(ModelForm):
    """Process form to add a category.
    """
    class Meta:
        model = Category
        fields = ("name", "slug")


class CategoryForm(ModelForm):
    """Process form to edit a category.
    """
    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.fields["image"].widget = LFSImageInput()

    class Meta:
        model = Category
        fields = ("name", "slug", "short_description", "description",
                  "exclude_from_navigation", "image", "static_block")


@permission_required("core.manage_shop")
def manage_categories(request):
    """Dispatches to the first category or to the add category form if no
    category exists yet.
    """
    try:
        category = Category.objects.all()[0]
    except IndexError:
        url = reverse("lfs_manage_no_categories")
    else:
        url = reverse("lfs_manage_category", kwargs={"category_id": category.id})

    return HttpResponseRedirect(url)


@permission_required("core.manage_shop")
def manage_category(request, category_id, template_name="manage/category/manage_category.html"):
    """Displays the form to manage the category with given category id.
    """
    category = Category.objects.get(pk=category_id)

    return render(request, template_name, {
        "categories_portlet": manage_categories_portlet(request, category_id),
        "category": category,
        "data": category_data(request, category_id),
        "seo": SEOView(Category).render(request, category),
        "view": category_view(request, category_id),
        "portlets": portlets_inline(request, category),
        "dialog_message": _("Do you really want to delete the category <b>'%(name)s'</b> and all its sub categories?") % {"name": category.name},
    })


@permission_required("core.manage_shop")
def category_data(request, category_id, form=None, template_name="manage/category/data.html"):
    """Displays the core data for the category_id with passed category_id.

    This is used as a part of the whole category form.
    """
    category = Category.objects.get(pk=category_id)

    if request.method == "POST":
        form = CategoryForm(instance=category, data=request.POST)
    else:
        form = CategoryForm(instance=category)

    return render_to_string(template_name, request=request, context={
        "category": category,
        "form": form,
    })


@permission_required("core.manage_shop")
def category_by_id(request, category_id):
    """
    Little helper which returns a category by id. (For the shop customer the
    products are displayed by slug, for the manager by id).
    """
    category = Category.objects.get(pk=category_id)
    url = reverse("lfs_category", kwargs={"slug": category.slug})
    return HttpResponseRedirect(url)


# Actions
@permission_required("core.manage_shop")
def edit_category_data(request, category_id, template_name="manage/category/data.html"):
    """Updates the category data.
    """
    category = Category.objects.get(pk=category_id)

    form = CategoryForm(instance=category, data=request.POST, files=request.FILES)
    if form.is_valid():
        form.save()
        message = _(u"Category data have been saved.")
    else:
        message = _(u"Please correct the indicated errors.")

    # Delete image
    if request.POST.get("delete_image"):
        category.image.delete()

    html = [
        ["#data", category_data(request, category.id)],
        ["#categories-portlet", manage_categories_portlet(request, category.id)],
    ]

    result = json.dumps({
        "message": message,
        "html": html,
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


@permission_required("core.manage_shop")
def add_category(request, category_id="", template_name="manage/category/add_category.html"):
    """Provides an add form and adds a new category to category with given id.
    """
    if category_id == "":
        parent = None
    else:
        try:
            parent = Category.objects.get(pk=category_id)
        except ObjectDoesNotExist:
            parent = None

    if request.method == "POST":
        form = CategoryAddForm(data=request.POST)
        if form.is_valid():
            new_category = form.save(commit=False)
            new_category.parent = parent
            new_category.position = 999
            if parent:
                new_category.level = parent.level + 1
            new_category.save()

            # Update positions
            manage_utils.update_category_positions(parent)
            url = reverse("lfs_manage_category", kwargs={"category_id": new_category.id})
            return HttpResponseRedirect(url)
    else:
        form = CategoryAddForm(initial={"parent": category_id})

    return render(request, template_name, {
        "category": parent,
        "form": form,
        "came_from": (request.POST if request.method == 'POST' else request.GET).get("came_from", reverse("lfs_manage_categories")),
    })


@permission_required("core.manage_shop")
@require_POST
def delete_category(request, id):
    """Deletes category with given id.
    """
    category = lfs_get_object_or_404(Category, pk=id)
    parent = category.parent
    category.delete()
    manage_utils.update_category_positions(parent)

    url = reverse("lfs_manage_categories")
    return HttpResponseRedirect(url)


@permission_required("core.manage_shop")
def sort_categories(request):
    """Sort categories
    """
    category_list = request.POST.get("categories", "").split('&')
    assert (isinstance(category_list, list))
    if len(category_list) > 0:
        pos = 10
        for cat_str in category_list:
            child, parent_id = cat_str.split('=')
            child_id = child[9:-1]  # category[2]
            child_obj = Category.objects.get(pk=child_id)

            parent_obj = None
            if parent_id != 'root':
                parent_obj = Category.objects.get(pk=parent_id)

            child_obj.parent = parent_obj
            child_obj.position = pos
            child_obj.save()

            pos = pos + 10

    set_category_levels()

    result = json.dumps({
        "message": _(u"The categories have been sorted."),
    }, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


# Privates
def _category_choices(context):
    """Returns categories to be used as choices for the field parent.
    Note: context is the category for which the form is applied.
    """
    categories = [("", "-")]
    for category in Category.objects.filter(parent=None):
        if context != category:
            categories.append((category.id, category.name))
            _category_choices_children(categories, category, context)
    return categories


def _category_choices_children(categories, category, context, level=1):
    """Adds the children of the given category to categories.
    Note: context is the category for which the form is applied.
    """
    for category in category.category_set.all():
        if context != category:
            categories.append((category.id, "%s %s" % ("-" * level * 5, category.name)))
            _category_choices_children(categories, category, context, level + 1)
