from django.db import models
from django.contrib.postgres.fields import ArrayField


class Courier(models.Model):
    courier_id = models.IntegerField(unique=True, primary_key=True)
    COURIER_TYPES = (
        ("foot", "foot"),
        ("bike", "bike"),
        ("car", "car"),
    )
    courier_type = models.CharField(max_length=128, choices=COURIER_TYPES)
    regions = ArrayField(models.IntegerField())
    working_hours = ArrayField(models.CharField(max_length=128))


class Order(models.Model):
    order_id = models.IntegerField(unique=True, primary_key=True)
    weight = models.FloatField()
    region = models.IntegerField()
    delivery_hours = ArrayField(models.CharField(max_length=128))
    courier_id = models.ForeignKey('Courier', default=-1, on_delete=models.SET_DEFAULT)
    completed = models.BooleanField(default=False)