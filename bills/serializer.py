from rest_framework import fields, serializers
from .models import *

class ConstProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConstProject
        fields = '__all__'

class ConstBillSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConstBill
        fields = '__all__'

class BillsExportedSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillsExported
        fields = ['bill', 'constructor_profile', 'created_at','bill_no'] 