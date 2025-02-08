from rest_framework import fields, serializers
from social.models import *
from social.serializer import LeadEditSerializer
from django.utils import timezone
from datetime import datetime, timedelta
from social.models import LeadEdit


    
class SiteVisitSerializer(serializers.ModelSerializer):
    leads = LeadEditSerializer(many=True)

    class Meta:
        model = LeadEdit
        fields = ['visit_number', 'leads']