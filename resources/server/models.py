from django.db import models


class Server(models.Model):
    discord_id = models.IntegerField(default=0)
    enabled = models.BooleanField(default=True)
