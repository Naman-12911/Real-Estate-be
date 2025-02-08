from django.shortcuts import render
from .models import *
from rest_framework.permissions import IsAuthenticated
from .serializer import *
from django.http.response import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from datetime import datetime, timedelta
from django.utils import timezone


# Create your views here.
class Fb_ViewAdmin(APIView):
    permission_classes = [IsAuthenticated,]
    def get_object(self, pk):
        try:
            return FbLeads.objects.get(pk=pk)
        except FbLeads.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
        
        if pk:
            data = self.get_object(pk)
            serializer = FbLeadSerializer(data)
            return Response(serializer.data)

        else:
            fb_leads = FbLeads.objects.all().order_by('-created_at')
            
            data = []
            now = timezone.now()  # Get the current time in the timezone-aware format
            thirty_day_minutes_ago = now - timedelta(days=30)  # Get the datetime 7 minutes ago
            for fb_lead in fb_leads:
                last_lead_edit = fb_lead.leadedit_set.last()  # Get the last lead edit related to this fb lead
                if last_lead_edit:
                    last_update_time = last_lead_edit.created_at
                    # Check if the last update was more than 48 hours ago
                    if now - last_update_time > timedelta(hours=48):
                        fb_lead.status = 'Delayed'
                else:
                    # No lead edit record found, check if the fb_lead was created more than 48 hours ago
                    if now - fb_lead.created_time > timedelta(hours=48):
                        fb_lead.status = 'Delayed'
                
                # Check if the fb_lead was created more than 7 minutes ago
                if fb_lead.created_time < thirty_day_minutes_ago and not last_lead_edit:
                    fb_lead.dump_lead = True
                
                fb_lead.save()  # Save the updated fb_lead object
                
                data.append(fb_lead)
            
            serializer = FbLeadSerializer(data, many=True)
            return Response(serializer.data)