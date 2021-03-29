from django.urls import path

from .views import CouriersPostView, CouriersGetPatchView, OrderView, AssignView, CompleteView


app_name = "sweets"

# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path('couriers/<int:pk>', CouriersGetPatchView.as_view()),
    path('couriers', CouriersPostView.as_view()),
    path('orders', OrderView.as_view()),
    path('orders/assign', AssignView.as_view()),
    path('orders/complete', CompleteView.as_view()),
]
