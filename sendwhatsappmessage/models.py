from django.db import models
from propertyStatus.models import Project,ProjectType
from account.models import BaseModel,User
from tinymce.models import HTMLField
from django.utils import timezone
# Create your models here.


class WhatsAppMessage(BaseModel):
    user = models.ForeignKey(User,models.CASCADE,null=True,blank=True)
    project_name = models.ForeignKey(Project,models.CASCADE,null=True,blank=True)
    project_type = models.ForeignKey(ProjectType,models.CASCADE,null=True,blank=True)
    all_project = models.BooleanField(default=False)
    description = HTMLField()


class TrackWhatAppMessage(BaseModel):
    user = models.ForeignKey(User,models.CASCADE,null=True,blank=True)
    phone_number = models.BigIntegerField(null=True,blank=True)
    time = models.TimeField(null=True,blank=True)
    
    def save(self, *args, **kwargs):
        # Check if time field is not set
        if not self.time:
            # Set the time field to the current time
            self.time = timezone.now().time()
        super().save(*args, **kwargs)

