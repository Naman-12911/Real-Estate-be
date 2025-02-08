from django.shortcuts import render
from rest_framework.views import APIView
from .models import Faq
from .serializers import FaqSerializers
from rest_framework.permissions import IsAuthenticated
from django.http.response import Http404
from rest_framework.response import Response
from rest_framework import status
from django_filters import rest_framework as filters

class FaqApiview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return Faq.objects.get(pk=pk)
        except Faq.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = self.get_object(pk)
                serializer = FaqSerializers(data)
                return Response(serializer.data)

            else:
                data = Faq.objects.all()
                serializer = FaqSerializers(data, many=True)

                return Response(serializer.data)
    def post(self, request, format=None):
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            
            serializer = FaqSerializers(data=mutable_data)

            # Check if the data passed is valid
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Return Response to User

            response = Response()

            response.data = {
                'message': 'Faq Created Successfully',
                'data': serializer.data
            }
            return response
    
    def patch(self, request, pk=None, format=None):
        # Get the booking to update
        Faq_to_update = Faq.objects.get(pk=pk)

        # Initialize serializer with instance to update and data
        serializer = FaqSerializers(Faq_to_update, data=request.data, partial=True)

        # Validate and save the serializer
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Prepare the response
        response_data = {
            'message': 'Faqupdated Successfully',
            'data': serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)

        
    def delete(self, request, pk, format=None):
        Faq_to_delete =  Faq.objects.get(pk=pk)

            # delete the todo
        Faq_to_delete.delete()

        return Response({
            'message': 'Faq Deleted Successfully'
        })