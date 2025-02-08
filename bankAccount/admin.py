from django.contrib import admin
from .models import BankAccount,BankName
from import_export.admin import ImportExportModelAdmin
# Register your models here.

class BankNameAdmin(admin.ModelAdmin):
    list_display = ('id', 'bank_name')

class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'bank_name', 'personal_deatils', 'bank_address', 'bank_ifsc', 'loan_file_no', 'loan_date', 'loan_account_number', 'loan_amount_sanctioned', 'executive_name', 'executive_number', 'status', 'margin_amount')

admin.site.register(BankName, BankNameAdmin)
admin.site.register(BankAccount, BankAccountAdmin)
