from django.db import models


class Entity(models.Model):
    name = models.CharField(max_length=30)
    discord_id = models.IntegerField(default=0)



