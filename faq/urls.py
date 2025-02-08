from django.urls import path,include
from .views import FaqApiview


urlpatterns = [
    path('faq/', FaqApiview.as_view(),name="FaqApiview"),
    path('faq/<int:pk>/', FaqApiview.as_view(),name="FaqApiview"),

]
