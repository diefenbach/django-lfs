# lfs imports
from lfs.criteria.models.criteria_objects import CriteriaObjects
from lfs.criteria.models.criteria import CountryCriterion
from lfs.criteria.models.criteria import CombinedLengthAndGirthCriterion
from lfs.criteria.models.criteria import CartPriceCriterion
from lfs.criteria.models.criteria import DistanceCriterion
from lfs.criteria.models.criteria import HeightCriterion
from lfs.criteria.models.criteria import LengthCriterion
from lfs.criteria.models.criteria import PaymentMethodCriterion
from lfs.criteria.models.criteria import ShippingMethodCriterion
from lfs.criteria.models.criteria import UserCriterion
from lfs.criteria.models.criteria import WidthCriterion
from lfs.criteria.models.criteria import WeightCriterion


def is_valid(request, object, product=None):
    """Returns True if the given object is valid. This is calculated via the
    attached criteria.

    Passed object is an object which can have criteria. At the momemnt are are
    shipping or payment methods.
    """
    for criterion_object in object.criteria_objects.all():
        if criterion_object.criterion.is_valid(request, product) == False:
            return False
    return True


def get_first_valid(request, objects, product=None):
    """Returns the first valid object of given objects.

    Passed objects are objects which can have criteria. At the momemnt these are
    shipping or payment methods.
    """
    for object in objects:
        if is_valid(request, object, product):
            return object
    return None


def save_criteria(request, object):
    """Saves the criteria for the given object. The criteria are passed via
    request body.
    """
    # First we delete all existing criteria objects for the given object.
    for co in object.criteria_objects.all():
        co.criterion.delete()
        co.delete()

    # Then we add all passed criteria to the shipping method.
    for key, type_ in request.POST.items():
        if key.startswith("type"):
            try:
                id = key.split("-")[1]
            except KeyError:
                continue

            # Get the operator and value for the calculated id
            operator = request.POST.get("operator-%s" % id)
            value = request.POST.get("value-%s" % id)

            if type_ == "country":
                value = request.POST.getlist("value-%s" % id)
                c = CountryCriterion.objects.create(operator=operator)
                c.countries = value
                c.save()
            elif type_ == "payment_method":
                value = request.POST.getlist("value-%s" % id)
                c = PaymentMethodCriterion.objects.create(operator=operator)
                c.payment_methods = value
                c.save()
            elif type_ == "shipping_method":
                value = request.POST.getlist("value-%s" % id)
                c = ShippingMethodCriterion.objects.create(operator=operator)
                c.shipping_methods = value
                c.save()
            elif type_ == "combinedlengthandgirth":
                try:
                    value = float(value)
                except (TypeError, ValueError):
                    value = 0.0
                c = CombinedLengthAndGirthCriterion.objects.create(operator=operator, clag=value)
            elif type_ == "price":
                try:
                    value = float(value)
                except (TypeError, ValueError):
                    value = 0.0
                c = CartPriceCriterion.objects.create(operator=operator, price=value)
            elif type_ == "height":
                try:
                    value = float(value)
                except (TypeError, ValueError):
                    value = 0.0
                c = HeightCriterion.objects.create(operator=operator, height=value)
            elif type_ == "length":
                try:
                    value = float(value)
                except (TypeError, ValueError):
                    value = 0.0
                c = LengthCriterion.objects.create(operator=operator, length=value)
            elif type_ == "width":
                try:
                    value = float(value)
                except (TypeError, ValueError):
                    value = 0.0
                c = WidthCriterion.objects.create(operator=operator, width=value)
            elif type_ == "weight":
                try:
                    value = float(value)
                except (TypeError, ValueError):
                    value = 0.0
                c = WeightCriterion.objects.create(operator=operator, weight=value)
            elif type_ == "user":
                c = UserCriterion.objects.create(operator=operator)
            elif type_ == "distance":
                try:
                    value = float(value)
                except (TypeError, ValueError):
                    value = 0.0
                c = DistanceCriterion.objects.create(operator=operator, distance=value)

            position = request.POST.get("position-%s" % id)
            CriteriaObjects.objects.create(content=object, criterion=c, position=position)
