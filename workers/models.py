from django.db import models
from account.models import BaseModel,User
from propertyStatus.models import Project,UnitNo
# Create your models here.

class SiteWorkers(BaseModel):
    project_name = models.ForeignKey(Project,models.CASCADE,null=True,blank=True)
    unit_no = models.ForeignKey(UnitNo,models.CASCADE,null=True,blank=True)
    worker_update_date = models.DateTimeField(null=True, blank=True)

    worker_stage1 = models.BooleanField(default=False)
    worker_stage2 = models.BooleanField(default=False)
    worker_stage3 = models.BooleanField(default=False)
    worker_stage4 = models.BooleanField(default=False)
    worker_stage5 = models.BooleanField(default=False)
    worker_stage6 = models.BooleanField(default=False)
    worker_stage7 = models.BooleanField(default=False)

    admin_stage1 = models.BooleanField(default=False)
    admin_stage2 = models.BooleanField(default=False)
    admin_stage3 = models.BooleanField(default=False)
    admin_stage4 = models.BooleanField(default=False)
    admin_stage5 = models.BooleanField(default=False)
    admin_stage6 = models.BooleanField(default=False)
    admin_stage7 = models.BooleanField(default=False)


    delay_stage1 = models.BooleanField(default=False)
    delay_stage2 = models.BooleanField(default=False)
    delay_stage3 = models.BooleanField(default=False)
    delay_stage4 = models.BooleanField(default=False)
    delay_stage5 = models.BooleanField(default=False)
    delay_stage6 = models.BooleanField(default=False)
    delay_stage7 = models.BooleanField(default=False)
    
    deleted =models.BooleanField(default=False)
    # site visit set target for a stage.
    accept =  models.BooleanField(default=False)  # accept by the site worker
    reject =  models.BooleanField(default=False)  # accept by the site worker
    target =  models.BooleanField(default=False)  # set by the admin
    admin_target_date = models.DateField(null=True,blank=True)
    worker_target_date = models.DateField(null=True,blank=True)
    stage_name = models.CharField(max_length=100,null=True,blank=True)

class MonthlyExpense(BaseModel):
    siteworker = models.ForeignKey(SiteWorkers,models.CASCADE,null=True,blank=True)
    money = models.FloatField(blank=True, null=True)
    money_rec = models.FloatField(default=0,blank=True, null=True)
    stage = models.CharField(max_length=50, blank=True, null=True)
    update_by = models.CharField(max_length=50, blank=True, null=True)
    deleted = models.BooleanField(default=False)
