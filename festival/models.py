from django.db import models
from account.models import BaseModel,User
# Create your models here.


class FestivalPost(BaseModel):
    user = models.ForeignKey(User,models.CASCADE,null=True,blank=True)
    image = models.ImageField(null=True,blank=True)
    file = models.FileField(null=True,blank=True)