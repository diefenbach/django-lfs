# django imports
import re
from django.db.models import Q
from django.core.exceptions import FieldError
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson

# lfs imports
from lfs.catalog.models import Category
from lfs.catalog.models import Product
#from lfs.catalog.settings import STANDARD_PRODUCT, PRODUCT_WITH_VARIANTS, VARIANT
from lfs.search.models import SearchNotFound

def livesearch(request, template_name="lfs/search/livesearch_results.html"):
    """
    """
    q = request.GET.get("q", "")

    if q == "":
        result = simplejson.dumps({
            "state": "failure",
        })
    else:
        # Products
        query = Q(active=True) & get_query(q, ['name', 'description'])
	    temp = Product.objects.filter(query)
        if not temp:
	        # Creates a SearchNotFound for the current session and/or user.
            if request.session.session_key is None:
                request.session.save()
            searchnotfound = SearchNotFound(session=request.session.session_key)
            if request.user.is_authenticated():
        	    searchnotfound.user = request.user
		    searchnotfound.query = q[0:99]
            searchnotfound.save()

        total = temp.count()
        products = temp[0:5]

        products = render_to_string(template_name, RequestContext(request, {
            "products": products,
            "q": q,
            "total": total,
        }))

        result = simplejson.dumps({
            "state": "success",
            "products": products,
        })
    return HttpResponse(result, mimetype='application/json')


def search(request, template_name="lfs/search/search_results.html"):
    """Returns the search result according to given query (via get request)
    ordered by the globally set sorting.
    """
    q = request.GET.get("q", "")

    # Products
    # TODO add a view in manage to select the attributs of Product modele : manufacturer__name, sku_manufacturer, ...
    query = Q(active=True) & get_query(q, ['name', 'description'])
    products = Product.objects.filter(query)
    if not products:
	    # Creates a SearchNotFound for the current session and/or user.
        if request.session.session_key is None:
            request.session.save()
        searchnotfound = SearchNotFound(session=request.session.session_key)
        if request.user.is_authenticated():
        	searchnotfound.user = request.user
	    searchnotfound.query = q
        searchnotfound.save()

    # Sorting
    sorting = request.session.get("sorting")
    if sorting:
        products = products.order_by(sorting)

    total = products.count()

    return render_to_response(template_name, RequestContext(request, {
        "products": products,
        "q": q,
        "total": total,
    }))

def normalize_query(query_string,
                    findterms=re.compile(ur'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)] 

def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.    
    '''
    query = None # Query to search for every search term        
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query
