from rest_framework import fields, serializers
from .models import *
from social.serializer import LeadEditSerializer
from django.utils import timezone


class SendMailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SendMailToClients
        fields = '__all__'

class MailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MailTemplate
        fields = '__all__'
