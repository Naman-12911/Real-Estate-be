from django.urls import path,include
from .views import *


urlpatterns = [
    path('booking/', BookingApiview.as_view(),name="BookingApiview"),
    path('booking/<int:pk>/', BookingApiview.as_view(),name="BookingApiview"),

    path('personal-deatils/', PersonalDeatilsApiview.as_view(),name="PersonalDeatilsApiview"),
    path('personal-deatils/<int:pk>/', PersonalDeatilsApiview.as_view(),name="PersonalDeatilsApiview"),

    path('co-deatils/', CoApplicantDeatilsApiview.as_view(),name="CoApplicantDeatilsApiview"),
    path('co-deatils/<int:pk>/', CoApplicantDeatilsApiview.as_view(),name="CoApplicantDeatilsApiview"),

    path('filter-name/', BookingFiltersData.as_view(),name="BookingFiltersData"),
    path('co-applicant/unit/<int:unit_id>/', CoApplicantFormByUnitNo.as_view(), name='CoApplicantFormByUnitNo'),

    path('document/', AllDocumentApiview.as_view(),name="AllDocumentApiview"),
    path('document<int:pk>/', AllDocumentApiview.as_view(), name='AllDocumentApiview'),
    path('delete-booking/<int:pk>/', DelBookingApiview.as_view(), name='DelBookingApiview'),
    path('cancel-booking/', CancelBookingAPI.as_view(), name='CancelBookingAPI'),
    path('cancel-report/', GenerateCancellationReport.as_view(), name='GenerateCancellationReport'),
]
