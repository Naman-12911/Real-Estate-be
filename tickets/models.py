from django.db import models
from account.models import BaseModel,User
from propertyStatus.models import Project
# Create your models here.


class Ticket(BaseModel):
    user = models.ForeignKey(User,models.CASCADE,null=True,blank=True)
    phone_number = models.IntegerField(null=True,blank=True)
    property_type = models.CharField(max_length=100,null=True,blank=True)
    # project_name = models.CharField(max_length=100,null=True,blank=True)
    unit_number = models.CharField(max_length=100,null=True,blank=True)
    query = models.TextField(blank=True)
    email = models.EmailField(null=True,blank=True)
    name = models.CharField(max_length=100,null=True,blank=True)
    solved = models.BooleanField(default=False)
    year_of_purchase = models.CharField(max_length=100,null=True,blank=True)
    possession_recieved = models.BooleanField(default=False)
    possession_date = models.CharField(max_length=100,null=True,blank=True)
    project_name = models.ForeignKey(Project,models.CASCADE,null=True,blank=True)

    # admin messages ---
    admin_message = models.CharField(max_length=100,null=True,blank=True)
    image = models.ImageField(blank=True,null=True)
    image1 = models.ImageField(blank=True,null=True)
    image2 = models.ImageField(blank=True,null=True)
    file = models.FileField(blank=True,null=True)


    def __str__(self):
        return self.email