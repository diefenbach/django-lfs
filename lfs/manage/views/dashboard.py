# django imports
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render_to_response
from django.template import RequestContext


@permission_required("core.manage_shop", login_url="/login/")
def dashboard(request, template_name="manage/dashboard.html"):
    """
    """
    return render_to_response(template_name, RequestContext((request)))
