from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin

class PaymentStageDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'stage_name', 'personal_deatils', 'step_no', 'payable_date', 'paybale_amount')

class PaymentReceiptsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'stage_deatils', 'receipent_number', 'mode', 'amount_recived', 'date')

class RemiderDemandInformationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'payment_receipts_stage', 'deplay', 'interst', 'amount_to_be_paid')

admin.site.register(PaymentStageDetail, PaymentStageDetailAdmin)
admin.site.register(PaymentReceipts, PaymentReceiptsAdmin)
admin.site.register(RemiderDemandInformation, RemiderDemandInformationAdmin)