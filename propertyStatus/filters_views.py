from django.shortcuts import render
from .models import *
from .serializer import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http.response import Http404
from rest_framework.response import Response
from rest_framework import generics
from .models import Phase
from .filters import PhaseFilter
from .serializer import PhaseSerializer
from django_filters.rest_framework import DjangoFilterBackend
# Create your views here.


class ProjectTypeListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        project_id = request.query_params.get('project_id')
        if "," in project_id:
            project_id = project_id.split(",")
            project_types = ProjectType.objects.filter(projects_id__in=project_id)
        else:
            if project_id:
                project_types = ProjectType.objects.filter(projects_id=project_id)
            else:
                project_types = ProjectType.objects.all()
        serializer = ProjectTypeSerializer(project_types, many=True)
        return Response(serializer.data)
    

class UnitNoListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        project_id = request.query_params.get('project_id')

        queryset = UnitNo.objects.all()

        if project_id:
            queryset = queryset.filter(projects_id=project_id, available=False)
        else:
            queryset = queryset.filter(available=False)

        serializer = UnitNoSerializer(queryset, many=True)
        return Response(serializer.data)
    
class UnitNoListbookedAllView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        project_id = request.query_params.get('project_id')
        if project_id:
            unit_nos = UnitNo.objects.filter(projects_id=project_id)
        else:
            unit_nos = UnitNo.objects.all()
        serializer = UnitNoSerializer(unit_nos, many=True)
        return Response(serializer.data)
    

class PhaseByProjectAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, project_id, format=None):
        # Filter phases based on the provided project_id
        phases = Phase.objects.filter(unit__projects_id=project_id)
        
        # Serialize the queryset
        serializer = PhaseSerializer(phases, many=True)
        
        return Response(serializer.data)