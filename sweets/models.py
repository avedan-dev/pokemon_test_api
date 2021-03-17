from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.timezone import now


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
    rating = models.FloatField(default=0, )
    earning = models.IntegerField(default=0)
    last_order = models.DateTimeField(default=None, null=True)


class Order(models.Model):
    order_id = models.IntegerField(unique=True, primary_key=True)
    weight = models.FloatField()
    region = models.IntegerField()
    delivery_hours = ArrayField(models.CharField(max_length=128))
    finish_time = models.IntegerField(default=None, null=True)

class CouriersAndOrders(models.Model):
    courier_id = models.ForeignKey(Courier, on_delete=models.CASCADE)
    order_id = models.OneToOneField(Order, on_delete=models.CASCADE, primary_key=True)
    completed = models.BooleanField(default=False)
    assign_time = models.DateTimeField(default=now)

    def __str__(self):
        return str(self.order_id.order_id)
