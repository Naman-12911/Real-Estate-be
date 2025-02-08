from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin
# Register your models here.

class FbLeadseAdmin(ImportExportModelAdmin):
    list_display = ('id','full_name', 'user','assigned_to',
                    'site_visit_to','corporate_visit_to','email','phone_number','dump_lead','permanent_dump_lead','site_visit','booked','corporate_visit','intersted',
                    'block_enquiry','call_not_recevied','do_not_call','good_lead','re_visit','poor_lead','may_be')
    search_fields = ('full_name', 'email', 'phone_number', 'user__name', 'assigned_to__name', 
                     'site_visit_to__name', 'corporate_visit_to__name')
    

class LeadSourceAdmin(ImportExportModelAdmin):
    pass

class ModeLeadAdmin(ImportExportModelAdmin):
    pass

class LeadEditAdmin(ImportExportModelAdmin):
    list_display = ('user','fb_leads','visited_by','mode','status_of_lead','project','status_of_lead_warm_hot_cold','mobile_number')


class MediumOfLeadAdmin(ImportExportModelAdmin):
    pass


class preferredLocationAdmin(ImportExportModelAdmin):
    pass



class ReasonAdmin(ImportExportModelAdmin):
    pass

class BudgetAdmin(ImportExportModelAdmin):
    pass


class StatusLeadAdmin(ImportExportModelAdmin):
    pass

class ReasonSiteVisitAdmin(ImportExportModelAdmin):
    pass

class NotificationStoreAdmin(ImportExportModelAdmin):
    list_display = ('id','message','seen','created_at','updated_at','head','sent_to')
    

admin.site.register(FbLeads,FbLeadseAdmin)
admin.site.register(LeadSource,LeadSourceAdmin)
admin.site.register(MediumOfLead,MediumOfLeadAdmin)
admin.site.register(ModeLead,ModeLeadAdmin)
admin.site.register(preferredLocation,preferredLocationAdmin)
admin.site.register(Reason,ReasonAdmin)
admin.site.register(Budget,BudgetAdmin)
admin.site.register(StatusLead,StatusLeadAdmin)
admin.site.register(LeadEdit,LeadEditAdmin)
admin.site.register(ReasonSiteVisit,ReasonSiteVisitAdmin)
admin.site.register(NotificationStore,NotificationStoreAdmin)
