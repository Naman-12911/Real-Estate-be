from django.db import models
from account.models import BaseModel,User
from bookingForm.models import PersonalDeatils
# Create your models here.


class BankName(BaseModel):
    bank_name = models.CharField(max_length=100,blank=True)
    def __str__(self):
        return self.bank_name

class BankAccount(BaseModel):
    bank_name = models.ForeignKey(BankName,models.CASCADE,null=True)
    personal_deatils = models.ForeignKey(PersonalDeatils,models.CASCADE,null=True)
    bank_address = models.CharField(max_length=100,blank=True)
    bank_ifsc = models.CharField(max_length=100,blank=True)
    loan_file_no = models.CharField(max_length=100,blank=True)
    loan_date = models.DateField(null=True,blank=True)
    loan_account_number = models.CharField(max_length=100,blank=True)
    loan_amount_sanctioned= models.CharField(max_length=100,blank=True)
    executive_name= models.CharField(max_length=100,blank=True)
    executive_number= models.CharField(max_length=100,blank=True)
    status = models.CharField(max_length=100,blank=True)
    margin_amount = models.CharField(max_length=100,blank=True)
