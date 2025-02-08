from django.db import models
from account.models import BaseModel
# Create your models here.

class Project(BaseModel):
    project_name = models.CharField(max_length=100)
    address = models.CharField(max_length=100,null=True,blank=True)
    ecternal_electric_charges = models.CharField(max_length=100,null=True,blank=True)
    water_connection_charges = models.CharField(max_length=100,null=True,blank=True)
    mutation_charges = models.CharField(max_length=100,null=True,blank=True)
    maintaince_charges_2_year = models.CharField(max_length=100,null=True,blank=True)
    society_charges = models.CharField(max_length=100,null=True,blank=True)
    
    def __str__(self):
        return self.project_name
    
class ProjectType(BaseModel):
    projects = models.ForeignKey(Project,models.CASCADE)
    property_type = models.CharField(max_length=100)
    def __str__(self):
        return self.property_type
    
class UnitNo(BaseModel):
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

    def __str__(self):
        return self.unit_no

class Phase(BaseModel):
    unit = models.ForeignKey(UnitNo,models.CASCADE,null=True,blank=True)
    projects = models.ForeignKey(Project,models.CASCADE,null=True,blank=True)
    phase_name = models.CharField(max_length=100)

    def __str__(self):
        return self.phase_name
    

class Status(BaseModel):
    status_name = models.CharField(max_length=100)
    def __str__(self):
        return self.status_name
    class Meta:
        verbose_name = "Status"
        verbose_name_plural = "Statuses"


class TaxType(BaseModel):
    tax_type = models.CharField(max_length=100)
    tax_percent = models.IntegerField(default=0)
    def __str__(self):
        return self.tax_type


class ProjectDocumentType(BaseModel):
    document_of = models.CharField(max_length=100,null=True,blank=True)

    def __str__(self):
        return self.document_of

class ProjectDocument(BaseModel):
    project_document= models.ForeignKey(Project,models.CASCADE)
    document_type = models.ForeignKey(ProjectDocumentType,models.CASCADE)
    date = models.DateField(null=True,blank=True)
    document_file = models.FileField(null=True,blank=True)
