from django.urls import path,include
from .views import *


urlpatterns = [
    path('ticket/', TicketAPIview.as_view(),name="TicketAPIview"),
    path('ticket/<int:pk>/', TicketAPIview.as_view(),name="TicketAPIview"),

    path('ticket-admin/', TicketAdminAPIview.as_view(),name="TicketAdminAPIview"),
    path('ticket-admin/<int:pk>/', TicketAdminAPIview.as_view(),name="TicketAdminAPIview"),


]