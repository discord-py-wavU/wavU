from django.apps import AppConfig


class ServerConfig(AppConfig):
    name = "resources.server"

    def ready(self):
        import resources.server.signals