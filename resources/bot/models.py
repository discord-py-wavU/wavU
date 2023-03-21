from django.db import models

class Bot(models.Model):
    token = models.CharField(max_length=10)
