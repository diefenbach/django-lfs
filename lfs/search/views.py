# django imports
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson

# lfs imports
from lfs.catalog.models import Category
from lfs.catalog.models import Product
from lfs.catalog.settings import STANDARD_PRODUCT, PRODUCT_WITH_VARIANTS, VARIANT

def livesearch(request, template_name="lfs/search/livesearch_results.html"):
    """
    """
    phrase = request.GET.get("phrase", "")

    if phrase == "":
        result = simplejson.dumps({
            "state" : "failure",
        })
    else:
        # Products
        query = Q(active=True) & \
                Q(name__icontains=phrase) & \
                Q(sub_type__in = (STANDARD_PRODUCT, PRODUCT_WITH_VARIANTS))
        
        temp = Product.objects.filter(query)
        total = len(temp)
        products = temp[0:5]
        
        products = render_to_string(template_name, RequestContext(request, {
            "products" : products,
            "phrase" : phrase,
            "total" : total,
        }))
        
        result = simplejson.dumps({
            "state" : "success",
            "products" : products,
        })
    return HttpResponse(result)
    
def search(request, template_name="lfs/search/search_results.html"):
    """Returns the search result according to given phrase (via get request) 
    ordered by the globally set sorting.
    """
    phrase = request.GET.get("phrase", "")
    
    # Products
    query = Q(active=True) & \
            Q(name__icontains=phrase) & \
            Q(sub_type__in = (STANDARD_PRODUCT, PRODUCT_WITH_VARIANTS))
    products = Product.objects.filter(query)

    # Sorting
    sorting = request.session.get("sorting")    
    if sorting: 
        products = products.order_by(sorting)
        
    total = 0
    if products:
        total += len(products)
        
    return render_to_response(template_name, RequestContext(request, {
        "products" : products,
        "phrase" : phrase,
        "total" : total,
    }))