from django.urls import path

from docx_gen.views import (
    AllotmentLetterDraft, TAndCPLetterDraft, NoDuesCertificateDraft, BookingForm, FinalCostSheet,
    DemandLetterDraft, LetterOfPossessionDraft, BankNocAxisBankNocDraft, BankNocCanaraBankNocDraft,
    BankNocHdfcBankNocDraft, BankNocLicBankNocDraft, BankNocPnbBankNocDraft, BankNocSbiRacpcNocDraft,
    BankNocSbiRacpc2NocDraft, RetrieveBookingPersonalDeatilsAPIView
)

urlpatterns = [
    path('raw-data/', RetrieveBookingPersonalDeatilsAPIView.as_view(), name="RetrieveBookingPersonalDeatils"),

    path('allotment-letter-draft/', AllotmentLetterDraft.as_view(), name="AllotmentLetterDraft"),
    path('booking-form/', BookingForm.as_view(), name="BookingForm"),
    path('demand-letter-draft/', DemandLetterDraft.as_view(), name="DemandLetterDraft"),
    path('final-cost-sheet/', FinalCostSheet.as_view(), name="FinalCostCalculationSheet"),
    path('letter-of-possession-draft/', LetterOfPossessionDraft.as_view(), name="LetterOfPossessionDraft"),
    path('no-dues-certificate-draft/', NoDuesCertificateDraft.as_view(), name="NoDuesCertificateDraft"),
    path('t-and-cp-letter-draft/', TAndCPLetterDraft.as_view(), name="TAndCPLetterDraft"),

    path('bank-noc-axis-bank-noc-draft/', BankNocAxisBankNocDraft.as_view(), name="BankNocAxisBankNocDraft"),
    path('bank-noc-canara-bank-noc-draft/', BankNocCanaraBankNocDraft.as_view(), name="BankNocCanaraBankNocDraft"),
    path('bank-noc-hdfc-bank-noc-draft/', BankNocHdfcBankNocDraft.as_view(), name="BankNocHdfcBankNocDraft"),
    path('bank-noc-lic-bank-noc-draft/', BankNocLicBankNocDraft.as_view(), name="BankNocLicBankNocDraft"),
    path('bank-noc-pnb-bank-noc-draft/', BankNocPnbBankNocDraft.as_view(), name="BankNocPnbBankNocDraft"),
    path('bank-noc-sbi-racpc-noc-draft/', BankNocSbiRacpcNocDraft.as_view(), name="BankNocSbiRacpcNocDraft"),
    path('bank-noc-sbi-racpc2-noc-draft/', BankNocSbiRacpc2NocDraft.as_view(), name="BankNocSbiRacpc2NocDraft"),

]
