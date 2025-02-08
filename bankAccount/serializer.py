from rest_framework import fields, serializers
from .models import *
from django.utils import timezone


class BankNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankName
        fields = '__all__'

   



class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = '__all__'

   
