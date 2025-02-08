from django.contrib import admin
from .models import SiteWorkers, MonthlyExpense
from import_export.admin import ImportExportModelAdmin

class SiteWorkersAdmin(admin.ModelAdmin):
    #list_display = ('id', 'project_name', 'unit_no','stage1','stage2','stage3','stage4','stage5','stage6','stage7',)
    pass

admin.site.register(SiteWorkers,SiteWorkersAdmin)
admin.site.register(MonthlyExpense)
