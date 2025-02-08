from django.db import models
from civilWorker.models import ConstructorProfile
# Create your models here.

class ConstProject(models.Model):
    constructor = models.ForeignKey(ConstructorProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.BigIntegerField(null=True, blank=True)
    unit = models.CharField(max_length=255, null=True, blank=True)
    rate = models.BigIntegerField(null=True, blank=True)
    discount = models.FloatField(null=True, blank=True)

class ConstBill(models.Model):
    bill_no = models.CharField(max_length=100, blank=True, null=True)
    project = models.ForeignKey(ConstProject, on_delete=models.CASCADE)
    amount = models.BigIntegerField(blank=True, null=True)
    total_amount = models.BigIntegerField(blank=True, null=True)
    prev_total_amount = models.BigIntegerField(blank=True, null=True)
    billed = models.BooleanField(default=False)

class BillsExported(models.Model):
    bill = models.FileField(null=True, blank=True)
    bill_no = models.CharField(max_length=255, null=True, blank=True)
    constructor_profile = models.ForeignKey(ConstructorProfile, models.CASCADE,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
