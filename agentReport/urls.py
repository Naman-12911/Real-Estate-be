from django.urls import path,include
from .views import *



urlpatterns = [
   

   path('data/', AgentReportAPIview.as_view(),name="AgentReportAPIview"),

   path('agent-site-visite-number/', AgentSiteVisitsAPIview.as_view(),name="AgentSiteVisitsAPIview"),



]