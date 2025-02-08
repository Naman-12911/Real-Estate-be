from django.shortcuts import render
from .models import *
from .serializer import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http.response import Http404
from rest_framework.response import Response


class WhatsAppMessageAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return WhatsAppMessage.objects.get(pk=pk)
        except WhatsAppMessage.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = WhatsAppMessage.objects.filter(project_name=pk).order_by('-created_at')
                serializer = WhatsAppMessageSerializer(data)
                return Response(serializer.data)

            else:
                data = WhatsAppMessage.objects.all().order_by('-created_at')
                serializer = WhatsAppMessageSerializer(data, many=True)

                return Response(serializer.data)
    def post(self, request, format=None):
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            
            serializer = WhatsAppMessageSerializer(data=mutable_data)

            # Check if the data passed is valid
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Return Response to User

            response = Response()

            response.data = {
                'message': 'message send  Successfully',
                'data': serializer.data
            }
            return response
    

class WhatsAppMessageAllAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return WhatsAppMessage.objects.get(pk=pk)
        except WhatsAppMessage.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = WhatsAppMessage.objects.all().order_by('-created_at')
                serializer = WhatsAppMessageAllSerializer(data)
                return Response(serializer.data)

            else:
                data = WhatsAppMessage.objects.filter(all_project=True).order_by('-created_at')
                serializer = WhatsAppMessageAllSerializer(data, many=True)

                return Response(serializer.data)
    def post(self, request, format=None):
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            
            serializer = WhatsAppMessageAllSerializer(data=mutable_data)

            # Check if the data passed is valid
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Return Response to User

            response = Response()

            response.data = {
                'message': 'message send  Successfully',
                'data': serializer.data
            }
            return response
   
    

class WhatsAppMessageTrackAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return TrackWhatAppMessage.objects.get(pk=pk)
        except TrackWhatAppMessage.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = TrackWhatAppMessage.objects.all().order_by('-created_at')
                serializer = WhatsAppMessageTrackSerializer(data)
                return Response(serializer.data)

            else:
                unique_users_data = {}

                # Get all messages
                all_messages = TrackWhatAppMessage.objects.all()

                # Iterate through each message
                for message in all_messages:
                    user_id = message.user_id

                    # Check if the user has already been serialized
                    if user_id not in unique_users_data:
                        # Serialize the user's data
                        serializer = WhatsAppMessageTrackSerializer(message)
                        user_data = serializer.data

                        # Add the serialized data to the dictionary
                        unique_users_data[user_id] = user_data

                # Return the serialized data for all unique users
                return Response(list(unique_users_data.values()))
    def post(self, request, format=None):
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            
            serializer = WhatsAppMessageTrackSerializer(data=mutable_data)

            # Check if the data passed is valid
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Return Response to User

            response = Response()

            response.data = {
                'message': 'message send  Successfully',
                'data': serializer.data
            }
            return response
   