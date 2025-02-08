from django.urls import path,include
from .views import *


urlpatterns = [
    path('filter-name-unitno/', ProfileSearchData.as_view(),name="ProfileSearchData"),
    path('payment-stage-deatils/', PaymentStageDetailAPIview.as_view(),name="PaymentStageDetailAPIview"),
    path('payment-stage-deatils/<int:pk>/', PaymentStageDetailAPIview.as_view(),name="PaymentStageDetailAPIview"),
    path('payment-stage-deatils-cancel/', PaymentStageDetailCancelAPIview.as_view(),name="PaymentStageDetailCancelAPIview"),
    path('payment-stage-deatils-cancel/<int:pk>/', PaymentStageDetailCancelAPIview.as_view(),name="PaymentStageDetailCancelAPIview"),
    
    # path('payment-stage/', PaymentStagesAPIview.as_view(),name="PaymentStagesAPIview"),
    # path('payment-stage/<int:id>/', PaymentStagesAPIview.as_view(),name="PaymentStagesAPIview"),
    path('payment-receipts/', PaymentReceiptsAPIview.as_view(),name="PaymentReceiptsAPIview"),
    path('payment-receipts/<int:id>/', PaymentReceiptsAPIview.as_view(),name="PaymentReceiptsAPIview"),
    path('payment-demand-information/', RemiderDemandInformationAPIview.as_view(),name="RemiderDemandInformationAPIview"),
    path('payment-demand-information/<int:id>/', RemiderDemandInformationAPIview.as_view(),name="RemiderDemandInformationAPIview"),
    path('user-balance/', UserBalance.as_view(),name="RemiderDemandInformationAPIview"),
    path('user-balance-export/', UserBalanceExcel.as_view(),name="RemiderDemandInformationAPIview"),
    
]