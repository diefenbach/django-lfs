# -*- coding: utf-8 -*-

# python imports
import re

# django imports
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

# lfs imports
from lfs.catalog.models import Product
from lfs.tagging import utils as tagging_utils
from lfs.tagging.settings import RE_STOP_WORDS
from lfs.tagging.settings import RE_SEPARATORS



@permission_required("core.manage_shop")
def tag_products(request, source="description"):
    """Auto tags product on base of product description.
    """
    if source == "description":
        parser = tagging_utils.SimpleHTMLParser()
        for product in Product.objects.all():
            parser.feed(product.description)
            product.tags.clear()

            data, amount = re.subn(r"[\W]*", "", parser.data)
            tags = re.split("\s*", data)
            for tag in tags:
                if tag:
                    product.tags.add(tag)

    elif source == "name":
        for product in Product.objects.all():
            product.tags.clear()

            data, amount = RE_STOP_WORDS.subn("", product.name)
            data, amount = RE_SEPARATORS.subn(" ", data)

            tags = re.split("\s*", data)

            for tag in tags:
                if tag:
                    product.tags.add(tag)

        return HttpResponse("")


def tagged_object_list(request, tag):
    product_list = Product.objects.filter(tags__name__in=[tag])
    c = RequestContext(request, {
        "tag": tag,
        "product_list": product_list,
    })
    return render_to_response('tagging/product_list.html', c)

