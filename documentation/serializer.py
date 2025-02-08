from rest_framework import serializers
from account.models import User
from .models import *
from propertyStatus.models import UnitNo,Project
from profileSearch.models import PaymentStageDetail
from profileSearch.serializer import PaymentStageDetailSerializer
from propertyStatus.serializer import UnitNoSerializer,ProjectSerializer,ProjectTypeSerializer



class DemandLetterSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandLetter
        fields = '__all__'
    def get_user(self, instance):
        return instance.user.name if instance.user else None
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['user'] = self.get_user(instance)
    
        # Serialize unit_number if it's not None
        if instance.unit_number:
            response['unit_number'] = UnitNoSerializer(instance.unit_number).data 
        else:
            response['unit_number'] = None
        
        # Serialize project_name if it's not None
        if instance.project_name:
            response['project_name'] = ProjectSerializer(instance.project_name).data 
        else:
            response['project_name'] = None
        
        # Serialize payment_stage if it's not None
        if instance.payment_stage:
            response['payment_stage'] = PaymentStageDetailSerializer(instance.payment_stage).data 
        else:
            response['payment_stage'] = None
        
        # Serialize project_type if it's not None
        if instance.project_type:
            response['project_type'] = ProjectTypeSerializer(instance.project_type).data 
        else:
            response['project_type'] = None
        
        return response

        


class ModeOfPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModeOfPayment
        fields = '__all__'


class BankNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankName
        fields = '__all__'
    


class ReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = '__all__'
    def get_user(self, instance):
        # return instance.user.name if instance.user else None
        if instance.user:
            return instance.user.name
        return None
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['user'] = self.get_user(instance)
        response['applicant_name'] = instance.payment_stage.personal_deatils.applicant_name if instance.payment_stage else None
        if instance.unit_number:
            response['unit_number'] = UnitNoSerializer(instance.unit_number).data 
        if instance.project_name:
            response['project_name'] = ProjectSerializer(instance.project_name).data 
        if instance.payment_stage:
            response['payment_stage'] = PaymentStageDetailSerializer(instance.payment_stage).data 
        if instance.mode_of_payment:
            response['mode_of_payment'] = ModeOfPaymentSerializer(instance.mode_of_payment).data 
        if instance.bank_name:
            response['bank_name'] = BankNameSerializer(instance.bank_name).data 

        return response




