from django.urls import path,include
from .views import *


urlpatterns = [
    path('contact/', ContactUsAPIview.as_view(),name="ContactUsAPIview"),
    path('contact/<int:pk>/', ContactUsAPIview.as_view(),name="ContactUsAPIview"),
]