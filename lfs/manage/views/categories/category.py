# django imports
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.caching.utils import lfs_get_object_or_404
from lfs.catalog.models import Category
from lfs.core.widgets.image import LFSImageInput
from lfs.manage import utils as manage_utils
from lfs.manage.views.categories.products import manage_products
from lfs.manage.views.categories.seo import edit_seo
from lfs.manage.views.categories.view import category_view
from lfs.manage.views.categories.portlet import manage_categories_portlet
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

        try:
            context = kwargs["instance"]
        except KeyError:
            context = None

    class Meta:
        model = Category
        fields = ("name", "slug", "short_description", "description",
                  "exclude_from_navigation", "image", "static_block")


@permission_required("core.manage_shop", login_url="/login/")
def manage_categories(request):
    """Dispatches to the first category or to the add category form if no
    category exists yet.
    """
    try:
        category = Category.objects.all()[0]
    except IndexError:
        url = reverse("lfs_manage_add_top_category")
    else:
        url = reverse("lfs_manage_category", kwargs={"category_id": category.id})

    return HttpResponseRedirect(url)


@permission_required("core.manage_shop", login_url="/login/")
def manage_category(request, category_id, template_name="manage/category/manage_category.html"):
    """Displays the form to manage the category with given category id.
    """
    category = Category.objects.get(pk=category_id)

    return render_to_response(template_name, RequestContext(request, {
        "categories_portlet": manage_categories_portlet(request, category_id),
        "category": category,
        "data": category_data(request, category_id),
        "seo": edit_seo(request, category_id),
        "view": category_view(request, category_id),
        "portlets": portlets_inline(request, category),
        "dialog_message": _("Do you really want to delete the category <b>'%(name)s'</b> and all its sub categories?" % {"name": category.name}),
    }))


@permission_required("core.manage_shop", login_url="/login/")
def category_data(request, category_id, template_name="manage/category/data.html"):
    """Displays the core data for the category_id with passed category_id.

    This is used as a part of the whole category form.
    """
    category = Category.objects.get(pk=category_id)

    if request.method == "POST":
        form = CategoryForm(data=request.POST, instance=category, files=request.FILES)
    else:
        form = CategoryForm(instance=category)

    return render_to_string(template_name, RequestContext(request, {
        "category": category,
        "form": form,
    }))


# Actions
@permission_required("core.manage_shop", login_url="/login/")
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
        return manage_category(request, category.id)

    # Delete image
    if request.POST.get("delete_image"):
        category.image.delete()

    # Update category level
    category.level = len(category.get_parents()) + 1
    category.save()
    for child in category.get_all_children():
        child.level = len(child.get_parents()) + 1
        child.save()

    # Update positions
    manage_utils.update_category_positions(category.parent)

    url = reverse("lfs_manage_category", kwargs={"category_id": category_id})
    return HttpResponseRedirect(url)


@permission_required("core.manage_shop", login_url="/login/")
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

    return render_to_response(template_name, RequestContext(request, {
        "next": request.REQUEST.get("next", request.META.get("HTTP_REFERER")),
        "category": parent,
        "form": form,
    }))


@require_POST
@permission_required("core.manage_shop", login_url="/login/")
def delete_category(request, id):
    """Deletes category with given id.
    """
    category = lfs_get_object_or_404(Category, pk=id)
    parent = category.parent
    category.delete()
    manage_utils.update_category_positions(parent)

    url = reverse("lfs_manage_categories")
    return HttpResponseRedirect(url)


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
