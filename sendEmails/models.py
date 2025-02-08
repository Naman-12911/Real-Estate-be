from django.db import models
from propertyStatus.models import Project,ProjectType
from account.models import BaseModel,User
from tinymce.models import HTMLField
from django.utils import timezone
# Create your models here .

class SendMailToClients(BaseModel):
    user = models.ForeignKey(User,models.CASCADE, null=True,blank=True)
    project_name = models.ForeignKey(Project,models.CASCADE, null=True,blank=True)
    project_type = models.ForeignKey(ProjectType,models.CASCADE, null=True,blank=True)
    name = models.CharField(max_length=100,null=True,blank=True)
    subject_line = models.CharField(max_length=100,null=True,blank=True)
    mail = models.TextField(null=True,blank=True)
    all_projects = models.BooleanField(default=False)

    # def __str__(self):
    #     return self.project_name

class MailTemplate(BaseModel):
    project_name = models.ForeignKey(Project,models.CASCADE, null=True,blank=True)
    project_type = models.ForeignKey(ProjectType,models.CASCADE, null=True,blank=True)
    mail = models.TextField(null=True,blank=True)
    all_projects = models.BooleanField(default=False)

    # def __str__(self):
    #     return self.project__project__name
