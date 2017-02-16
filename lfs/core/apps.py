from django.apps import AppConfig


class LfsCoreAppConfig(AppConfig):
    name = 'lfs.core'

    def ready(self):
        import listeners
        from . import views
        views.one_time_setup()
