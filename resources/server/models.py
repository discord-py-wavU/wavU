# Django Imports
from django.db import models


class Server(models.Model):
    discord_id = models.BigIntegerField(default=0, null=False, blank=False, db_index=True)
    enabled = models.BooleanField(default=True)
