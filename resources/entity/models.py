# Django imports
from django.db import models
# Project imports
from resources.server.models import Server


class Entity(models.Model):
    name = models.CharField(max_length=30, null=False, blank=False)
    discord_id = models.BigIntegerField(default=0, null=False, blank=False, db_index=True)
    server = models.ForeignKey(Server, on_delete=models.SET_NULL, related_name="entities", null=True)
    created_at = models.DateField(auto_now_add=True, null=False, blank=False)
