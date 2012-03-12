# python imports
from datetime import datetime
from datetime import timedelta

# django imports
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST

# lfs imports
import lfs.core.utils
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.utils import LazyEncoder

# review imports
from reviews.models import Review


# Views
@permission_required("core.manage_shop", login_url="/login/")
def review(request, review_id, template_name="manage/reviews/review.html"):
    """Displays review with provided review id.
    """
    review = lfs_get_object_or_404(Review, pk=review_id)

    return render_to_response(template_name, RequestContext(request, {
        "review_inline": review_inline(request, review_id),
        "review_filters_inline": review_filters_inline(request, review_id),
        "selectable_reviews_inline": selectable_reviews_inline(request, review_id),
        "review": review,
    }))


@permission_required("core.manage_shop", login_url="/login/")
def reviews(request, template_name="manage/reviews/reviews.html"):
    """Base view to display reviews overview.
    """
    return render_to_response(template_name, RequestContext(request, {
        "reviews_inline": reviews_inline(request),
        "reviews_filters_inline": reviews_filters_inline(request),
    }))


# Parts
def review_inline(request, review_id, template_name="manage/reviews/review_inline.html"):
    """Displays review with provided review id.
    """
    review_filters = request.session.get("review-filters", {})
    review = lfs_get_object_or_404(Review, pk=review_id)

    return render_to_string(template_name, RequestContext(request, {
        "review": review,
        "name": review_filters.get("name", ""),
        "active": review_filters.get("active", ""),
    }))


def reviews_inline(request, template_name="manage/reviews/reviews_inline.html"):
    """Renders the reviews section of the reviews overview view.
    """
    review_filters = request.session.get("review-filters", {})
    reviews = _get_filtered_reviews(request, review_filters)

    paginator = Paginator(reviews, 30)

    page = request.REQUEST.get("page", 1)
    page = paginator.page(page)

    return render_to_string(template_name, RequestContext(request, {
        "reviews": reviews,
        "page": page,
        "paginator": paginator,
        "start": review_filters.get("start", ""),
        "end": review_filters.get("end", ""),
        "active": review_filters.get("active", ""),
        "name": review_filters.get("name", ""),
        "ordering": request.session.get("review-ordering", "id"),
    }))


def review_filters_inline(request, review_id, template_name="manage/reviews/review_filters_inline.html"):
    """Renders the filter section of the review view.
    """
    review_filters = request.session.get("review-filters", {})
    review = lfs_get_object_or_404(Review, pk=review_id)

    return render_to_string(template_name, RequestContext(request, {
        "review": review,
        "name": review_filters.get("name", ""),
        "active": review_filters.get("active", ""),
    }))


def reviews_filters_inline(request, template_name="manage/reviews/reviews_filters_inline.html"):
    """Renders the reviews filters section of the reviews overview view.
    """
    review_filters = request.session.get("review-filters", {})
    reviews = _get_filtered_reviews(request, review_filters)

    paginator = Paginator(reviews, 30)

    page = request.REQUEST.get("page", 1)
    page = paginator.page(page)

    return render_to_string(template_name, RequestContext(request, {
        "page": page,
        "paginator": paginator,
        "start": review_filters.get("start", ""),
        "end": review_filters.get("end", ""),
        "active": review_filters.get("active", ""),
        "name": review_filters.get("name", ""),
    }))


def selectable_reviews_inline(request, review_id, template_name="manage/reviews/selectable_reviews_inline.html"):
    """Display selectable reviews.
    """
    review_filters = request.session.get("review-filters", {})
    reviews = _get_filtered_reviews(request, review_filters)

    paginator = Paginator(reviews, 30)

    try:
        page = int(request.REQUEST.get("page", 1))
    except TypeError:
        page = 1
    page = paginator.page(page)

    return render_to_string(template_name, RequestContext(request, {
        "paginator": paginator,
        "page": page,
        "review_id": int(review_id),
    }))


# Actions
@permission_required("core.manage_shop", login_url="/login/")
def set_reviews_page(request):
    """Sets the page for the reviews overview view.
    """
    result = simplejson.dumps({
        "html": (
            ("#reviews-inline", reviews_inline(request)),
            ("#reviews-filters-inline", reviews_filters_inline(request)),
        ),
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
def set_selectable_reviews_page(request):
    """Sets the page of selectable reviews.
    """
    review_id = request.GET.get("review-id", 1)

    html = (
        ("#selectable-reviews", selectable_reviews_inline(request, review_id)),
        ("#selectable-reviews-inline", selectable_reviews_inline(request, review_id)),
    )

    result = simplejson.dumps({
        "html": html,
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
def set_ordering(request, ordering):
    """Sets review ordering given by passed request.
    """
    request.session["review-ordering"] = ordering

    if ordering == request.session.get("review-ordering"):
        if request.session.get("review-ordering-order", "") == "":
            request.session["review-ordering-order"] = "-"
        else:
            request.session["review-ordering-order"] = ""
    else:
        request.session["review-ordering-order"] = ""

    if request.REQUEST.get("came-from") == "review":
        review_id = request.REQUEST.get("review-id")
        html = (
            ("#selectable-reviews-inline", selectable_reviews_inline(request, review_id)),
            ("#review-inline", review_inline(request, review_id)),
        )
    else:
        html = (("#reviews-inline", reviews_inline(request)),)

    result = simplejson.dumps({
        "html": html,
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
def set_review_filters(request):
    """Sets review filters given by passed request.
    """
    review_filters = request.session.get("review-filters", {})

    if request.POST.get("name", "") != "":
        review_filters["name"] = request.POST.get("name")
    else:
        if review_filters.get("name"):
            del review_filters["name"]

    if request.POST.get("active", "") != "":
        review_filters["active"] = request.POST.get("active")
    else:
        if review_filters.get("active"):
            del review_filters["active"]

    request.session["review-filters"] = review_filters

    if request.REQUEST.get("came-from") == "review":
        review_id = request.REQUEST.get("review-id")
        html = (
            ("#selectable-reviews-inline", selectable_reviews_inline(request, review_id)),
            ("#review-inline", review_inline(request, review_id)),
        )
    else:
        html = (
            ("#reviews-inline", reviews_inline(request)),
            ("#reviews-filters-inline", reviews_filters_inline(request)),
        )

    msg = _(u"Review filters have been set")

    result = simplejson.dumps({
        "html": html,
        "message": msg,
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
def reset_review_filters(request):
    """Resets all review filters.
    """
    if "review-filters" in request.session:
        del request.session["review-filters"]

    if request.REQUEST.get("came-from") == "review":
        review_id = request.REQUEST.get("review-id")
        html = (
            ("#selectable-reviews-inline", selectable_reviews_inline(request, review_id)),
            ("#review-inline", review_inline(request, review_id)),
            ("#review-filters-inline", review_filters_inline(request, review_id)),
        )
    else:
        html = (
            ("#reviews-inline", reviews_inline(request)),
            ("#reviews-filters-inline", reviews_filters_inline(request)),
        )

    msg = _(u"Review filters have been reset")

    result = simplejson.dumps({
        "html": html,
        "message": msg,
    }, cls=LazyEncoder)

    return HttpResponse(result)


@permission_required("core.manage_shop", login_url="/login/")
@require_POST
def delete_review(request, review_id):
    """Deletes review with passed review id.
    """
    try:
        review = Review.objects.get(pk=review_id)
    except Review.DoesNotExist:
        pass
    else:
        review.delete()

    try:
        ordering = "%s%s" % (request.session.get("review-ordering-order", "id"), request.session.get("review-ordering", "id"))
        review = Review.objects.all().order_by(ordering)[0]
    except IndexError:
        url = reverse("lfs_manage_reviews")
    else:
        url = reverse("lfs_manage_review", kwargs={"review_id": review.id})

    return lfs.core.utils.set_message_cookie(url, _(u"Review has been deleted."))


@permission_required("core.manage_shop", login_url="/login/")
def set_review_state(request, review_id):
    """Sets the state for given review.
    """
    try:
        review = Review.objects.get(pk=review_id)
    except Review.DoesNotExist:
        pass
    else:
        review.active = int(request.POST.get("active"))
        review.save()

    html = (
        ("#selectable-reviews-inline", selectable_reviews_inline(request, review_id)),
        ("#review-inline", review_inline(request, review_id)),
    )

    msg = _(u"Review state has been set")

    result = simplejson.dumps({
        "html": html,
        "message": msg,
    }, cls=LazyEncoder)

    return HttpResponse(result)


# Private Methods
def _get_filtered_reviews(request, review_filters):
    """
    """
    reviews = Review.objects.all()
    review_ordering = request.session.get("review-ordering", "id")
    review_ordering_order = request.session.get("review-ordering-order", "")

    # Filter
    name = review_filters.get("name", "")
    if name != "":
        reviews = reviews.filter(user_name__icontains=name)

    active = review_filters.get("active", "")
    if active != "":
        reviews = reviews.filter(active=active)

    # Ordering
    if review_ordering == "product":
        reviews = list(reviews)
        if review_ordering_order == "-":
            reviews.sort(lambda b, a: cmp(a.content.get_name(), b.content.get_name()))
        else:
            reviews.sort(lambda a, b: cmp(a.content.get_name(), b.content.get_name()))

    else:
        reviews = reviews.order_by("%s%s" % (review_ordering_order, review_ordering))

    return reviews
