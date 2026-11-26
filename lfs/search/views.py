import json

from django.apps import apps
from django.core.paginator import EmptyPage
from django.core.paginator import InvalidPage
from django.core.paginator import Paginator
from django.urls import reverse
from django.db import connection
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.translation import ngettext

import lfs.catalog.utils
from lfs.catalog.models import Product
from lfs.core.utils import lfs_pagination

SEARCH_FIELDS = ("name", "short_description", "description", "manufacturer__name", "sku_manufacturer")


def product_search_query(q: str) -> Q:
    """Return the filter for active products whose text fields contain ``q``, ignoring case.

    On PostgreSQL with django.contrib.postgres accents are ignored too (unaccent); other databases have no unaccent.
    """
    if connection.vendor == "postgresql" and apps.is_installed("django.contrib.postgres"):
        lookup = "unaccent__icontains"
    else:
        lookup = "icontains"
    matches = Q()
    for field in SEARCH_FIELDS:
        matches |= Q(**{f"{field}__{lookup}": q})
    return Q(active=True) & matches


def livesearch(request, template_name="lfs/search/livesearch_results.html"):
    """ """
    q = request.GET.get("q", "")

    if q == "":
        result = json.dumps(
            {
                "state": "failure",
            }
        )
    else:
        # Products
        temp = Product.objects.filter(product_search_query(q))
        total = temp.count()
        products = temp[0:5]

        products = render_to_string(
            template_name,
            request=request,
            context={
                "products": products,
                "q": q,
                "total": total,
            },
        )

        result = json.dumps(
            {
                "state": "success",
                "products": products,
            }
        )
    return HttpResponse(result, content_type="application/json")


def search(request, template_name="lfs/search/search_results.html"):
    """Returns the search result according to given query (via get request)
    ordered by the globally set sorting.
    """
    q = request.GET.get("q", "")

    if q == "":
        return render(
            request,
            template_name,
            {
                "q": q,
                "total": 0,
                "item_list_tracking": None,
            },
        )

    start = request.GET.get("start", 1)

    # Products
    products = Product.objects.filter(product_search_query(q))
    amount_of_products = products.count()

    # Sorting
    sorting = request.session.get("sorting")
    if sorting:
        products = products.order_by(sorting)

    # prepare paginator
    paginator = Paginator(products, 10)

    try:
        current_page = paginator.page(start)
    except (EmptyPage, InvalidPage):
        current_page = paginator.page(paginator.num_pages)

    # Calculate urls
    pagination_data = lfs_pagination(request, current_page, url=reverse("lfs_search"))
    pagination_data["total_text"] = ngettext("%(count)d product", "%(count)d products", amount_of_products) % {
        "count": amount_of_products
    }

    tracking_products = [
        lfs.catalog.utils.resolve_product_for_search_list(request, product)
        for product in current_page.object_list
    ]
    item_list_tracking = lfs.catalog.utils.item_list_to_tracking_snapshot(
        request,
        tracking_products,
        list_id="search",
        list_name=q,
    )

    return render(
        request,
        template_name,
        {
            "products": current_page,
            "pagination": pagination_data,
            "q": q,
            "total": products.count(),
            "item_list_tracking": item_list_tracking,
        },
    )
