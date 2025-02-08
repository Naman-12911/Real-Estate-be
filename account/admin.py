from django.contrib import admin
from django.utils.translation import gettext_lazy  as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import User,FCMTokens,UserHoliday
from django.contrib.auth.models import Group


class customUserAdmin(UserAdmin):
  #form = UserChangeForm
  fieldsets = (
      (None, {'fields': ('email', 'password', )}),
      (_('Personal info'), {'fields': ('name',)}),
      (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser','sales_employee','accounts_employee','site_worker','admin','normal_user'
                                                ),}),
      (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('user_info'), {'fields': ( 'phone_no',
                                     )}),

       (_('account_info'), {'fields': ( 'account_report','account_property_status','account_direct_booking','account_booking_form','account_payment_stages',
                                       'account_demand_letter','account_documentation','account_billing','account_clinet_loan_profile','account_project_document',
                                       'accounts_all_details','accounts_customer_details','accounts_registry_details'
                                     )}),
        (_('sales_info'), {'fields': ( 'sales_my_job_desk', 'sales_add_new_lead','sales_view_lead','sales_dump_data','sales_site_visit','sales_corporate_visit'
                                     )}),
  )
  add_fieldsets = (
      (None, {
          'classes': ('wide', ),
          'fields': ('email', 'password1', 'password2'),
      }),
  )
  list_display = ['email', 'name', 'is_staff' ,"phone_no"]
  search_fields = ('email',)
  ordering = ('email', )
admin.site.register(User, customUserAdmin)
admin.site.unregister(Group)
admin.site.register(UserHoliday)
admin.site.register(FCMTokens)