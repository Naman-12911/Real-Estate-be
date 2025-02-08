from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.http.response import Http404
from rest_framework.response import Response
from .models import *
from .serializer import *
from social.fcm_manager import sendPush
from account.models import *



class ContactUsAPIview(APIView):
    permission_classes = [AllowAny]
    def get_object(self, pk):
        try:
            return ContactUs.objects.get(pk=pk)
        except ContactUs.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = self.get_object(pk)
                serializer = ContactUs(data)
                return Response(serializer.data)

            else:
                data = ContactUs.objects.all()
                serializer = ContactUsSerializer(data, many=True)

                return Response(serializer.data)
            
    def post(self, request, format=None):
        current_user = request.user
        mutable_data = request.data.copy() if request.data else {}

        mutable_data['user'] = current_user.id 
                
        serializer = ContactUsSerializer(data=mutable_data)

        # Check if the data passed is valid
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Return Response to User
        response = Response({
            'message': 'Contact Created Successfully',
            'data': serializer.data
        })
        return response