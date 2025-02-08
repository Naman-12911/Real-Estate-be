from rest_framework import serializers
from account.models import User
from .models import *
from bookingForm.serializers import BookingPersonalDeatils


# class PaymentStagesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PaymentStages
#         fields = '__all__'
#     def get_user(self, instance):
#         return instance.user.name if instance.user else None
#     def to_representation(self, instance):
#         response = super().to_representation(instance)
#         response['user'] = self.get_user(instance)

class PaymentStageDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentStageDetail
        fields = '__all__'
    def to_representation(self, instance):
        response = super().to_representation(instance)
       

        response['user'] = self.get_user(instance)
        return response

    def get_user(self, instance):
        return instance.user.name if instance.user else None


class PaymentReceiptsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentReceipts
        fields = '__all__'
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['stage_name'] = PaymentStageDetailSerializer(instance.stage_name).data 
        return response

    def get_user(self, instance):
        return instance.user.name if instance.user else None
    

class RemiderDemandInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RemiderDemandInformation
        fields = '__all__'
    
    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.payment_receipts_stage:
            response['payment_receipts_stage'] = PaymentReceiptsSerializer(instance.payment_receipts_stage).data
        else:
            response['payment_receipts_stage'] = None

        return response

    def get_user(self, instance):
        return instance.user.name if instance.user else None





