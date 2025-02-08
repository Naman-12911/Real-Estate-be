from django.shortcuts import render
from rest_framework.views import APIView
from .models import ClientLoanProfile
from .serializers import ClientLoanProfileSerializers
from rest_framework.permissions import IsAuthenticated
from django.http.response import Http404
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter
from rest_framework import status
from django_filters import rest_framework as filters

class ClientLoanApiview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return ClientLoanProfile.objects.get(pk=pk)
        except ClientLoanProfile.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = self.get_object(pk)
                serializer = ClientLoanProfileSerializers(data)
                return Response(serializer.data)

            else:
                data = ClientLoanProfile.objects.all().order_by("-created_at")
                serializer = ClientLoanProfileSerializers(data, many=True)

                return Response(serializer.data)
    def post(self, request, format=None):
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            
            serializer = ClientLoanProfileSerializers(data=mutable_data)

            # Check if the data passed is valid
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Return Response to User

            response = Response()

            response.data = {
                'message': 'Client Loan Profile Created Successfully',
                'data': serializer.data
            }
            return response
    
    def patch(self, request, pk=None, format=None):
        # Get the booking to update
        client_loan_to_update = ClientLoanProfile.objects.get(pk=pk)

        # Initialize serializer with instance to update and data
        serializer = ClientLoanProfileSerializers(client_loan_to_update, data=request.data, partial=True)

        # Validate and save the serializer
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Prepare the response
        response_data = {
            'message': 'Client Loan Profile updated Successfully',
            'data': serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)

        
    def delete(self, request, pk, format=None):
        clinet_loan_to_delete =  ClientLoanProfile.objects.get(pk=pk)

            # delete the todo
        clinet_loan_to_delete.delete()

        return Response({
            'message': 'Client Loan Profile Deleted Successfully'
        })