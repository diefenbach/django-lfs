import json

from django.core.paginator import EmptyPage
from django.core.paginator import InvalidPage
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.translation import ungettext

from lfs.catalog.models import Product
from lfs.core.utils import lfs_pagination


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
    start = request.GET.get("start", 1)

    # Products
    query = Q(active=True) & (
        Q(name__icontains=q) |
        Q(manufacturer__name__icontains=q) |
        Q(sku_manufacturer__icontains=q)
    )

    products = Product.objects.filter(query)
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
    pagination_data = lfs_pagination(request, current_page, url=reverse('lfs_search'))
    pagination_data['total_text'] = ungettext('%(count)d product',
                                              '%(count)d products',
                                              amount_of_products) % {'count': amount_of_products}

    return render(request, template_name, {
        "products": current_page,
        "pagination": pagination_data,
        "q": q,
        "total": products.count(),
    })
