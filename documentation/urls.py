from django.urls import path,include
from .views import *


urlpatterns = [
    path('demand-letter/', DemandLetterAPIview.as_view(),name="DemandLetterAPIview"),
    path('demand-letter/<int:pk>/', DemandLetterAPIview.as_view(),name="DemandLetterAPIview"),

    path('mode-of-payment/', ModeOfPaymentAPIview.as_view(),name="ModeOfPaymentAPIview"),
    path('mode-of-payment/<int:pk>/', ModeOfPaymentAPIview.as_view(),name="ModeOfPaymentAPIview"),

    path('bank-name/', BankNameBranchNameAPIview.as_view(),name="BankNameBranchNameAPIview"),
    path('bank-name/<int:pk>/', BankNameBranchNameAPIview.as_view(),name="BankNameBranchNameAPIview"),

    path('receipt/<int:pk>/', ReceiptAPIview.as_view(),name="ReceiptAPIview"),
    path('receipt/', ReceiptAPIview.as_view(),name="ReceiptAPIview"),

    path('receipt-filter/', BookingFiltersData.as_view(),name="BookingFiltersData"),
    path('receipt-filter-cancel/', BookingFiltersCancelData.as_view(),name="BookingFiltersCancelData"),
    path('demand-letter-personal-details/', DemandLetterPersonalDeatilsAPIview.as_view(),name="DemandLetterPersonalDeatilsAPIview"),
    path('fix-payment-stage/', PaymentDetails.as_view(), name='fix-payment-stage'),
    path("export-receipts/", ReceiptExportAPIview.as_view(), name="ReceiptExportAPIview"),
]