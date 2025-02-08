from django.urls import path,include
from .views import *
from .filters_views import *



urlpatterns = [
    path('message/', WhatsAppMessageAPIview.as_view(),name="WhatsAppMessageAPIview"),
    path('message/<int:pk>/', WhatsAppMessageAPIview.as_view(),name="WhatsAppMessageAPIview"),
    path('message/all/', WhatsAppMessageAllAPIview.as_view(),name="WhatsAppMessageAllAPIview"),

    path('filter/', WhatsAppMessageFilterGenric.as_view(),name="WhatsAppMessageFilterGenric"),

    path('track-whats-message/', WhatsAppMessageTrackAPIview.as_view(),name="WhatsAppMessageTrackAPIview"),


   


]
