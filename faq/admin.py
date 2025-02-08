from django.contrib import admin
from .models import Faq
from import_export.admin import ImportExportModelAdmin

class FaqAdmin(ImportExportModelAdmin):
    pass

admin.site.register(Faq,FaqAdmin)
