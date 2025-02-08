from django.db import models
from django.contrib.auth.models import AbstractUser,PermissionsMixin
from django.utils.translation import gettext_lazy  as _
from account.managers import CustomUserManager
from rest_framework_simplejwt.tokens import RefreshToken
# Create your models here.
from django.contrib.auth.models import User
from django.utils import timezone

# resgiter the user
AUTH_PROVIDERS = {'email': 'email'}
class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    phone_no = models.CharField(unique=True,  null=True,max_length=10,blank=True)
    name = models.CharField(max_length=100,null=True)
    platform = models.CharField(max_length=50,blank=True,null=True)  #'web', 'app', etc.
    # sales section
    sales_employee = models.BooleanField(default=False)
    sales_my_job_desk = models.BooleanField(default=False)
    sales_add_new_lead = models.BooleanField(default=False)
    sales_view_lead = models.BooleanField(default=False)
    sales_dump_data = models.BooleanField(default=False)
    sales_site_visit = models.BooleanField(default=False)
    sales_corporate_visit = models.BooleanField(default=False)
    # account section
    accounts_employee = models.BooleanField(default=False)
    account_report = models.BooleanField(default=False)
    account_property_status = models.BooleanField(default=False)
    account_direct_booking = models.BooleanField(default=False)
    account_booking_form = models.BooleanField(default=False)
    account_payment_stages = models.BooleanField(default=False)
    account_demand_letter = models.BooleanField(default=False)
    account_documentation = models.BooleanField(default=False)
    account_billing = models.BooleanField(default=False)
    account_clinet_loan_profile= models.BooleanField(default=False)
    account_project_document = models.BooleanField(default=False)
    accounts_all_details  = models.BooleanField(default=False)
    accounts_customer_details  = models.BooleanField(default=False)
    accounts_registry_details  = models.BooleanField(default=False)

    site_worker = models.BooleanField(default=False)
    normal_user =  models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    auth_provider = models.CharField(max_length=255, blank=False, null=False, default=AUTH_PROVIDERS.get('email'))
    assign = models.BooleanField(default=True, blank=True, null=True)
    USERNAME_FIELD = 'email'
    objects = CustomUserManager() 
    REQUIRED_FIELDS = []
    def __str__(self):
        return self.email
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
    

class BaseModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

class UserHoliday(models.Model):
    from_date = models.DateTimeField(default=timezone.now)
    to_date = models.DateTimeField(default=timezone.now)
    reason = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user',null=True,blank=True)
    
class FCMTokens(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_token')
    device_token = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True, null=True)