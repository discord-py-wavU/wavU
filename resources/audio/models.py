from django.db import models
from resources.server.models import Server
from resources.entity.models import Entity

from django.utils import timezone


class Audio(models.Model):
    hashcode = models.CharField(blank=False, null=False, max_length=30, db_index=True)
    created_at = models.DateField(blank=False, null=False, default=timezone.now())


class AudioInEntity(models.Model):
    audio = models.ForeignKey(Audio, on_delete=models.CASCADE, related_name="entities")
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name="audios")
    enabled = models.BooleanField(default=True)
    name = models.CharField(default="", max_length=20, db_index=True)


class AudioInServer(models.Model):
    audio = models.ForeignKey(Audio, on_delete=models.CASCADE, related_name="servers")
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name="audios")
    enabled = models.BooleanField(default=True)
    name = models.CharField(default="", max_length=20, db_index=True)
