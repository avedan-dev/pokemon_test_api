from django.contrib import admin

# Register your models here.
from .models import Courier, Order
admin.site.register(Courier)
admin.site.register(Order)
