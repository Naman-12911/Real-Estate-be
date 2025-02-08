from django.db import models
from datetime import datetime
from django.utils import timezone
from account.models import User
from propertyStatus.models import Project,Phase,ProjectType
from account.models import BaseModel

# Create your models here.



class MediumOfLead(BaseModel):
    medium = models.CharField(max_length=100,null=True,blank=True)
    user = models.ForeignKey(User,models.CASCADE,null=True,blank=True)

    def __str__(self):
        return self.medium
class LeadSource(BaseModel):
    user = models.ForeignKey(User,models.CASCADE,null=True,blank=True)
    medium_of_lead = models.ForeignKey(MediumOfLead,null=True,blank=True,on_delete=models.CASCADE)
    lead_source = models.CharField(max_length=100,null=True,blank=True)
    def __str__(self):
        return self.lead_source
    
class preferredLocation(BaseModel):
    preferred_location = models.CharField(max_length=100,null=True,blank=True)
    user = models.ForeignKey(User,models.CASCADE,null=True,blank=True)

    def __str__(self):
        return self.preferred_location
    

    
class ReasonSiteVisit(BaseModel):
    reason_of_site_visit = models.CharField(max_length=100,null=True,blank=True)
    user = models.ForeignKey(User,models.CASCADE,null=True,blank=True)

    def __str__(self):
        return self.reason_of_site_visit

class Budget(BaseModel):
    max_budget = models.CharField(max_length=100,null=True,blank=True)
    user = models.ForeignKey(User,models.CASCADE,null=True,blank=True)

    def __str__(self):
        return self.max_budget

class StatusLead(models.Model):
    user = models.ForeignKey(User,models.CASCADE,null=True,blank=True)
    status_lead = models.CharField(max_length=100,null=True,blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.status_lead

class Reason(BaseModel):
    reason_of_dump = models.CharField(max_length=100,null=True,blank=True)
    user = models.ForeignKey(User,models.CASCADE,null=True,blank=True)


    def __str__(self):
        return self.reason_of_dump

class ModeLead(models.Model):
    user = models.ForeignKey(User,models.CASCADE,null=True,blank=True)
    mode_lead = models.CharField(max_length=100,null=True,blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.mode_lead
     

class FbLeads(models.Model):
    user = models.ForeignKey(User,models.CASCADE,null=True,blank=True)
    assigned_to = models.ForeignKey(User, models.CASCADE, related_name='assigned_leads', null=True, blank=True)
    site_visit_to = models.ForeignKey(User,models.CASCADE,null=True,blank=True,related_name='site_visit_to')
    corporate_visit_to = models.ForeignKey(User,models.CASCADE,null=True,blank=True,related_name='corporate_visit_to')
    ad_id = models.CharField(max_length=250, null=True, blank=True)
    ad_name = models.CharField(max_length=250, null=True, blank=True)  # Here user can add add type
    adset_id = models.CharField(max_length=250, null=True, blank=True)
    adset_name = models.CharField(max_length=250, null=True, blank=True)
    campaign_id = models.CharField(max_length=250, null=True, blank=True)
    campaign_name = models.CharField(max_length=250, null=True, blank=True)

    city = models.CharField(max_length=250, null=True, blank=True)
    custom_disclaimer_responses = models.CharField(max_length=250, null=True, blank=True)
    created_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    company_name = models.CharField(max_length=100, null=True, blank=True)
    prices_available = models.JSONField(blank=True, null=True)
    raw = models.JSONField(null=True, blank=True)
    vehicle = models.CharField(max_length=100, null=True, blank=True)
    retailer_item_id = models.CharField(max_length=100, null=True, blank=True)
    fb_from = models.CharField(max_length=100, null=True, blank=True)

    full_name = models.CharField(max_length=255, null=True, blank=True)
    form_name = models.CharField(max_length=255, null=True, blank=True)
    form_id = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=100, null=True, blank=True)
    page_name = models.CharField(max_length=255, null=True, blank=True)
    form = models.CharField(max_length=255, null=True, blank=True)
    page_id = models.CharField(max_length=255, null=True, blank=True)
    job_title = models.CharField(max_length=255, null=True, blank=True)
    platform = models.CharField(max_length=255, null=True, blank=True)
    partner_name = models.CharField(max_length=255, null=True, blank=True)
    select_available_price = models.CharField(max_length=255, null=True, blank=True)
    alternative_number = models.CharField(max_length=100,null=True,blank=True)

    project_name = models.ManyToManyField(Project, blank=True)   
    #phase_name = models.ForeignKey(Phase, models.CASCADE, blank=True,null=True)
    project_type_name = models.ManyToManyField(ProjectType, blank=True)

    address = models.TextField(null=True,blank=True)
    occupation = models.CharField(max_length=100,null=True,blank=True)

    preferred_location = models.ForeignKey(preferredLocation,models.CASCADE,null=True,blank=True)
    preferred_location_other = models.CharField(max_length=100,null=True,blank=True)
    reasons_feedback = models.ForeignKey(Reason,models.CASCADE,null=True,blank=True)
    budget = models.ForeignKey(Budget,models.CASCADE,null=True,blank=True)

    
    lead_source = models.ForeignKey(LeadSource,models.CASCADE,null=True,blank=True)
    by_medium = models.ForeignKey(MediumOfLead,models.CASCADE,null=True,blank=True)
    corporate_visit_place = models.CharField(max_length=255, null=True, blank=True)

    dump_lead = models.BooleanField(default=False,null=True,blank=True)
    permanent_dump_lead = models.BooleanField(default=False,null=True,blank=True)
    site_visit = models.BooleanField(default=False,null=True,blank=True)
    booked = models.BooleanField(default=False,null=True,blank=True)
    corporate_visit = models.BooleanField(default=False,null=True,blank=True)
    intersted = models.BooleanField(default=False,null=True,blank=True)
    block_enquiry = models.BooleanField(default=False,null=True,blank=True)
    call_not_recevied = models.BooleanField(default=False,null=True,blank=True)
    do_not_call = models.BooleanField(default=False,null=True,blank=True)
    good_lead = models.BooleanField(default=False,null=True,blank=True)
    re_visit = models.BooleanField(default=False,null=True,blank=True)
    poor_lead = models.BooleanField(default=False,null=True,blank=True)
    may_be = models.BooleanField(default=False,null=True,blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now, null=True, blank=True)

    Type = models.CharField(max_length=255, blank=True, null=True)
    PhoneVerificationStatus = models.BooleanField(null=True,blank=True)
    Query = models.CharField(max_length=255, blank=True, null=True)
    CalledOn = models.DateTimeField(default=timezone.now)
    Time = models.TimeField(default=datetime.now().time(), blank=True, null=True)
    Duration = models.IntegerField(null=True,blank=True)
    CallStatus = models.BooleanField(null=True,blank=True)
    url = models.CharField(max_length=255, blank=True, null=True)
    receiveddate = models.DateField(default=datetime.now().date(), blank=True, null=True)
    interestedin = models.CharField(max_length=255, null=True, blank=True)
    responetype = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    EmailVerificationStatus = models.BooleanField(null=True, blank=True)
    Questionnaire = models.CharField(max_length=255, null=True, blank=True)
    productcode = models.CharField(max_length=255, null=True, blank=True)
    producttype = models.CharField(max_length=255, null=True, blank=True)
    IntentVerificationStatus = models.CharField(max_length=255, null=True, blank=True)
    LeadScore = models.CharField(max_length=255, null=True, blank=True)
    FollowupCurrentStatus = models.CharField(max_length=255, null=True, blank=True)
    ProdType = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    project = models.CharField(max_length=255, null=True, blank=True)
    rescom = models.CharField(max_length=255, null=True, blank=True)
    Bhk = models.IntegerField(null=True, blank=True)
    PropertySnapshot = models.CharField(max_length=255, null=True, blank=True)
    ParentProductDetails = models.CharField(max_length=255, null=True, blank=True)
    SetIsParentProductTypeResponse = models.CharField(max_length=255, null=True, blank=True)
    CompactLabel = models.CharField(max_length=255, null=True, blank=True)
    Duplicate = models.BooleanField(null=True, blank=True)

    property_title = models.CharField(max_length=255, null=True, blank=True)
    purpose_of_property = models.CharField(max_length=255, null=True, blank=True)
    property = models.CharField(max_length=255, null=True, blank=True)
    locality = models.CharField(max_length=255, null=True, blank=True)
    details = models.CharField(max_length=255, null=True, blank=True)
    
    service_type = models.CharField(max_length=255, null=True, blank=True)
    property_type = models.CharField(max_length=255, null=True, blank=True)
    seller_id = models.IntegerField(null=True,blank=True)
    seller_name = models.CharField(max_length=255, null=True, blank=True)
    configuration = models.CharField(max_length=255, null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    feedback = models.CharField(max_length=250,null=True,blank=True)
    # enquiry date for corporate visit.
    enquiry_date = models.DateField(null=True,blank=True)

    status_acc_admin = models.CharField(max_length=100,null=True,blank=True)
    feedback_acc_admin = models.CharField(max_length=100,null=True,blank=True)
    expected_booking = models.BooleanField(default=False)
    expected_booking_date = models.DateField(null=True,blank=True)
    customer_ref_name = models.CharField(max_length=255,null=True,blank=True)

    class Meta:
        verbose_name = "All lead"
        verbose_name_plural = "All leads"

        
class LeadEdit(models.Model):
    user = models.ForeignKey(User,models.CASCADE,null=True,blank=True)
    fb_leads = models.ForeignKey(FbLeads,models.CASCADE,null=True,blank=True)
    visited_by = models.ForeignKey(User,models.CASCADE,null=True,blank=True,related_name="VisitedBy")
    mode = models.ForeignKey(ModeLead,models.CASCADE,null=True,blank=True)
    upload_file = models.FileField(null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    status_of_lead = models.ForeignKey(StatusLead,models.CASCADE, null=True,blank=True)
    reason_for_dump = models.ForeignKey(Reason,models.CASCADE,null=True,blank=True)
    # feilds for the Booked only
    project = models.ForeignKey(Project,models.CASCADE,null=True,blank=True)
    square_fit = models.CharField(max_length=100,null=True,blank=True)
    date_of_booking = models.DateField(null=True,blank=True)
    purchased_location = models.CharField(max_length=100,null=True,blank=True)
    visit_date = models.DateField(null=True,blank=True)
    # visited_by = models.ForeignKey(User,models.CASCADE,null=True,blank=True,related_name="VisitedBy")
    mobile_number = models.BigIntegerField(null=True,blank=True)
    status_of_lead_warm_hot_cold = models.CharField(max_length=100,null=True,blank=True)

    visit_number = models.CharField(max_length=100,null=True,blank=True)
    next_schedule_date = models.DateField(blank=True,null=True,verbose_name="Next Schedule Date")
    next_schedule_mode = models.ForeignKey(ModeLead, models.CASCADE, null=True,blank=True,related_name="next_shedule_mode_of_the_cutomer")
    enquiry_date = models.DateField(null=True,blank=True)
    reason_for_site_visit = models.ForeignKey(ReasonSiteVisit,models.CASCADE,null=True,blank=True)

    created_at = models.DateTimeField(default=timezone.now,null=True,blank=True)
    updated_at = models.DateTimeField(default=timezone.now,null=True,blank=True)
    site_visits = models.BigIntegerField(default=0, null=True, blank=True)
    feedback = models.CharField(max_length=255,null=True,blank=True)

    class Meta:
        verbose_name = "Discussion"
        verbose_name_plural = "Discussions"

class NotificationStore(models.Model):
    sent_to = models.ForeignKey(User,models.CASCADE,null=True,blank=True)
    head = models.CharField(max_length=250,null=True,blank=True)
    message = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(default=timezone.now,null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True,blank=True)
    seen = models.BooleanField(default=False, null=True, blank=True)
    