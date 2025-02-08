from django.urls import path,include
from .views import ClientLoanApiview


urlpatterns = [
    path('loan/', ClientLoanApiview.as_view(),name="ClientLoanApiview"),
    path('loan/<int:pk>/', ClientLoanApiview.as_view(),name="ClientLoanApiview"),

]
