from django.contrib import admin
from django.urls import path, include
from rest_framework.schemas import get_schema_view
from rest_framework.renderers import JSONOpenAPIRenderer

schema_view = get_schema_view(
    title='Server Monitoring API',
    url='http://127.0.0.1:8000/',
    renderer_classes=[JSONOpenAPIRenderer]
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('sweets_api.sweets.urls')),
    path('schema.json', schema_view),
]