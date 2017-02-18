from django.apps import AppConfig


class LfsCatalogAppConfig(AppConfig):
    name = 'lfs.catalog'

    def ready(self):
        import listeners  # NOQA
