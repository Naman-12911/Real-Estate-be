from django.urls import path

from . import views
from . import views_filter
from .admin_views import Fb_ViewAdmin
from . import views_filter

urlpatterns = [
    path("fb/",views.Fb_View.as_view()),
    path('fb/<int:pk>/', views.Fb_View.as_view()),

    path('lead-source/',views.LeadSourceAPIView.as_view()),
    path('lead-source/<int:pk>/',views.LeadSourceAPIView.as_view()),

    path('lead-source/filter/',views_filter.LeadSourceFilterListApiview.as_view()),

    path('medium-lead/',views.MediumOfLeadAPIView.as_view()),
    path('medium-lead/<int:pk>/',views.MediumOfLeadAPIView.as_view()),

    path('prefred-location/',views.preferredLocationAPIView.as_view()),
    path('prefred-location/<int:pk>/',views.preferredLocationAPIView.as_view()),

    path('reason-site-visit/',views.ReasonSiteUpdateAPIView.as_view()),
    path('reason-site-visit/<int:pk>/',views.ReasonSiteUpdateAPIView.as_view()),

    path('reason/',views.ReasonAPIView.as_view()),
    path('reason/<int:pk>/',views.ReasonAPIView.as_view()),

    path('budget/',views.BudgetAPIView.as_view()),
    path('budget/<int:pk>/',views.BudgetAPIView.as_view()),

    path('status-lead/',views.StatusLeadAPIView.as_view()),
    path('status-lead/<int:pk>/',views.StatusLeadAPIView.as_view()),

    path('mode-lead/',views.ModeLeadAPIView.as_view()),
    path('mode-lead/<int:pk>/',views.ModeLeadAPIView.as_view()),

    path('lead-edit/',views.LeadEditAPIView.as_view()),
    path('lead-edit/<int:pk>/',views.LeadEditAPIView.as_view()),

    path('dump-lead/',views.FbDumpViewAPIView.as_view()),
    path('dump-lead/<int:pk>/',views.FbDumpViewAPIView.as_view()),

    path('site-visit/',views.FbSiteVisitViewAPIView.as_view()),
    path('site-visit/<int:pk>/',views.FbSiteVisitViewAPIView.as_view()),

    path('fb-lead/lead-edit/<int:fb_lead_id>/',views_filter.FbLeadLeadEditAPIView.as_view()),

    path('fb-lead/filter/',views_filter.FbLeadFilterList.as_view()),

    path('fb-lead/filter/dump/',views_filter.FbLeadFilterDumpList.as_view()),

    path('fb-lead/filter/site-visit/',views_filter.FbLeadFilterSiteVisit.as_view()),

    path('fb-lead/filter/phone-number/',views_filter.FbLeadFilterPhoneNumberList.as_view()),

    path('fb-leads-zap', views.FBleadsZap.as_view()),
    path('fb-leads-zap-2', views.FBleadsZap2.as_view()),

    path('show-notification/',views.ShowNotificationAPIview.as_view()),
    path('pending-task/',views.PendingTasks.as_view()),

    path('admin-fb-lead/',Fb_ViewAdmin.as_view()),
    path('reassign-dump/',views.ReassignDumpleads.as_view()),
    path('agent-site-visit/', views.AgentSiteVisits.as_view()),
    path('agent-site-visit-fb/', views.AgentSiteVisitsForFbLead.as_view()),
    path('next-scheduled/', views.CheckScheduled.as_view()),

    path('lead-medium/',views.AgentLeadSouce.as_view()),
    path('lead-99/',views.acers99Leads.as_view()),
    path('lead-housing/',views.HousingLeads.as_view()),
    path('lead-house-online/',views.HomeOnlineLeads.as_view()),

    path('delete-fb-delete/',views.FbLeadAPIviewDelete.as_view()),

    path('site-visit-count/',views.SiteVisitCountAPIView.as_view()),

    path('dump-lead-count/',views.DumpLeadsCount.as_view()),
    path('update-lead-status/',views.ModifyStatus.as_view()),

]
