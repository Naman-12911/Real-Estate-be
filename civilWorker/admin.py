from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin
# Register your models here.

admin.site.register(Miscellaneous)
admin.site.register(Bills)
admin.site.register(Remarks)
admin.site.register(CivilStatges)
admin.site.register(ConstructorProfile)
admin.site.register(ExcelFilesCivilStages)
admin.site.register(InvoiceCivilStages)

class ConstructorUnitNoAdmin(ImportExportModelAdmin):
    list_display = ('id', 'projects', 'unit_no', 'available', 'booked', 'hold', 'east_by', 'west_by', 'north_by', 'south_by', 'unit_cost', 'square_fit')

admin.site.register(ConstructorUnitNo,ConstructorUnitNoAdmin)
