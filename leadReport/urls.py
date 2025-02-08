from django.urls import path,include
from .views import *



urlpatterns = [


    path('lead-counts/', LeadCountsAPIView.as_view(), name='lead_counts'),
    path('medium-lead/', MediumOfLeadCountAPIView.as_view(), name='MediumOfLeadCountAPIView'),
    path('lead-source/', SourceCountAPIView.as_view(),name="SourceCountAPIView"),
    path('lead-fb/', SourceCountFbLeadAPIView.as_view(),name="SourceCountFbLeadAPIView"),
    path('lead-source-type/', SourceTypeAPIView.as_view(),name="SourceCountFbLeadAPIView"),

]