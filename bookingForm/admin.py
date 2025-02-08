from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin

class BookingAdmin(ImportExportModelAdmin):
    list_display = ('id', 'user', 'project_name', 'type_name', 'unit_no', 'tax_type', 'gender', 'loan_required', 'application_date')

class PersonalDetailsAdmin(ImportExportModelAdmin):
    list_display = ('id', 'user',  'applicant_name', 'so_wo_do', 'mobile_number', 'email_address')
    

class CoApplicantFormAdmin(ImportExportModelAdmin):
    list_display = ('id', 'user', 'name', 'date_of_birth', 'age', 'present_address', 'permanent_address', 'residence_address')


class AllDocumentAdmin(ImportExportModelAdmin):
    pass

admin.site.register(Booking, BookingAdmin)
admin.site.register(PersonalDeatils, PersonalDetailsAdmin)
admin.site.register(CoApplicantForm, CoApplicantFormAdmin)
admin.site.register(AllDocument,AllDocumentAdmin)
admin.site.register(CancelBooking)
admin.site.register(CancelRefund)