from django.apps import AppConfig


class AudioConfig(AppConfig):
    name = "resources.audio"

    def ready(self):
        import resources.audio.signals
