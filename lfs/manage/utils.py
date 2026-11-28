from datetime import date, datetime, time, timedelta

from django.utils import timezone

from lfs.catalog.models import Category


def day_range(start: date | None, end: date | None) -> tuple[datetime | None, datetime | None]:
    """Turn the calendar days ``start`` and ``end`` of a date filter into aware datetimes in the shop's time zone.

    Returns the start of ``start`` and the start of the day after ``end``, so that ``>= start`` and ``< end``
    include both days completely. A missing day gives ``None``.
    """
    start_dt = timezone.make_aware(datetime.combine(start, time.min)) if start else None
    end_dt = timezone.make_aware(datetime.combine(end + timedelta(days=1), time.min)) if end else None
    return start_dt, end_dt


def get_current_page(request, objs, obj, amount):
    """Returns the current page of obj within objs."""
    try:
        page = int((request.POST if request.method == "POST" else request.GET).get("page"))
    except TypeError:
        try:
            idx = tuple(objs).index(obj)
        except ValueError:
            page = 1
        else:
            page = int(idx / amount) + 1

    return page


def cartesian_product(*seqin):
    """Calculates the cartesian product of given lists."""

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
    """Updates the position of the children of the passed category."""
    for i, child in enumerate(Category.objects.filter(parent=category)):
        child.position = (i + 1) * 10
        child.save()
