from django.apps import AppConfig


class LfsCachingAppConfig(AppConfig):
    name = 'lfs.caching'

    def ready(self):
        import listeners  # NOQA
