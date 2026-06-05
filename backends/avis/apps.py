from django.apps import AppConfig


class AvisConfig(AppConfig):
    name = "backends.avis"

    def ready(self):
        import backends.avis.signals
