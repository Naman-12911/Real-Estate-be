from django.db import models
from account.models import User,BaseModel
from propertyStatus.models import UnitNo,Project,ProjectType
from profileSearch.models import PaymentStageDetail
import uuid
from django.utils import timezone
# Create your models here.

class DemandLetter(BaseModel):
    user = models.ForeignKey(User,models.CASCADE,null=True,blank=True)
    project_name = models.ForeignKey(Project,models.CASCADE)
    unit_number = models.ForeignKey(UnitNo,models.CASCADE)
    payment_stage = models.ForeignKey(PaymentStageDetail,models.CASCADE)
    date = models.DateField(null=True,blank=True)
    tax_percentage = models.CharField(max_length=100,null=True,blank=True)
    project_type = models.ForeignKey(ProjectType,models.CASCADE,null=True,blank=True,)
    deleted = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)
    #project_name = models.ForeignKey()

class ModeOfPayment(BaseModel):
    mode_of_payment = models.CharField(max_length=100,null=True,blank=True)
    def __str__(self):
        return self.mode_of_payment

class BankName(BaseModel):
    bank_name = models.CharField(max_length=100)
    drawn_on = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.bank_name

class Receipt(BaseModel):
    user = models.ForeignKey(User, models.CASCADE, null=True, blank=True)
    receipt_unique_id = models.CharField(max_length=15, unique=True,blank=True,null=True)
    receipt_date = models.DateField()
    project_name = models.ForeignKey(Project, models.CASCADE)
    unit_number = models.ForeignKey(UnitNo, models.CASCADE)
    payment_stage = models.ForeignKey(PaymentStageDetail, models.CASCADE)
    mode_of_payment = models.ForeignKey(ModeOfPayment, models.CASCADE)
    cheque_number = models.CharField(max_length=100, null=True, blank=True)
    transation_date = models.DateField(null=True, blank=True)  # date feild
    branch_name = models.CharField(max_length=100, null=True, blank=True)
    bank_name = models.ForeignKey(BankName, models.CASCADE, null=True, blank=True)
    by_bank = models.BooleanField(default=False)
    by_customer = models.BooleanField(default=False)
    cancel = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)
    delete = models.BooleanField(default=False)  # add this for to hide the recipt
    # created_at = models.DateTimeField(default=timezone.now)
    # updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Generate a unique 5-digit receipt ID if it's not already set
        if not self.receipt_unique_id:
            row = Receipt.objects.all()
            new_id = int(row.count()-447)+1
            # for i in row:
            #     try:
            #         if new_id==int(i.receipt_unique_id):
            #             new_id+=1
            #     except:
            #         pass
            new_id =  self.check_id(row, new_id)
            
            try:
                self.receipt_unique_id = str(new_id).zfill(5)
            except:
                self.receipt_unique_id = str(new_id+1).zfill(5)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.receipt_unique_id

    def check_id(self, row, new_id):
        for i in row:
            try:
                if new_id==int(i.receipt_unique_id):
                    new_id+=1
                    new_id = self.check_id(row, new_id)
            except:
                pass 
        return new_id
