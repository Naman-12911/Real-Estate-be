from django.db import models
from account.models import User,BaseModel
from propertyStatus.models import UnitNo
from  propertyStatus.models import Project
# Create your models here.

class ConstructorUnitNo(BaseModel):
    projects = models.ForeignKey(Project,models.CASCADE)
    unit_no = models.CharField(max_length=100)
    available = models.BooleanField(default=False)
    booked = models.BooleanField(default=False)
    hold = models.BooleanField(default=False)
    east_by = models.CharField(max_length=100,blank=True)
    west_by = models.CharField(max_length=100,blank=True)
    north_by = models.CharField(max_length=100,blank=True)
    south_by = models.CharField(max_length=100,blank=True)
    unit_cost = models.IntegerField(null=True)
    square_fit = models.CharField(max_length=100,null=True,blank=True)
    rate = models.FloatField(null=True,blank=True)
    delete = models.BooleanField(default=False)

    def __str__(self):
        return self.unit_no

class Miscellaneous(BaseModel):
    user = models.ForeignKey(User,models.CASCADE,null=True,blank=True)
    unit = models.ForeignKey(ConstructorUnitNo,models.CASCADE,blank=True,null=True)
    title = models.CharField(max_length=100,null=True,blank=True)
    amount = models.FloatField(null=True,blank=True)
    delete = models.BooleanField(default=False)
    prev_bill = models.BooleanField(default=False)

    def __str__(self):
        return str(self.amount)

class Remarks(BaseModel):
    user = models.ForeignKey(User,models.CASCADE,null=True,blank=True)
    unit = models.ForeignKey(ConstructorUnitNo,models.CASCADE,blank=True,null=True)
    title = models.CharField(max_length=100,null=True,blank=True)
    delete = models.BooleanField(default=False)



class Bills(BaseModel):
    user = models.ForeignKey(User,models.CASCADE,null=True,blank=True)
    unit = models.ForeignKey(ConstructorUnitNo,models.CASCADE,blank=True,null=True)
    title = models.CharField(max_length=100,null=True,blank=True)
    image = models.ImageField(null=True,blank=True,upload_to="media/bills/")
    delete = models.BooleanField(default=False)

class ConstructorProfile(BaseModel):
    user = models.ForeignKey(User,models.CASCADE,null=True,blank=True)
    hsncode = models.CharField(max_length=100,null=True,blank=True)
    bank_name = models.CharField(max_length=100,null=True,blank=True)
    branch = models.CharField(max_length=100,null=True,blank=True)
    gst = models.CharField(max_length=100,null=True,blank=True)
    address = models.CharField(max_length=100,null=True,blank=True)
    discount = models.FloatField(null=True,blank=True)
    bank_no = models.BigIntegerField(null=True,blank=True)
    ifsc_code = models.CharField(max_length=100,null=True,blank=True)
    name = models.CharField(max_length=100,null=True,blank=True)
    unit = models.ManyToManyField(ConstructorUnitNo,blank=True, null=True)
    rate = models.FloatField(null=True,blank=True)
    profile = models.CharField(max_length=255, blank=True, null=True)
    delete = models.BooleanField(default=False)
# save the excel  files and pdf files.

class ExcelFilesCivilStages(BaseModel):
    file = models.FileField(null=True,blank=True)
    unit = models.ManyToManyField(ConstructorUnitNo,blank=True)
    prev_bill = models.JSONField(null=True,blank=True)
    constructor_profile = models.ForeignKey(ConstructorProfile, models.CASCADE,null=True,blank=True)
    downloaded_sucessfully = models.BooleanField(default=False)
    bill_no = models.CharField(max_length=100, blank=True, null=True)

class InvoiceCivilStages(BaseModel):
    invoice = models.FileField(null=True,blank=True)
    unit = models.ManyToManyField(ConstructorUnitNo,blank=True)
    bill_no = models.CharField(max_length=100, blank=True, null=True)
    constructor_profile = models.ForeignKey(ConstructorProfile, models.CASCADE,null=True,blank=True)

class CivilStatges(BaseModel):
    user = models.ForeignKey(User,models.CASCADE,null=True,blank=True)
    unit = models.ForeignKey(ConstructorUnitNo,models.CASCADE,blank=True,null=True)
    miscellaneous_expense = models.ManyToManyField(Miscellaneous,blank=True)
    constructor_profile = models.ForeignKey(ConstructorProfile, models.CASCADE,null=True,blank=True)
    remark = models.ForeignKey(Remarks,models.CASCADE,blank=True,null=True)
    bill = models.ForeignKey(Bills,models.CASCADE,blank=True,null=True)
    # stage 1 feilds
    stage1 = models.CharField(max_length=100,null=True,blank=True,default='Piles')
    completed_stage_1 = models.BooleanField(default=False)
    target_date_stage_1 = models.DateField(null=True,blank=True)
    completed_date_stage_1 = models.DateField(null=True,blank=True)
    completed_before_hand_stage_1 = models.BooleanField(default=False)
    percentage_stage_1 = models.FloatField(default=10,null=True)
    updated_percentage_stage_1 = models.CharField(max_length=100,null=True,blank=True)
    bill_downloaded_1 = models.BooleanField(default=False)
    # stage 2
    stage2 = models.CharField(max_length=100,null=True,blank=True,default='Plinth')
    completed_stage_2 = models.BooleanField(default=False)
    target_date_stage_2 = models.DateField(null=True,blank=True)
    completed_date_stage_2 = models.DateField(null=True,blank=True)
    completed_before_hand_stage_2 = models.BooleanField(default=False)
    percentage_stage_2 = models.FloatField(default=10,null=True)
    updated_percentage_stage_2 = models.CharField(max_length=100,null=True,blank=True)
    bill_downloaded_2 = models.BooleanField(default=False)


    # stage 3
    stage3 = models.CharField(max_length=100,null=True,blank=True,default='GF Slab')
    completed_stage_3 = models.BooleanField(default=False)
    target_date_stage_3 = models.DateField(null=True,blank=True)
    completed_date_stage_3 = models.DateField(null=True,blank=True)
    completed_before_hand_stage_3 = models.BooleanField(default=False)
    percentage_stage_3 = models.FloatField(default=10,null=True)
    updated_percentage_stage_3 = models.CharField(max_length=100,null=True,blank=True)
    bill_downloaded_3 = models.BooleanField(default=False)

    # stage 4
    stage4 = models.CharField(max_length=100,null=True,blank=True,default='FF Slab')
    completed_stage_4 = models.BooleanField(default=False)
    target_date_stage_4 = models.DateField(null=True,blank=True)
    completed_date_stage_4 = models.DateField(null=True,blank=True)
    completed_before_hand_stage_4 = models.BooleanField(default=False)
    percentage_stage_4 = models.FloatField(default=10,null=True)
    updated_percentage_stage_4 = models.CharField(max_length=100,null=True,blank=True)
    bill_downloaded_4 = models.BooleanField(default=False)

    # stage 5
    stage5 = models.CharField(max_length=100,null=True,blank=True,default='Tower/Mummty')
    completed_stage_5 = models.BooleanField(default=False)
    target_date_stage_5 = models.DateField(null=True,blank=True)
    completed_date_stage_5 = models.DateField(null=True,blank=True)
    completed_before_hand_stage_5 = models.BooleanField(default=False)
    percentage_stage_5 = models.FloatField(default=5,null=True)
    updated_percentage_stage_5 = models.CharField(max_length=100,null=True,blank=True)
    bill_downloaded_5 = models.BooleanField(default=False)

    # stage 6
    stage6 = models.CharField(max_length=100,null=True,blank=True,default='Brick Work')
    completed_stage_6 = models.BooleanField(default=False)
    target_date_stage_6 = models.DateField(null=True,blank=True)
    completed_date_stage_6 = models.DateField(null=True,blank=True)
    completed_before_hand_stage_6 = models.BooleanField(default=False)
    percentage_stage_6 = models.FloatField(default=10,null=True)
    updated_percentage_stage_6 = models.CharField(max_length=100,null=True,blank=True)
    bill_downloaded_6 = models.BooleanField(default=False)

    #stage 7
    stage7 = models.CharField(max_length=100,null=True,blank=True,default='Plastring')
    completed_stage_7 = models.BooleanField(default=False)
    target_date_stage_7 = models.DateField(null=True,blank=True)
    completed_date_stage_7 = models.DateField(null=True,blank=True)
    completed_before_hand_stage_7 = models.BooleanField(default=False)
    percentage_stage_7 = models.FloatField(default=15,null=True)
    updated_percentage_stage_7 = models.CharField(max_length=100,null=True,blank=True)
    bill_downloaded_7 = models.BooleanField(default=False)

    # stage 8
    stage8 = models.CharField(max_length=100,null=True,blank=True,default='Flooring')
    completed_stage_8 = models.BooleanField(default=False)
    target_date_stage_8 = models.DateField(null=True,blank=True)
    completed_date_stage_8 = models.DateField(null=True,blank=True)
    completed_before_hand_stage_8 = models.BooleanField(default=False)
    percentage_stage_8 = models.FloatField(default=10,null=True)
    updated_percentage_stage_8 = models.CharField(max_length=100,null=True,blank=True)
    bill_downloaded_8 = models.BooleanField(default=False)

    # stage 9
    stage9 = models.CharField(max_length=100,null=True,blank=True,default='Double Coat Putty & Double Coat Putty')
    completed_stage_9 = models.BooleanField(default=False)
    target_date_stage_9 = models.DateField(null=True,blank=True)
    completed_date_stage_9 = models.DateField(null=True,blank=True)
    completed_before_hand_stage_9 = models.BooleanField(default=False)
    percentage_stage_9 = models.FloatField(default=5,null=True)
    updated_percentage_stage_9 = models.CharField(max_length=100,null=True,blank=True)
    bill_downloaded_9 = models.BooleanField(default=False)

    # stage 10
    stage10 = models.CharField(max_length=100,null=True,blank=True,default='Pre Final')
    completed_stage_10 = models.BooleanField(default=False)
    target_date_stage_10 = models.DateField(null=True,blank=True)
    completed_date_stage_10 = models.DateField(null=True,blank=True)
    completed_before_hand_stage_10 = models.BooleanField(default=False)
    percentage_stage_10 = models.FloatField(default=10,null=True)
    updated_percentage_stage_10 = models.CharField(max_length=100,null=True,blank=True)
    bill_downloaded_10 = models.BooleanField(default=False)

    # stage 11
    stage11 = models.CharField(max_length=100,null=True,blank=True,default='Hand over')
    completed_stage_11 = models.BooleanField(default=False)
    target_date_stage_11 = models.DateField(null=True,blank=True)
    completed_date_stage_11 = models.DateField(null=True,blank=True)
    completed_before_hand_stage_11 = models.BooleanField(default=False)
    percentage_stage_11 = models.FloatField(default=5,null=True)
    updated_percentage_stage_11 = models.CharField(max_length=100,null=True,blank=True)
    bill_downloaded_11 = models.BooleanField(default=False)
    delete = models.BooleanField(default=False)
    # def __str__(self):
    #     return str(self.unit)
    



