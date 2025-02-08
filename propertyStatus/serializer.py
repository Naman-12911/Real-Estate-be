from rest_framework import serializers
from account.models import User
from .models import *


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class ProjectTypeSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='projects.project_name', read_only=True)
    class Meta:
        model = ProjectType
        fields = "__all__"
    

class UnitNoSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='projects.project_name', read_only=True)
    class Meta:
        model = UnitNo
        fields = '__all__'

class PhaseSerializer(serializers.ModelSerializer):
    unit_number = serializers.CharField(source='unit.unit_no', read_only=True)
    class Meta:
        model = Phase
        fields = '__all__'
    def to_representation(self, instance):
        response = super().to_representation(instance)
       
        response['unit'] = UnitNoSerializer(instance.unit).data

        return response


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = '__all__'

class TaxTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxType
        fields = '__all__'




class ProjectDocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectDocumentType
        fields = '__all__'


class ProjectDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectDocument
        fields = '__all__'
    def to_representation(self, instance):
        response = super().to_representation(instance)
       
        response['project_document'] = ProjectSerializer(instance.project_document).data
        response['document_type'] = ProjectDocumentTypeSerializer(instance.document_type).data

        return response