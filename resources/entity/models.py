from django.db import models
from resources.server.models import Server


class Entity(models.Model):
    name = models.CharField(max_length=30, null=False, blank=False)
    discord_id = models.IntegerField(default=0, null=False, blank=False, db_index=True)
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name="entities")


