from rest_framework import fields, serializers
from .models import *
from social.serializer import LeadEditSerializer
from django.utils import timezone


class TickerSerializer(serializers.ModelSerializer):
    project_names = serializers.CharField(source='project_name.project_name', read_only=True)
    class Meta:
        model = Ticket
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['user'] = self.get_user(instance)
        return response

    def get_user(self, instance):
        user = instance.user
        if user:
            return {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email
            }
        return None
