from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.base import TemplateView

from lfs import __version__ as lfs_version
from lfs.core.utils import import_symbol


class EnvironmentView(PermissionRequiredMixin, TemplateView):
    """Displays miscellaneous information about the environment."""

    template_name = "manage/information/environment.html"
    permission_required = "core.manage_shop"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        apps = []
        for app in settings.INSTALLED_APPS:
            if app in ["lfs"] or app.startswith("lfs.") or app.startswith("django."):
                continue

            try:
                version = import_symbol("%s.__version__" % app)
            except AttributeError:
                version = "N/A"

            apps.append(
                {
                    "name": app,
                    "version": version,
                }
            )

        apps.sort(key=lambda k: k["name"])

        context.update(
            {
                "lfs_version": lfs_version,
                "apps": apps,
            }
        )

        return context
