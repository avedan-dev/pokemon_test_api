from django.db import models
from django.contrib.postgres.fields import ArrayField


class User(models.Model):
    user_id = models.IntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=128)
    pokemons = ArrayField(models.CharField(max_length=128), null=True)
