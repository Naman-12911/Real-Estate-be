from django.urls import path,include
from .views import *


urlpatterns = [
    path('festival/', FestivalPostAPIview.as_view(),name="FestivalPostAPIview"),
    path('festival/<int:pk>/', FestivalPostAPIview.as_view(),name="FestivalPostAPIview"),
]