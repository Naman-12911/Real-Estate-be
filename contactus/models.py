from django.db import models
from account.models import BaseModel
# Create your models here.

class ContactUs(BaseModel):
    name = models.CharField(max_length=100,null=True,blank=True)
    message = models.CharField(max_length=100,null=True,blank=True)
    subject = models.CharField(max_length=100,null=True,blank=True)
