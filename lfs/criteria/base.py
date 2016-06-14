# django imports
from django.contrib.contenttypes.models import ContentType

# lfs imports
from django.core.cache import cache
from lfs.core.utils import import_symbol


class Criteria(object):
    """
    Base class for objects which have criteria.
    """
    def is_valid(self, request, product=None):
        """
        Returns ``True`` if the object is valid, otherwise ``False``.
        """
        for criterion in self.get_criteria():
            criterion.request = request
            criterion.product = product
            if not criterion.is_valid():
                return False
        return True

    def get_criteria(self):
        """
        Returns all criteria of the object.
        """
        content_type = ContentType.objects.get_for_model(self)
        cache_key = u'criteria_for_model_{}_{}'.format(self.pk, content_type.pk)
        criteria = cache.get(cache_key, None)
        if criteria is None:
            criteria = []
            from lfs.criteria.models import Criterion
            for criterion in Criterion.objects.filter(content_id=self.pk, content_type=content_type):
                criteria.append(criterion.get_content_object())
            cache.set(cache_key, criteria)
        return criteria

    def save_criteria(self, request):
        """
        Saves all passed criteria (via request.POST) to the object.
        """
        # First we delete all existing criteria objects for the given object.
        for co in self.get_criteria():
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
                criterion = criterion_class.objects.create(content=self, operator=operator, position=position)

                if criterion.get_value_type() == criterion.MULTIPLE_SELECT:
                    value = request.POST.getlist("value-%s" % id)
                else:
                    value = request.POST.get("value-%s" % id)

                criterion.update(value)

        content_type = ContentType.objects.get_for_model(self)
        cache_key = u'criteria_for_model_{}_{}'.format(self.pk, content_type.pk)
        cache.delete(cache_key)
