# django imports
from django.contrib.admin import widgets
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.db.models import Q
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST

# lfs imports
import lfs.core.utils
from lfs.caching.utils import lfs_get_object_or_404
from lfs.catalog.models import Category
from lfs.catalog.models import Product
from lfs.catalog.settings import VARIANT, PRODUCT_TYPE_FORM_CHOICES, PRODUCT_TEMPLATES
from lfs.core.utils import LazyEncoder
from lfs.manage.views.product.images import manage_images
from lfs.manage.views.product.seo import manage_seo
from lfs.manage.views.product.properties import manage_properties
from lfs.manage.views.lfs_portlets import portlets_inline
from lfs.utils.widgets import SelectImage


# Forms
class ProductAddForm(ModelForm):
    """Form to add a new product.
    """
    class Meta:
        model = Product
        fields = ("name", "slug")


class ProductSubTypeForm(ModelForm):
    """Form to change the sub type.
    """
    class Meta:
        model = Product
        fields = ("sub_type",)

    def __init__(self, *args, **kwargs):
        super(ProductSubTypeForm, self).__init__(*args, **kwargs)
        self.fields["sub_type"].choices = PRODUCT_TYPE_FORM_CHOICES


class ProductDataForm(ModelForm):
    """Form to add and edit master data of a product.
    """
    def __init__(self, *args, **kwargs):
        super(ProductDataForm, self).__init__(*args, **kwargs)
        self.fields["template"].widget = SelectImage(choices=PRODUCT_TEMPLATES)

    class Meta:
        model = Product
        fields = ("active", "name", "slug", "sku", "sku_manufacturer", "price", "tax", "price_calculator",
            "short_description", "description", "for_sale", "for_sale_price", "static_block", "template",
            "active_price_calculation", "price_calculation", "price_unit", "unit")

    def clean(self):
        super(ProductDataForm, self).clean()
        if self.instance:
            redirect_to = self.data.get("redirect_to", "")
            if redirect_to != "":
                lfs.core.utils.set_redirect_for(self.instance.get_absolute_url(), redirect_to)
            else:
                lfs.core.utils.remove_redirect_for(self.instance.get_absolute_url())

        return self.cleaned_data


class VariantDataForm(ModelForm):
    """Form to add and edit master data of a variant.
    """
    def __init__(self, *args, **kwargs):
        super(VariantDataForm, self).__init__(*args, **kwargs)
        self.fields["template"].widget = SelectImage(choices=PRODUCT_TEMPLATES)

    class Meta:
        model = Product
        fields = ("active", "active_name", "name", "slug", "active_sku", "sku", "sku_manufacturer",
            "active_price", "price", "price_calculator", "active_short_description", "short_description", "active_description",
            "description", "for_sale", "for_sale_price", "active_for_sale", "active_for_sale_price",
            "active_related_products", "active_static_block", "static_block", "template")

    def clean(self):
        """
        """
        if self.instance:
            redirect_to = self.data.get("redirect_to", "")
            if redirect_to != "":
                lfs.core.utils.set_redirect_for(self.instance.get_absolute_url(), redirect_to)
            else:
                lfs.core.utils.remove_redirect_for(self.instance.get_absolute_url())

        return self.cleaned_data


class ProductStockForm(ModelForm):
    """Form to add and edit stock data of a product.
    """
    class Meta:
        model = Product
        fields = ("weight", "width", "height", "length", "manage_stock_amount",
                  "stock_amount", "manual_delivery_time", "delivery_time",
                  "deliverable", "order_time", "ordered_at", "active_dimensions",
                  "packing_unit", "packing_unit_unit", "active_packing_unit")

    def __init__(self, *args, **kwargs):
        super(ProductStockForm, self).__init__(*args, **kwargs)
        self.fields["ordered_at"].widget = widgets.AdminDateWidget()


@permission_required("core.manage_shop", login_url="/login/")
def manage_product(request, product_id, template_name="manage/product/product.html"):
    """Displays the whole manage/edit form for the product with the passed id.
    """
    # NOTE: For any reason the script from swfupload (see product/images.html)
    # calls this method (I have no idea how and why). It calls it without a
    # product id so we have to take care of it here as a workaround.
    if not product_id:
        return HttpResponse("")

    product = lfs_get_object_or_404(Product, pk=product_id)
    products = _get_filtered_products_for_product_view(request)
    paginator = Paginator(products, 20)
    page = paginator.page(request.REQUEST.get("page", 1))

    try:
        product = Product.objects.get(pk=product_id)
    except Exception:
        return HttpResponse("")
    return render_to_response(template_name, RequestContext(request, {
        "product": product,
        "product_filters": product_filters_inline(request, page, paginator, product_id),
        "pages_inline": pages_inline(request, page, paginator, product_id),
        "product_data": product_data_form(request, product_id),
        "images": manage_images(request, product_id, as_string=True),
        "selectable_products": selectable_products_inline(request, page, paginator, product.id),
        "seo": manage_seo(request, product_id),
        "stock": stock(request, product_id),
        "portlets": portlets_inline(request, product),
        "properties": manage_properties(request, product_id),
        "form": ProductSubTypeForm(instance=product),
        "name_filter_value": request.session.get("product_filters", {}).get("product_name", ""),
    }))


@permission_required("core.manage_shop", login_url="/login/")
def stock(request, product_id, template_name="manage/product/stock.html"):
    """Displays and updates product's stock data.
    """
    # prefix="stock" because <input name="length" doesn't seem to work with IE
    product = lfs_get_object_or_404(Product, pk=product_id)

    if request.method == "POST":
        form = ProductStockForm(prefix="stock", instance=product, data=request.POST)
        if form.is_valid():
            form.save()
            message = _(u"Product stock data has been saved.")
        else:
            message = _(u"Please correct the indicated errors.")
    else:
        form = ProductStockForm(prefix="stock", instance=product)

    result = render_to_string(template_name, RequestContext(request, {
        "product": product,
        "form": form
    }))

    html = [["#stock", result]]

    if request.is_ajax():
        result = simplejson.dumps({
            "html": html,
            "message": message,
            "init_date": True,
        }, cls=LazyEncoder)
        return HttpResponse(result)
    else:
        return result


@permission_required("core.manage_shop", login_url="/login/")
def product_data_form(request, product_id, template_name="manage/product/data.html"):
    """Displays the product master data form within the manage product view.
    """
    product = Product.objects.get(pk=product_id)

    if product.sub_type == VARIANT:
        form = VariantDataForm(instance=product)
    else:
        form = ProductDataForm(instance=product)

    return render_to_string(template_name, RequestContext(request, {
        "product": product,
        "form": form,
        "redirect_to": lfs.core.utils.get_redirect_for(product.get_absolute_url()),
    }))


@permission_required("core.manage_shop", login_url="/login/")
def products(request, template_name="manage/product/products.html"):
    """Displays an overview list of all products.
    """
    products = _get_filtered_products(request)
    paginator = Paginator(products, 20)
    page = paginator.page(request.REQUEST.get("page", 1))

    return render_to_response(template_name, RequestContext(request, {
        "products_inline": products_inline(request, page, paginator),
        "product_filters": product_filters_inline(request, page=page, paginator=paginator),
        "pages_inline": pages_inline(request, page, paginator, 0),
    }))


# Parts
@permission_required("core.manage_shop", login_url="/login/")
def products_inline(request, page, paginator, template_name="manage/product/products_inline.html"):
    """Displays the list of products.
    """
    return render_to_string(template_name, RequestContext(request, {
        "page": page,
        "paginator": paginator,
    }))


@permission_required("core.manage_shop", login_url="/login/")
def product_filters_inline(request, page, paginator, product_id=0, template_name="manage/product/product_filters_inline.html"):
    """
    """
    product_filters = request.session.get("product_filters", {})

    try:
        product_id = int(product_id)
    except TypeError:
        product_id = 0

    # amount options
    amount = product_filters.get("amount", "25")
    amount_options = []
    for value in ("10", "25", "50", "100"):
        amount_options.append({
            "value": value,
            "selected": value == amount
        })

    return render_to_string(template_name, RequestContext(request, {
        "amount_options": amount_options,
        "name": product_filters.get("name", ""),
        "price": product_filters.get("price", ""),
        "active": product_filters.get("active", ""),
        "for_sale": product_filters.get("for_sale", ""),
        "sub_type": product_filters.get("sub_type", ""),
        "page": page,
        "paginator": paginator,
        "product_id": product_id,
    }))


@permission_required("core.manage_shop", login_url="/login/")
def pages_inline(request, page, paginator, product_id, template_name="manage/product/pages_inline.html"):
    """Displays the page navigation.
    """
    return render_to_string(template_name, RequestContext(request, {
        "page": page,
        "paginator": paginator,
        "product_id" : product_id,
    }))


@permission_required("core.manage_shop", login_url="/login/")
def selectable_products_inline(request, page, paginator, product_id=0, template_name="manage/product/selectable_products_inline.html"):
    """Displays the selectable products for the product view. (Used to switch
    quickly from one product to another.)
    """
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return ""

    if product.is_variant():
        base_product = product.parent
    else:
        base_product = product

    return render_to_string(template_name, RequestContext(request, {
        "paginator": paginator,
        "page": page,
        "current_product": product,
        "base_product" : base_product,
    }))


# Actions
def add_product(request, template_name="manage/product/add_product.html"):
    """Shows a simplified product form and adds a new product.
    """
    if request.method == "POST":
        form = ProductAddForm(request.POST)
        if form.is_valid():
            new_product = form.save()
            url = reverse("lfs_manage_product", kwargs={"product_id": new_product.id})
            return HttpResponseRedirect(url)
    else:
        form = ProductAddForm()

    return render_to_response(template_name, RequestContext(request, {
        "form": form,
        "next": request.REQUEST.get("next", request.META.get("HTTP_REFERER")),
    }))


@permission_required("core.manage_shop", login_url="/login/")
def change_subtype(request, product_id):
    """Changes the sub type of the product with passed id.
    """
    product = Product.objects.get(pk=product_id)
    form = ProductSubTypeForm(instance=product, data=request.POST)
    form.save()

    return lfs.core.utils.set_message_cookie(
        url=reverse("lfs_manage_product", kwargs={"product_id": product_id}),
        msg=_(u"Sub type has been changed."),
    )


@require_POST
@permission_required("core.manage_shop", login_url="/login/")
def delete_product(request, product_id):
    """Deletes product with passed id.
    """
    product = lfs_get_object_or_404(Product, pk=product_id)
    product.delete()

    url = reverse("lfs_manage_product_dispatcher")
    return HttpResponseRedirect(url)


@require_POST
@permission_required("core.manage_shop", login_url="/login/")
def edit_product_data(request, product_id, template_name="manage/product/data.html"):
    """Edits the product with given.
    """
    product = lfs_get_object_or_404(Product, pk=product_id)
    products = _get_filtered_products_for_product_view(request)
    paginator = Paginator(products, 20)
    page = paginator.page(request.REQUEST.get("page", 1))

    if product.sub_type == VARIANT:
        form = VariantDataForm(instance=product, data=request.POST)
    else:
        form = ProductDataForm(instance=product, data=request.POST)

    if form.is_valid():
        form.save()
        if product.sub_type == VARIANT:
            form = VariantDataForm(instance=product)
        else:
            form = ProductDataForm(instance=product)

        message = _(u"Productdata has been saved.")
    else:
        message = _(u"Please correct the indicated errors.")

    form_html = render_to_string(template_name, RequestContext(request, {
        "product": product,
        "form": form,
        "redirect_to": lfs.core.utils.get_redirect_for(product.get_absolute_url()),
    }))

    html = [
        ["#selectable-products-inline", selectable_products_inline(request, page, paginator, product_id)],
        ["#data", form_html],
    ]

    result = simplejson.dumps({
        "html": html,
        "message": message,
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
def product_dispatcher(request):
    """Dispatches to the first product. This is called when the shop user clicks
    on the manage products link.
    """
    try:
        product = Product.objects.exclude(sub_type=VARIANT)[0]
        url = reverse("lfs_manage_product", kwargs={"product_id": product.id})
    except IndexError:
        url = reverse("lfs_manage_add_product")

    return HttpResponseRedirect(url)


@permission_required("core.manage_shop", login_url="/login/")
def reset_filters(request):
    """Resets all product filters.
    """
    if "product_filters" in request.session:
        del request.session["product_filters"]

    products = _get_filtered_products(request)
    paginator = Paginator(products, 20)
    page = paginator.page(request.REQUEST.get("page", 1))

    product_id = request.REQUEST.get("product-id", 0)
    html = (
        ("#product-filters", product_filters_inline(request, page, paginator, product_id)),
        ("#products-inline", products_inline(request, page, paginator)),
        ("#selectable-products-inline", selectable_products_inline(request, page, paginator, product_id)),
        ("#pages-inline", pages_inline(request, page, paginator, product_id)),
    )

    msg = _(u"Product filters have been reset")
    result = simplejson.dumps(
        {"html": html, "message": msg, }, cls=LazyEncoder)
    return HttpResponse(result)


@require_POST
@permission_required("core.manage_shop", login_url="/login/")
def save_products(request):
    """Saves products with passed ids (by request body).
    """
    products = _get_filtered_products(request)
    paginator = Paginator(products, 20)
    page = paginator.page(request.REQUEST.get("page", 1))

    if request.POST.get("action") == "delete":
        for key, value in request.POST.items():
            if key.startswith("delete-"):
                id = key.split("-")[1]

                try:
                    product = Product.objects.get(pk=id)
                except Product.DoesNotExist:
                    continue
                else:
                    product.delete()
        msg = _(u"Products have been deleted.")

    elif request.POST.get("action") == "save":
        for key, value in request.POST.items():
            if key.startswith("id-"):
                id = value

                try:
                    product = Product.objects.get(pk=id)
                except Product.DoesNotExist:
                    continue

                product.name = request.POST.get("name-%s" % id, "")
                product.sku = request.POST.get("sku-%s" % id, "")
                product.slug = request.POST.get("slug-%s" % id, "")
                product.sub_type = request.POST.get("sub_type-%s" % id, 0)

                try:
                    product.price = float(request.POST.get("price-%s" % id, 0))
                except ValueError:
                    product.price = 0
                try:
                    product.for_sale_price = \
                        float(request.POST.get("for_sale_price-%s" % id, 0))
                except ValueError:
                    product.for_sale_price = 0

                if request.POST.get("for_sale-%s" % id):
                    product.for_sale = True
                else:
                    product.for_sale = False

                if request.POST.get("active-%s" % id):
                    product.active = True
                else:
                    product.active = False

                try:
                    product.save()
                except IntegrityError:
                    pass

                msg = _(u"Products have been saved")

    html = (("#products-inline", products_inline(request, page, paginator)),)

    result = simplejson.dumps({
        "html": html,
        "message": msg,
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
def set_name_filter(request):
    """Sets product filters given by passed request.
    """
    product_filters = request.session.get("product_filters", {})

    if request.POST.get("name", "") != "":
        product_filters["product_name"] = request.POST.get("name")
    else:
        if product_filters.get("product_name"):
            del product_filters["product_name"]

    request.session["product_filters"] = product_filters

    products = _get_filtered_products_for_product_view(request)
    paginator = Paginator(products, 20)
    page = paginator.page(request.REQUEST.get("page", 1))

    product_id = request.REQUEST.get("product-id", 0)

    html = (
        ("#products-inline", products_inline(request, page, paginator)),
        ("#selectable-products-inline", selectable_products_inline(request, page, paginator, product_id)),
        ("#pages-inline", pages_inline(request, page, paginator, product_id)),
    )

    result = simplejson.dumps({
        "html": html,
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
def set_filters(request):
    """Sets product filters given by passed request.
    """
    product_filters = request.session.get("product_filters", {})
    for name in ("name", "active", "price", "category", "for_sale", "sub_type", "amount"):
        if request.POST.get(name, "") != "":
            product_filters[name] = request.POST.get(name)
        else:
            if product_filters.get(name):
                del product_filters[name]

    request.session["product_filters"] = product_filters

    try:
        amount = int(product_filters.get("amount", 25))
    except TypeError:
        amount = 25

    products = _get_filtered_products(request)
    paginator = Paginator(products, amount)
    page = paginator.page(request.REQUEST.get("page", 1))

    product_id = request.REQUEST.get("product-id", 0)
    html = (
        ("#product-filters", product_filters_inline(request, page, paginator, product_id)),
        ("#products-inline", products_inline(request, page, paginator)),
        ("#selectable-products-inline", selectable_products_inline(request, page, paginator, product_id)),
        ("#pages-inline", pages_inline(request, page, paginator, product_id)),
    )

    msg = _(u"Product filters have been set")

    result = simplejson.dumps({
        "html": html,
        "message": msg,
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
def set_products_page(request):
    """Sets the displayed product page.
    """
    product_id = request.GET.get("product-id")
    products = _get_filtered_products_for_product_view(request)
    paginator = Paginator(products, 20)
    page = paginator.page(request.REQUEST.get("page", 1))

    html = (
        ("#products-inline", products_inline(request, page, paginator)),
        ("#pages-inline", pages_inline(request, page, paginator, product_id)),
        ("#selectable-products-inline", selectable_products_inline(request, page, paginator, product_id)),
    )

    return HttpResponse(
        simplejson.dumps({"html": html}, cls=LazyEncoder))


@permission_required("core.manage_shop", login_url="/login/")
def product_by_id(request, product_id):
    """Little helper which returns a product by id. (For the shop customer the
    products are displayed by slug, for the manager by id).
    """
    product = Product.objects.get(pk=product_id)
    url = reverse("lfs.catalog.views.product_view", kwargs={"slug": product.slug})
    return HttpResponseRedirect(url)


def _get_filtered_products_for_product_view(request):
    """Returns a query set with filtered products based on saved name filter
    and ordering within the current session.
    """
    products = Product.objects.all()
    product_ordering = request.session.get("product-ordering", "id")
    product_ordering_order = request.session.get("product-ordering-order", "")

    # Filter
    product_filters = request.session.get("product_filters", {})
    name = product_filters.get("product_name", "")
    if name != "":
        products = products.filter(Q(name__icontains=name) | Q(sku__icontains=name))

    products = products.exclude(sub_type="2")
    products = products.order_by("%s%s" % (product_ordering_order, product_ordering))
    return products


def _get_filtered_products(request):
    """Returns a query set with filtered products based on saved filters and
    ordering within the current session.
    """
    products = Product.objects.all()
    product_filters = request.session.get("product_filters", {})
    product_ordering = request.session.get("product-ordering", "id")
    product_ordering_order = request.session.get("product-ordering-order", "")

    # Filter
    name = product_filters.get("name", "")
    if name != "":
        products = products.filter(Q(name__icontains=name) | Q(sku__icontains=name))

    active = product_filters.get("active", "")
    if active != "":
        products = products.filter(active=active)

    for_sale = product_filters.get("for_sale", "")
    if for_sale != "":
        products = products.filter(for_sale=for_sale)

    sub_type = product_filters.get("sub_type", "")
    if sub_type != "":
        products = products.filter(sub_type=sub_type)

    price = product_filters.get("price", "")
    if price.find("-") != -1:
        s, e = price.split("-")
        products = products.filter(price__range=(s, e))

    category = product_filters.get("category", "")
    if category == "None":
        products = products.filter(categories=None).distinct()
    elif category == "All":
        products = products.filter().distinct()
    elif category != "":
        category = lfs_get_object_or_404(Category, pk=category)
        categories = [category]
        categories.extend(category.get_all_children())
        products = products.filter(categories__in=categories).distinct()

    products = products.order_by("%s%s" % (product_ordering_order, product_ordering))

    return products
