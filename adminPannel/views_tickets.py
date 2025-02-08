from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http.response import Http404
from rest_framework.response import Response
from rest_framework import status
from django_filters import rest_framework as filters
from tickets.models import *
from tickets.serializer import *

    

class TicketAdminAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return Ticket.objects.get(pk=pk)
        except Ticket.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            current_user = request.user
            if pk:
                data = self.get_object(pk)
                serializer = Ticket(data)
                return Response(serializer.data)

            else:
                data = Ticket.objects.all().order_by('-created_at')
                serializer = TickerSerializer(data, many=True)

                return Response(serializer.data)
            
    def post(self, request, format=None):
        current_user = request.user
        mutable_data = request.data.copy() if request.data else {}

        mutable_data['user'] = current_user.id 
                
        serializer = TickerSerializer(data=mutable_data)

        # Check if the data passed is valid
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Return Response to User
        response = Response({
            'message': 'Ticker Created Successfully',
            'data': serializer.data
        })
        return response
    def patch(self, request, pk=None, format=None):
        # Get the todo to update
        ticket_to_update = Ticket.objects.get(pk=pk)

        serializer = TickerSerializer(instance=ticket_to_update, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = Response()
        response.data = {
            'message': 'Ticket updated Successfully',
            'data': serializer.data
        }

        return response

    def delete(self, request, pk, format=None):
        ticket_to_delete =  Ticket.objects.get(pk=pk)

            # delete the todo
        ticket_to_delete.delete()

        return Response({
            'message': 'Ticket Deleted Successfully'
        })