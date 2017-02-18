from lfs.catalog.models import Category


def get_current_page(request, objs, obj, amount):
    """Returns the current page of obj within objs.
    """
    try:
        page = int((request.POST if request.method == 'POST' else request.GET).get("page"))
    except TypeError:
        try:
            idx = tuple(objs).index(obj)
        except ValueError:
            page = 1
        else:
            page = int(idx / amount) + 1

    return page


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


def update_category_positions(category):
    """Updates the position of the children of the passed category.
    """
    for i, child in enumerate(Category.objects.filter(parent=category)):
        child.position = (i + 1) * 10
        child.save()
