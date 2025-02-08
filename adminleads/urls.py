from django.urls import path,include
from .views import *
from .filters_views import *


urlpatterns = [
    path('all-leads/', Fb_ViewAdminAPIView.as_view(),name="Fb_ViewAdminAPIView"),
    path('all-leads/<int:pk>/', Fb_ViewAdminAPIView.as_view(),name="Fb_ViewAdminAPIView"),

    path('site-visit/', FbSiteVisitViewAdminAPIView.as_view(),name="FbSiteVisitViewAdminAPIView"),
    path('site-visit/<int:pk>/', FbSiteVisitViewAdminAPIView.as_view(),name="FbSiteVisitViewAdminAPIView"),


    path('corporate/', FbCorporateAdminVisitAPIView.as_view(),name="FbCorporateAdminVisitAPIView"),
    path('corporate/<int:pk>/', FbCorporateAdminVisitAPIView.as_view(),name="FbCorporateAdminVisitAPIView"),


    path('dump-leads/', FbDumpViewAdminAPIView.as_view(),name="FbDumpViewAdminAPIView"),
    path('dump-leads/<int:pk>/', FbDumpViewAdminAPIView.as_view(),name="FbDumpViewAdminAPIView"),

    path('corporate-leads/', FbLeadFilterCorporte.as_view(),name="FbLeadFilterCorporte"),

    path('total-count/', TotalCountsLeadStatsAPIView.as_view(),name="TotalCountsLeadStatsAPIView"),

    path('sales-person-count/', SalesPersonCountsLeadStatsAPIView.as_view(),name="SalesPersonCountsLeadStatsAPIView"),

    path('next-shedule-date/', NextSheduleTrackAPIview.as_view(),name="NextSheduleTrackAPIview"),

    path('next-booking-date/', BookingDoneAPIview.as_view(),name="BookingDoneAPIview"),
    path('lead-data-user/', LeadEditDataAPIView.as_view(),name="LeadEditDataAPIView"),



]