from django.urls import path,include
from .views import *



urlpatterns = [
    path('units/status/', BookedAvailableUnit.as_view(), name='booked-available-hold-units'),
    path('top-performer/', TopPerformerAPIview.as_view(), name='TopPerformerAPIview'),

]