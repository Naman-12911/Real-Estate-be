from django.db import models
from account.models import BaseModel,User
from propertyStatus.models import Project
# Create your models here.


class Faq(BaseModel):
    user = models.ForeignKey(User,models.CASCADE)
    project_faq = models.ForeignKey(Project,models.CASCADE)
    questions = models.CharField(max_length=100,blank=True)
    answer = models.TextField()
    image = models.ImageField(null=True,blank=True)
    video = models.FileField(null=True,blank=True)

    def __str__(self):
        return self.questions