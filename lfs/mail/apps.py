from django.apps import AppConfig


class LfsMailAppConfig(AppConfig):
    name = "lfs.mail"

    def ready(self):
        from . import listeners  # NOQA
