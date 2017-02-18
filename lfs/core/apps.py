from django.apps import AppConfig


class LfsCoreAppConfig(AppConfig):
    name = 'lfs.core'

    def ready(self):
        import listeners  # NOQA
        from . import views
        views.one_time_setup()
