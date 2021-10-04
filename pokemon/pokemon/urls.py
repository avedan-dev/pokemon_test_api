from django.urls import path

from .views import PokemonTypesDamageView, PokemonCountersView, PokemonBeatView


app_name = "pokemon"
# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path('pokemon/types/<str:pk>', PokemonTypesDamageView.as_view()),
    path('pokemon/counters/<str:pk>', PokemonCountersView.as_view()),
    path('pokemon/beat/<str:pk>', PokemonBeatView.as_view()),
]
