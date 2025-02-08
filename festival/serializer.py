from rest_framework import serializers
from account.models import User
from .models import *
from .serializer import *




class FestivalPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = FestivalPost
        fields = '__all__'
    