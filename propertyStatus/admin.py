from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin

class ProjectTypeAdmin(ImportExportModelAdmin):
    list_display = ('id', 'projects', 'property_type')

class UnitNoAdmin(ImportExportModelAdmin):
    list_display = ('id', 'projects', 'unit_no', 'available', 'booked', 'hold', 'east_by', 'west_by', 'north_by', 'south_by', 'unit_cost', 'square_fit')

class ProjectAdmin(ImportExportModelAdmin):
    list_display = ('id', 'project_name', 'address')

class PhaseAdmin(ImportExportModelAdmin):
    list_display = ('id', 'unit', 'phase_name')

class StatusAdmin(ImportExportModelAdmin):
    list_display = ('id', 'status_name')

class TaxTypeAdmin(ImportExportModelAdmin):
    list_display = ('id', 'tax_type', 'tax_percent')

class ProjectDocumentTypeAdmin(ImportExportModelAdmin):
    list_display = ('id', 'document_of')

class ProjectDocumentAdmin(ImportExportModelAdmin):
    list_display = ('id', 'project_document', 'document_type', 'date', 'document_file')

# Register your models with the custom admin classes
admin.site.register(ProjectType, ProjectTypeAdmin)
admin.site.register(UnitNo, UnitNoAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Phase, PhaseAdmin)
admin.site.register(Status, StatusAdmin)
admin.site.register(TaxType, TaxTypeAdmin)
admin.site.register(ProjectDocumentType, ProjectDocumentTypeAdmin)
admin.site.register(ProjectDocument, ProjectDocumentAdmin)