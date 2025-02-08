from rest_framework import serializers
from account.models import User
from .models import Faq
from propertyStatus.serializer import ProjectSerializer
from django.contrib.sites.shortcuts import get_current_site


class FaqSerializers(serializers.ModelSerializer):
    agent_name = serializers.CharField(source='user.name', read_only=True)
    class Meta:
        model = Faq
        fields = '__all__'

    def get_user(self, instance):
        return instance.user.name if instance.user else None
    def Image(self, obj):
        return self.build_absolute_image_url(obj.image)
    def video(self, obj):
        return self.build_absolute_image_url(obj.video)
    
    def build_absolute_image_url(self, image_path):
        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(image_path)
        else:
            # If request is not available (for example, in shell), use the default site
            site = get_current_site(None)
            return f"{site.scheme}://{site.domain}{image_path}"

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['user'] = self.get_user(instance)
        response['project_faq'] = ProjectSerializer(instance.project_faq).data
        return response
   
    



