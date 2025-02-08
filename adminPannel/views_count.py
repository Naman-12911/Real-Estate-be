from django.shortcuts import render
from .models import *
from propertyStatus.serializer import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http.response import Http404
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter
from rest_framework import status
from django_filters import rest_framework as filters
from rest_framework.status import HTTP_204_NO_CONTENT
from social.models import LeadEdit, FbLeads
from django.db.models import Count


class StatusCountOfLeads(APIView):
    def get(self, request, *args, **kwargs):
        # Aggregate count of leads based on the status_lead field
        lead_counts = FbLeads.objects.values('status_of_lead__status_lead').annotate(count=Count('id'))
        
        # Format the result as a dictionary
        result = {item['status_of_lead__status_lead']: item['count'] for item in lead_counts}
        
        return Response(result, status=status.HTTP_200_OK)