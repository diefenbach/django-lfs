# django imports
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext
from django.template.loader import render_to_string

# lfs imports
from lfs.catalog.models import Category
from lfs.catalog.models import Product


def cartesian_product(*seqin):
    """Calculates the cartesian product of given lists.
    """
    # Found in ASPN Cookbook
    def rloop(seqin, comb):
        if seqin:
            for item in seqin[0]:
                newcomb = comb + [item]
                for item in rloop(seqin[1:], newcomb):
                    yield item
        else:
            yield comb

    return rloop(seqin, [])

if __name__ == "__main__":
    for x in cartesian_product([u'5|11', u'7|15', u'6|12']):
        print x


def update_category_positions(category):
    """Updates the position of the children of the passed category.
    """
    for i, child in enumerate(Category.objects.filter(parent=category)):
        child.position = (i + 1) * 10
        child.save()
