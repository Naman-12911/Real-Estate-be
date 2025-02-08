from django.contrib import admin
from .models import ClientLoanProfile
from import_export.admin import ImportExportModelAdmin
class ClientLoanProfileAdmin(ImportExportModelAdmin):
    list_display = ('id', 'user', 'bookings', 'bank_name', 'bank_address', 'bank_ifsc', 'loan_file_no', 'loan_date', 'loan_amount_sanctioned', 'excutive_name', 'excutive_number', 'status_active_inactive', 'loan_approval_date', 'margin_amount')

admin.site.register(ClientLoanProfile, ClientLoanProfileAdmin)