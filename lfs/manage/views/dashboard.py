# django imports
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render


@permission_required("core.manage_shop")
def dashboard(request, template_name="manage/dashboard.html"):
    """
    """
    return render(request, template_name, {})
