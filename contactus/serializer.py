from rest_framework import fields, serializers
from .models import *


class ContactUsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ContactUs
        fields = '__all__'

   