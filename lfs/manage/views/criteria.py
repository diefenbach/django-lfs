# django imports
from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse

# lfs imports
from lfs.core.utils import import_symbol


@permission_required("core.manage_shop")
def add_criterion(request):
    """
    Adds a new criterion form.
    """
    try:
        default_criterion = settings.LFS_CRITERIA[0]
        default_criterion = import_symbol(default_criterion[0])
        result = default_criterion().render(request, 10)
    except:
        result = ""

    default_criterion = settings.LFS_CRITERIA[0]
    default_criterion = import_symbol(default_criterion[0])
    result = default_criterion().render(request, 10)

    return HttpResponse(result)


@permission_required("core.manage_shop")
def change_criterion_form(request):
    """
    Changes the changed criterion form to the given type (via request body)
    form.

    This is called via an AJAX request. The result is injected into the right
    DOM node.
    """
    type = request.POST.get("type", "price")
    criterion = import_symbol(type)

    # create dummy criterion
    result = criterion(pk=1).render(request, 10)
    return HttpResponse(result)
