from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin

class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('id', 'receipt_unique_id', 'receipt_date', 'project_name', 'unit_number', 'payment_stage', 'mode_of_payment')

class BankNameAdmin(admin.ModelAdmin):
    list_display = ('id', 'bank_name', 'drawn_on')

class ModeOfPaymentAdmin(ImportExportModelAdmin):
    list_display = ('id', 'mode_of_payment')

class DemandLetterAdmin(ImportExportModelAdmin):
    list_display = ('id', 'project_name', 'unit_number', 'payment_stage', 'date', 'tax_percentage', 'project_type')

admin.site.register(Receipt, ReceiptAdmin)
admin.site.register(BankName, BankNameAdmin) 
admin.site.register(ModeOfPayment, ModeOfPaymentAdmin)
admin.site.register(DemandLetter, DemandLetterAdmin)
