from django.contrib import admin

# Register your models here.
from .models import Courier, Order, CouriersAndOrders
admin.site.register(Courier)
admin.site.register(Order)
admin.site.register(CouriersAndOrders)
