import json

# django imports
from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render_to_response
from django.template import RequestContext

# lfs imports
from lfs.core.utils import import_symbol

# versions
from lfs import __version__ as lfs_version
from lfs_theme import __version__ as lfs_theme_version

@permission_required("core.manage_shop")
def environment(request, template_name="manage/information/environment.html"):
    """Displays miscellaneous information about the evnironment.
    """
    apps = []
    for app in settings.INSTALLED_APPS:
        if app in ["lfs"] or \
           app.startswith("lfs.") or \
           app.startswith("django."):
            continue

        try:
            version = import_symbol("%s.__version__" % app)
        except AttributeError:
            version = "N/A"

        apps.append({
            "name": app,
            "version": version,
        })

    apps.sort(lambda a, b: cmp(a["name"], b["name"]))

    return render_to_response(template_name, RequestContext(request, {
        "lfs_version": lfs_version,
        "lfs_theme_version": lfs_theme_version,
        "apps": apps,
    }))
