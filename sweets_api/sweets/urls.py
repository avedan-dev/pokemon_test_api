from django.urls import path

from .views import CourierView, OrderView, AssignView, CompleteView


app_name = "articles"

# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path('couriers/<int:pk>', CourierView.as_view()),
    path('couriers', CourierView.as_view()),
    path('orders', OrderView.as_view()),
    path('orders/assign', AssignView.as_view()),
    path('orders/complete', CompleteView.as_view()),
]
