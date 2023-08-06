# -*- coding: utf-8 -*-

from django.apps import AppConfig


class EntityConfig(AppConfig):
    name = "resources.entity"

    def ready(self):
        import resources.entity.signals
