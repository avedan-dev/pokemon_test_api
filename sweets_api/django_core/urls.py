from django.contrib import admin
from django.urls import path, include
from rest_framework.schemas import get_schema_view
from rest_framework.renderers import JSONOpenAPIRenderer

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('sweets_api.sweets.urls')),
]
