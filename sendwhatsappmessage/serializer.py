from rest_framework import serializers
from account.models import User
from .models import *


class WhatsAppMessageSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project_name.project_name', read_only=True)
    property_type = serializers.CharField(source='project_type.property_type', read_only=True)
    agent_name = serializers.SerializerMethodField()
    class Meta:
        model = WhatsAppMessage
        fields = '__all__'
    def get_agent_name(self, obj):
        return obj.user.get_full_name() if obj.user else None
    

class WhatsAppMessageAllSerializer(serializers.ModelSerializer):
    agent_name = serializers.SerializerMethodField()
    class Meta:
        model = WhatsAppMessage
        fields = ['all_project','description','user','created_at','updated_at','agent_name']
    def get_agent_name(self, obj):
        return obj.user.get_full_name() if obj.user else None
    
class WhatsAppMessageTrackSerializer(serializers.ModelSerializer):
    #agent_name = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()
    class Meta:
        model = TrackWhatAppMessage
        fields = '__all__'
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['agent_name'] = self.get_agent_name(instance)
        return response

    def get_agent_name(self, instance):
        return instance.user.name if instance.user else None
    def get_message_count(self, obj):
        # Get the count of messages for the user associated with the message
        user = obj.user
        if user:
            return TrackWhatAppMessage.objects.filter(user=user).count()
        return 0