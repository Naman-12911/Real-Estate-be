from django.db import models
from account.models import BaseModel,User
from bookingForm.models import PersonalDeatils

class PaymentStageDetail(BaseModel):
    user = models.ForeignKey(User,models.CASCADE,null=True)
    stage_name = models.CharField(max_length=100,blank=True,null=True)
    personal_deatils = models.ForeignKey(PersonalDeatils,models.CASCADE,blank=True,null=True)
    step_no = models.CharField(max_length=100,blank=True)
    payable_date = models.DateField(null=True,blank=True)
    paybale_amount = models.CharField(max_length=100,blank=True,null=True)
    deleted = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)


class PaymentReceipts(BaseModel):
    user = models.ForeignKey(User,models.CASCADE,null=True,blank=True)
    stage_deatils = models.ForeignKey(PaymentStageDetail, on_delete=models.CASCADE)
    receipent_number = models.CharField(max_length=100,null=True,blank=True)
    mode = models.CharField(max_length=100,null=True,blank=True)
    amount_recived = models.CharField(max_length=100,null=True,blank=True)
    date = models.CharField(max_length=100,null=True,blank=True)
    deleted = models.BooleanField(default=False)

class RemiderDemandInformation(BaseModel):
    user = models.ForeignKey(User,models.CASCADE,null=True,blank=True)
    payment_receipts_stage = models.ForeignKey(PaymentReceipts, on_delete=models.CASCADE)
    deplay = models.CharField(max_length=100,blank=True)
    interst = models.FloatField(default=0)
    amount_to_be_paid = models.FloatField(default=0)
    deleted = models.BooleanField(default=False)