import json

# django imports
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string

# lfs imports
from lfs.catalog.models import Product


def livesearch(request, template_name="lfs/search/livesearch_results.html"):
    """
    """
    q = request.GET.get("q", "")

    if q == "":
        result = json.dumps({
            "state": "failure",
        })
    else:
        # Products
        query = Q(active=True) & (
            Q(name__icontains=q) |
            Q(manufacturer__name__icontains=q) |
            Q(sku_manufacturer__icontains=q)
        )

        temp = Product.objects.filter(query)
        total = temp.count()
        products = temp[0:5]

        products = render_to_string(template_name, request=request, context={
            "products": products,
            "q": q,
            "total": total,
        })

        result = json.dumps({
            "state": "success",
            "products": products,
        })
    return HttpResponse(result, content_type='application/json')


def search(request, template_name="lfs/search/search_results.html"):
    """Returns the search result according to given query (via get request)
    ordered by the globally set sorting.
    """
    q = request.GET.get("q", "")

    # Products
    query = Q(active=True) & (
        Q(name__icontains=q) |
        Q(manufacturer__name__icontains=q) |
        Q(sku_manufacturer__icontains=q)
    )

    products = Product.objects.filter(query)

    # Sorting
    sorting = request.session.get("sorting")
    if sorting:
        products = products.order_by(sorting)

    total = products.count()

    return render(request, template_name, {
        "products": products,
        "q": q,
        "total": total,
    })
