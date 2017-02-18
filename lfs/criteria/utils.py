from django.contrib.contenttypes.models import ContentType

from lfs.core.utils import import_symbol
from lfs.criteria.models import Criterion

import logging
logger = logging.getLogger(__name__)


# DEPRECATED 0.8
def is_valid(request, object, product=None):
    """
    Returns True if the given object is valid. This is calculated via the
    attached criteria.

    Passed object is an object which can have criteria. At the moment these are
    discounts, shipping/payment methods and shipping/payment prices.
    """
    logger.info("Decprecated: lfs.criteria.utils.is_valid: this function is deprecated. Please use the Criteria class instead.")
    for criterion_object in get_criteria(object):
        criterion_object.request = request
        criterion_object.product = product
        if criterion_object.is_valid() is False:
            return False
    return True


# DEPRECATED 0.8
def get_criteria(object):
    """
    Returns all criteria for given object.
    """
    logger.info("Decprecated: lfs.criteria.utils.get_criteria: this function is deprecated. Please use the Criteria class instead.")
    content_type = ContentType.objects.get_for_model(object)

    criteria = []
    for criterion in Criterion.objects.filter(content_id=object.id, content_type=content_type):
        criteria.append(criterion.get_content_object())
    return criteria


def get_first_valid(request, objects, product=None):
    """
    Returns the first valid object of given objects.

    Passed object is an object which can have criteria. At the moment these are
    discounts, shipping/payment methods and shipping/payment prices.
    """
    for object in objects:
        if object.is_valid(request, product):
            return object
    return None


# DEPRECATED 0.8
def save_criteria(request, object):
    """
    Saves the criteria for the given object. The criteria are passed via
    request body.
    """
    logger.info("Decprecated: lfs.criteria.utils.save_criteria: this function is deprecated. Please use the Criteria class instead.")
    # First we delete all existing criteria objects for the given object.
    for co in get_criteria(object):
        co.delete()

    # Then we add all passed criteria to the object.
    for key, model in request.POST.items():
        if key.startswith("type"):
            try:
                id = key.split("-")[1]
            except KeyError:
                continue

            # Get the values for the criterion
            operator = request.POST.get("operator-%s" % id)
            position = request.POST.get("position-%s" % id)

            criterion_class = import_symbol(model)
            criterion = criterion_class.objects.create(content=object, operator=operator, position=position)

            if criterion.get_value_type() == criterion.MULTIPLE_SELECT:
                value = request.POST.getlist("value-%s" % id)
            else:
                value = request.POST.get("value-%s" % id)

            criterion.update(value)
