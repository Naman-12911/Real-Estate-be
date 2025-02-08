from django.db import models
from account.models import BaseModel,User
from bookingForm.models import Booking
# Create your models here.

class ClientLoanProfile(BaseModel):
    user  = models.ForeignKey(User,models.CASCADE)
    bookings  = models.ForeignKey(Booking,models.CASCADE)
    bank_name = models.CharField(max_length=100)
    bank_address = models.CharField(max_length=100)
    bank_ifsc = models.CharField(max_length=100)
    loan_file_no = models.CharField(max_length=100)
    loan_date = models.DateField()
    loan_amount_sanctioned = models.CharField(max_length=100)
    excutive_name = models.CharField(max_length=100)
    excutive_number = models.CharField(max_length=100)
    status_active_inactive = models.CharField(max_length=100)
    loan_approval_date = models.DateField()
    margin_amount = models.CharField(max_length=100)
