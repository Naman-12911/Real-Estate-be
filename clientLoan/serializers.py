from rest_framework import serializers
from account.models import User
from .models import ClientLoanProfile
from bookingForm.serializers import BookingSerializers


class ClientLoanProfileSerializers(serializers.ModelSerializer):
    agent_name = serializers.CharField(source='user.name', read_only=True)
    class Meta:
        model = ClientLoanProfile
        fields = '__all__'

    def get_user(self, instance):
        return instance.user.name if instance.user else None
    # def to_representation(self, instance):
    #     response = super().to_representation(instance)
    #     response['user'] = self.get_user(instance)
    #     return response

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['user'] = self.get_user(instance)
        response['bookings'] = BookingSerializers(instance.bookings).data
        return response
    



