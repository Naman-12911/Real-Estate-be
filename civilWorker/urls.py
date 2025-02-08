from django.urls import path,include
from .views import *


urlpatterns = [
    path('miscellaneous/', MiscellaneousAPIview.as_view(),name="MiscellaneousAPIview"),
    path('miscellaneous/<int:pk>/', MiscellaneousAPIview.as_view(),name="MiscellaneousAPIview"),

    path('remark/', RemarksAPIview.as_view(),name="RemarksAPIview"),
    path('remark/<int:pk>/', RemarksAPIview.as_view(),name="RemarksAPIview"),

    path('bill/', BillsAPIview.as_view(),name="BillsAPIview"),
    path('bill/<int:pk>/', BillsAPIview.as_view(),name="BillsAPIview"),

    path('civil-stages/', CivilStatgesAPIview.as_view(),name="CivilStatgesAPIview"),
    path('civil-stages/<int:pk>/', CivilStatgesAPIview.as_view(),name="CivilStatgesAPIview"),

    path('constructor-profile/', ConstructorProfileAPIview.as_view(),name="ConstructorProfileAPIview"),
    path('constructor-profile/<int:pk>/', ConstructorProfileAPIview.as_view(),name="ConstructorProfileAPIview"),

    path('constructor-unit/', COnstructorUnitNoAPIview.as_view(),name="COnstructorUnitNoAPIview"),
    path('constructor-unit/<int:pk>/', COnstructorUnitNoAPIview.as_view(),name="COnstructorUnitNoAPIview"),
]