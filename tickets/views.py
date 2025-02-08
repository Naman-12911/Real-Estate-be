from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http.response import Http404
from rest_framework.response import Response
from rest_framework import status
from django_filters import rest_framework as filters
from .models import *
from .serializer import *
from social.fcm_manager import sendPush
from account.models import *
from social.serializer import NotificationStoreSerializer
from django.contrib.auth import get_user_model
from realEstate.pagination import CommonPagination


class TicketAPIview(APIView):
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
                data = Ticket.objects.filter(user=current_user).order_by('-created_at')
                serializer = TickerSerializer(data, many=True)

                return Response(serializer.data)
            
    def post(self, request, format=None):
        current_user = request.user
        mutable_data = request.data.copy()
        mutable_data['user'] = current_user.id
        
        serializer = TickerSerializer(data=mutable_data)

        # Check if the data passed is valid
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        User = get_user_model()  # Get the user model
        admin_users = User.objects.filter(admin=True)
        
        # Get FCM tokens for all admin users
        fcm_tokens = []
        admin_user_ids = []
        for admin_user in admin_users:
            admin_user_ids.append(admin_user.id)
            token_query = FCMTokens.objects.filter(user=admin_user)
            fcm_tokens.extend([i.device_token for i in token_query if i.device_token != ""])

        # Prepare notification data
        notification_data = {
            "sent_to": admin_user_ids,
            "head": "Ticket Raised",
            "message": f"New ticket has been raised by {current_user.name}"
        }
        
        notiserializer = NotificationStoreSerializer(data=notification_data)
        if notiserializer.is_valid():
            notiserializer.save()
        
        # Send push notification
        try:
            sendPush("Ticket Raised", f"New ticket has been raised by {current_user.name}", fcm_tokens)
        except Exception as e:
            print("Error while sending push notification", e)
        
        # Return Response to User
        response = Response()
        response.data = {
            'message': 'Ticket Created Successfully',
            'data': serializer.data
        }
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
    

class TicketAdminAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return Ticket.objects.get(pk=pk)
        except Ticket.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            paginator = CommonPagination()
            current_user = request.user
            if pk:
                data = self.get_object(pk)
                serializer = Ticket(data)
                return Response(serializer.data)

            else:
                data = Ticket.objects.all().order_by('-created_at')
                result_page = paginator.paginate_queryset(data, request)
                serializer = TickerSerializer(result_page, many=True)
                return paginator.get_paginated_response(serializer.data)
            
    
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