from django.urls import path,include
from .views import *


urlpatterns = [
    path('transfer-data/', TransferDataToAnotherAgent.as_view(),name="TransferDataToAnotherAgent"),
]