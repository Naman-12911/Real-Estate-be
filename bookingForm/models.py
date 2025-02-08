from django.db import models
from propertyStatus.models import Project,ProjectType,UnitNo,TaxType
from account.models import BaseModel,User
# Create your models here.


class AllDocument(BaseModel):
    document = models.CharField(max_length=100,blank=True,null=True)

    def __str__(self):
        return self.document


LOAN_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]

GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Transgender', 'Transgender'),
    ]

class Booking(BaseModel):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    project_name = models.ForeignKey(Project,models.CASCADE,null=True,blank=True)
    type_name = models.ForeignKey(ProjectType,models.CASCADE,null=True,blank=True)
    unit_no = models.ForeignKey(UnitNo,models.CASCADE,null=True,blank=True)
    tax_type = models.ForeignKey(TaxType,models.CASCADE,null=True,blank=True)
    tax_percent = models.CharField(blank=True,max_length=100,null=True)
    unit_cost = models.FloatField(max_length=100,blank=True)

    # all costings
    discount = models.IntegerField(default=0)
    maintainance_charges_2_year = models.IntegerField(default=0)
    external_electrical_charges = models.IntegerField(default=0)
    water_connection_charges = models.IntegerField(default=0)
    corner_plot_charges = models.IntegerField(default=0)
    park_face_charges = models.IntegerField(default=0)
    registry_extra_charges = models.IntegerField(default=0)
    mutation_charges = models.IntegerField(default=0)
    socity_maintaince_charges = models.IntegerField(default=0)
    govt_extra_charges = models.IntegerField(default=0)
    other_charges = models.IntegerField(default=0)
    wide_road_facing_charges = models.IntegerField(default=0)
    cost_payable_to_company = models.FloatField(default=0)

    profile_picture = models.ImageField(blank=True,null=True)
    interst_rate = models.CharField(max_length=100,blank=True)
    Annual_income = models.CharField(max_length=100,blank=True)
    booking_amount = models.IntegerField(default=0)
    application_date = models.DateField(blank=True,null=True)
    gender = models.CharField(max_length=100,blank=True,choices=GENDER_CHOICES)
    loan_required = models.CharField(max_length=100,choices=LOAN_CHOICES,null=True,blank=True)
    mutation_date = models.DateField(null=True,blank=True)
    mutation_True_false = models.BooleanField(default=False)
    registry_date = models.DateField(null=True,blank=True)
    registry_true_false = models.BooleanField(default=False)
    posession_date = models.DateField(null=True,blank=True)
    posession_true_false = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)

SOWODO = [
        ('S/O', 'S/O'),
        ('W/O', 'W/O'),
        ('D/O', 'D/O'),
    ]

class PersonalDeatils(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    booking = models.ForeignKey(Booking,models.CASCADE,null=True,blank=True)
    so_wo_do = models.CharField(max_length=100,null=True,blank=True,choices=SOWODO)
    sowodo = models.CharField(max_length=100,null=True,blank=True)
    applicant_name = models.CharField(max_length=100,null=True,blank=True)
   
    persent_address = models.CharField(max_length=100,null=True,blank=True)
    permanent_address = models.CharField(max_length=100,null=True,blank=True)
    pin_code = models.CharField(max_length=100,null=True,blank=True)
    date_of_birth = models.DateField(max_length=100,null=True,blank=True)
    age = models.CharField(max_length=100,null=True,blank=True)
    mobile_number = models.CharField(max_length=100,null=True,blank=True)
    residence_address = models.CharField(max_length=100,null=True,blank=True)
    email_address = models.CharField(max_length=100,null=True,blank=True)
    adhar_no = models.CharField(max_length=100,null=True,blank=True)
    nationality = models.CharField(max_length=100,null=True,blank=True)
    pan_number = models.CharField(max_length=100,null=True,blank=True)
    profession = models.CharField(max_length=100,null=True,blank=True)
    fax_number = models.CharField(max_length=100,null=True,blank=True)
    matial_status = models.CharField(max_length=100,null=True,blank=True)
    document = models.ImageField(null=True,blank=True)
    document_name = models.ForeignKey(AllDocument,models.CASCADE,null=True,blank=True)
    deleted = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)

    def __str__(self):
        user_str = str(self.user) if self.user else ""
        applicant_name_str = self.applicant_name if self.applicant_name else ""
        return f"{user_str} - {applicant_name_str}"
    class Meta:
        verbose_name_plural = "Personal Details"


class CoApplicantForm(BaseModel):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    personal_deatils = models.ForeignKey(PersonalDeatils,on_delete=models.CASCADE,null=True,blank=True)
    profile_picture = models.ImageField(blank=True,null=True)
    name = models.CharField(max_length=100,blank=True,null=True)
    date_of_birth = models.CharField(max_length=100,blank=True,null=True)
    age = models.CharField(max_length=100,blank=True,null=True)
    present_address = models.CharField(max_length=100,blank=True,null=True)
    permanent_address = models.CharField(max_length=100,blank=True,null=True)
    residence_address = models.CharField(max_length=100,blank=True,null=True)
    email_address = models.CharField(max_length=100,blank=True,null=True)
    adhar_no = models.CharField(max_length=100,blank=True,null=True)
    nationality = models.CharField(max_length=100,blank=True,null=True)
    pan_number = models.CharField(max_length=100,blank=True,null=True)
    profession = models.CharField(max_length=100,blank=True,null=True)
    fax_number = models.CharField(max_length=100,blank=True,null=True)
    matial_status = models.CharField(max_length=100,blank=True,null=True)
    deleted = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)

class CancelBooking(models.Model):
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    unit_no = models.ForeignKey(UnitNo,models.CASCADE,null=True,blank=True)
    booking = models.ForeignKey(Booking,models.CASCADE,null=True,blank=True)
    cancellation_date = models.DateTimeField(auto_now_add=True)
    total_refund_amt = models.FloatField(default=0, null=True, blank=True)
    cancellation_reason = models.TextField(null=True, blank=True)
    remaining_bal = models.FloatField(default=0, null=True, blank=True)
    deleted = models.BooleanField(default=False)

class CancelRefund(models.Model):
    reciept_no = models.CharField(max_length=20, blank=True, null=True)
    cancelbooking = models.ForeignKey(CancelBooking, on_delete=models.CASCADE, blank=True, null=True)
    refunded_amt = models.FloatField(default=0)
    mode_of_refund = models.CharField(max_length=100, null=True, blank=True)
    cheque_no = models.CharField(max_length=100, null=True, blank=True)
    bank_name = models.CharField(max_length=50, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)