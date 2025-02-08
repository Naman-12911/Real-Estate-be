from django.urls import path,include
from .views import *
from .civilWorkerExcelFiles import *


urlpatterns = [
    path('all-leads/', AllLeadAPIView.as_view(),name="AllLeadAPIView"),
    path('all-leads-dump/', AllDumpAPIView.as_view(),name="AllDumpAPIView"),
    path('all-leads-site-visit/', AllSiteVisitAPIView.as_view(),name="AllSiteVisitAPIView"),
    path('all-leads-corporate/', AllCorporateVisitAPIView.as_view(),name="AllCorporateVisitAPIView"),

    path('lead-sv-book/', LeadsSvBookFilesForBookedStatus.as_view(),name="LeadsSvBookFilesForBookedStatus"),
    path('pr-high-light-next-shedule-task/', PRHighlightMetricsNextSheduleTask.as_view(),name="PRHighlightMetricsNextSheduleTask"),
    path('pr-high-light-today-task/', PRHighlightMetricsTodayTask.as_view(),name="PRHighlightMetricsTodayTask"),
    path('site-worker-file/', SiteWorkersData.as_view(),name="SiteWorkersData"),
    # civil worker excel files
    path('constructor-bill/', ContractorBillsAPIview.as_view(),name="ContractorBillsAPIview"),

    path('download-prev-bill/', DownloadPreviousBillsAPIview.as_view(),name="DownloadPreviousBillsAPIview"),
    path('invoice-bill/', InvoiceAPIview.as_view(),name="InvoiceAPIview"),
    path('invoice-bill/download/', InvoiceAPIview.as_view(),name="InvoiceAPIview"),
    path('constructor-bill/view/', ContractorBillsProtectFormSavingRemoveColorAPIview.as_view(),name="ContractorBillsProtectFormSavingRemoveColorAPIview"),
    path('invoice-bill/view/', InvoiceRemoveSavingFileAPIview.as_view(),name="InvoiceRemoveSavingFileAPIview"),
    # path('merge-files/', MergeAPIsToExcelAPIView.as_view(),name="MergeAPIsToExcelAPIView"),



]