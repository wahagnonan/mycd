from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'backends.core'

    def ready(self):
        import backends.core.signals
