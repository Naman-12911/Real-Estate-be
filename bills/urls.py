from django.urls import path,include
from .views import *


urlpatterns = [
    path('projects/', ProjectsApi.as_view(),name="ProjectsApi"),
    path('bills/', ConstBillAPI.as_view(),name="ConstBillAPI"),
    path('bills-excel/', ExcelBillsAPI.as_view(),name="ExcelBillsAPI"),
    path('previous/bills/', BillsExportedListView.as_view(),name="BillsExportedListView"),
]