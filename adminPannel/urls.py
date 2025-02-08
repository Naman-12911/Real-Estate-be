from django.urls import path,include
from .views import *
# from .filters_views import *
from .views_bookings import *
from .views_profileSearch import *
from .viewsfestival import *
from .views_faq import *
from .views_client_loan import *
from .views_tickets import *
from .views_documentation import *
from .views_social import *
from .overview import *
# from .views_count import *

urlpatterns = [
    path('project/', ProjectAPIview.as_view(),name="ProjectAPIview"),
    path('project/<int:pk>/', ProjectAPIview.as_view(),name="ProjectAPIview"),

    path('project-type/', ProjectTypAPIview.as_view(),name="ProjectTypAPIview"),
    path('project-type/<int:pk>/', ProjectTypAPIview.as_view(),name="ProjectTypAPIview"),

    path('unit-number/', UnitNoAPIview.as_view(),name="UnitNoAPIview"),
    path('unit-number/<int:pk>/', UnitNoAPIview.as_view(),name="UnitNoAPIview"),

    path('phase/', PhaseAPIview.as_view(),name="PhaseAPIview"),
    path('phase/<int:pk>/', PhaseAPIview.as_view(),name="PhaseAPIview"),

    path('status/', StatusAPIview.as_view(),name="StatusAPIview"),
    path('status/<int:pk>/', StatusAPIview.as_view(),name="StatusAPIview"),

    path('tax/', TaxTypeAPIview.as_view(),name="TaxTypeAPIview"),
    path('tax/<int:pk>/', TaxTypeAPIview.as_view(),name="TaxTypeAPIview"),

    # urls for the filters apis
   

  
    path('unit-no-with-available/', UnitNoListunbookedAllViewunitnumber.as_view(),name="UnitNoListunbookedAllViewunitnumber"),
    path('unit-no-non-available/', UnitNoListbookedAllViewunitnumber.as_view(),name="UnitNoListunbookedAllViewunitnumber"),

    path('document-type/', ProjectDocumentTypeAPIview.as_view(),name="ProjectDocumentTypeAPIview"),
    path('document-type/<int:pk>/', ProjectDocumentTypeAPIview.as_view(),name="ProjectDocumentTypeAPIview"),

    path('upload-document/', ProjectDocumentAPIview.as_view(),name="ProjectDocumentAPIview"),
    path('upload-document/<int:pk>/', ProjectDocumentAPIview.as_view(),name="ProjectDocumentAPIview"),



    # booking form apis
    path('booking/', BookingApiview.as_view(),name="BookingApiview"),
    path('booking/<int:pk>/', BookingApiview.as_view(),name="BookingApiview"),

    path('personal-deatils/', PersonalDeatilsApiview.as_view(),name="PersonalDeatilsApiview"),
    path('personal-deatils/<int:pk>/', PersonalDeatilsApiview.as_view(),name="PersonalDeatilsApiview"),

    path('co-deatils/', CoApplicantDeatilsApiview.as_view(),name="CoApplicantDeatilsApiview"),
    path('co-deatils/<int:pk>/', CoApplicantDeatilsApiview.as_view(),name="CoApplicantDeatilsApiview"),

   
    path('co-applicant/unit/<int:unit_id>/', CoApplicantFormByUnitNo.as_view(), name='CoApplicantFormByUnitNo'),

    path('document/', AllDocumentApiview.as_view(),name="AllDocumentApiview"),
    path('document<int:pk>/', AllDocumentApiview.as_view(), name='AllDocumentApiview'),


    # profile search 

    path('payment-stage-deatils/', PaymentStageDetailAPIview.as_view(),name="PaymentStageDetailAPIview"),
    path('payment-stage-deatils/<int:pk>/', PaymentStageDetailAPIview.as_view(),name="PaymentStageDetailAPIview"),
    # path('payment-stage/', PaymentStagesAPIview.as_view(),name="PaymentStagesAPIview"),
    # path('payment-stage/<int:id>/', PaymentStagesAPIview.as_view(),name="PaymentStagesAPIview"),
    path('payment-receipts/', PaymentReceiptsAPIview.as_view(),name="PaymentReceiptsAPIview"),
    path('payment-receipts/<int:id>/', PaymentReceiptsAPIview.as_view(),name="PaymentReceiptsAPIview"),
    path('payment-demand-information/', RemiderDemandInformationAPIview.as_view(),name="RemiderDemandInformationAPIview"),
    path('payment-demand-information/<int:id>/', RemiderDemandInformationAPIview.as_view(),name="RemiderDemandInformationAPIview"),
    path('user-balance/', UserBalance.as_view(),name="RemiderDemandInformationAPIview"),

    # festivals
    path('festival/', FestivalPostAPIview.as_view(),name="FestivalPostAPIview"),
    path('festival/<int:pk>/', FestivalPostAPIview.as_view(),name="FestivalPostAPIview"),


    # faq
    path('faq/', FaqApiview.as_view(),name="FaqApiview"),
    path('faq/<int:pk>/', FaqApiview.as_view(),name="FaqApiview"),

    # clinet loan profile
    path('loan/', ClientLoanApiview.as_view(),name="ClientLoanApiview"),
    path('loan/<int:pk>/', ClientLoanApiview.as_view(),name="ClientLoanApiview"),

    # tickets
    path('ticket-admin/', TicketAdminAPIview.as_view(),name="TicketAdminAPIview"),
    path('ticket-admin/<int:pk>/', TicketAdminAPIview.as_view(),name="TicketAdminAPIview"),

    # documentation
    path('demand-letter/', DemandLetterAPIview.as_view(),name="DemandLetterAPIview"),
    path('demand-letter/<int:pk>/', DemandLetterAPIview.as_view(),name="DemandLetterAPIview"),

    path('mode-of-payment/', ModeOfPaymentAPIview.as_view(),name="ModeOfPaymentAPIview"),
    path('mode-of-payment/<int:pk>/', ModeOfPaymentAPIview.as_view(),name="ModeOfPaymentAPIview"),

    path('bank-name/', BankNameBranchNameAPIview.as_view(),name="BankNameBranchNameAPIview"),
    path('bank-name/<int:pk>/', BankNameBranchNameAPIview.as_view(),name="BankNameBranchNameAPIview"),

    path('receipt/<int:pk>/', ReceiptAPIview.as_view(),name="ReceiptAPIview"),
    path('receipt/', ReceiptAPIview.as_view(),name="ReceiptAPIview"),

    path('receipt-filter/', BookingFiltersData.as_view(),name="BookingFiltersData"),

    path('fb-lead/filter/site-visit/',FbLeadFilterSiteVisit.as_view()),
    path('fb-lead/filter/dump/',FbLeadFilterDumpList.as_view()),
    path('corporate-leads/', FbLeadFilterCorporate.as_view(),name="FbLeadFilterCorporate"),
    
    path('pr-highlight-metrics/', PRHighlightMetrics.as_view(), name="HighlightMetrics"),
    path('pr-highlight-metrics-data-pending/', PRHighlightMetricsNumericDataPending.as_view(), name="PRHighlightMetricsNumericDataPending"),
    path('pr-highlight-metrics-data-next-schedule-task/', PRHighlightMetricsNumericDataPendingNextScheduleTask.as_view(), name="PRHighlightMetricsNumericDataPendingNextScheduleTask"),
    path('pr-highlight-metrics-data-today-task/', PRHighlightMetricsNumericDataPendingTodayTask.as_view(), name="PRHighlightMetricsNumericDataPendingTodayTask"),

    path('leads-overview/', LeadsOverview.as_view(), name="HighlightMetrics"),
    path('task-overview/', TaskOverview.as_view(), name="TaskOverview"),
    path('upcoming-site-visits/', UpcomingSiteVisit.as_view(), name="UpcomingSiteVisit"),
    path('lr-highlight-metrics/', LeadsHighlighted.as_view(), name="LeadsHighlighted"),
    #path('lr-highlight-metrics-data/', LeadsHighlightedNumericData.as_view(), name="LeadsHighlightedNumericData"),

    path('lead-sv-book/', LeadsSvBook.as_view(), name="LeadsSvBook"),
    path('lead-sv-book-data/', LeadsSvBookNumericData.as_view(), name="LeadsSvBookNumericData"),
    path('lead-source-analysis/', LeadSourceAna.as_view(), name="LeadSourceAna"),

    path('agent-perf-report/', AgentPerformanceReport.as_view(), name='AgentPerformanceReport'),
    path('top-agent-perf/', TopPerformingAgent.as_view(), name='TopPerformingAgent'),
    path('all-time-leads/', AllTimeLeads.as_view(), name="AllTimeLeads"),
    path('performance-trend/', PerformanceTrend.as_view(), name="PerformanceTrend"),
    path('plat-comp/', PlatformComp.as_view(), name="PlatformComp"),

    path('count-of-status-lead/', StatusCountOfLeads.as_view(), name="StatusCountOfLeads"),
    path('lead-counts/', TotalLeadDumpCorporateSiteVisitCount.as_view(), name='lead-counts'),
    path('count-of-site-viste-project/', TotalSiteVisitAccordingToProject.as_view(), name='TotalSiteVisitAccordingToProject'),
]
