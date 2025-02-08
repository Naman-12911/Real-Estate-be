from django.urls import path,include
from .views import *

urlpatterns = [
    path('mass-email/', MassEmail.as_view(), name='mass-email'),
    path('email-template/', EmailTemplate.as_view(), name='mass-email'),
]
