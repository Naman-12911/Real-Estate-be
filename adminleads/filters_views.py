from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from social.models import FbLeads,LeadEdit
from .serializer import FbLeadAdminSerializer
from rest_framework.permissions import IsAuthenticated
from .filters import FbLeadsCorporateFilter,SalesPersonCountsLeadStatsFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import status
from realEstate.pagination import CommonPagination
from django.db.models import Q
from social.serializer import FbLeadSerializer
from django.db.models import OuterRef, Subquery

    

class FbLeadFilterCorporte(generics.ListAPIView):
    permission_classes = [IsAuthenticated,]
    serializer_class = FbLeadSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = FbLeadsCorporateFilter
    pagination_class = CommonPagination

    def get_queryset(self):
        user = self.request.user
        queryset = FbLeads.objects.filter(Q(corporate_visit_to=user) | Q(assigned_to=user)).filter(corporate_visit=True).order_by("-created_at")
        status_of_lead = self.request.query_params.get('status_of_lead')
        lead_edits = LeadEdit.objects.all()
        if status_of_lead:
                latest_lead_edit_subquery = LeadEdit.objects.filter(
                    fb_leads=OuterRef('fb_leads')
                ).order_by('-created_at').values('pk')[:1]

                lead_edits = lead_edits.filter(
                    pk__in=Subquery(latest_lead_edit_subquery),
                    status_of_lead__status_lead__exact=status_of_lead
                )
                fb_lead_ids = lead_edits.values_list('fb_leads_id', flat=True)
                queryset = queryset.filter(id__in=fb_lead_ids)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)  # Use paginate_queryset to get the paginated queryset
        
        # if not queryset.exists():
        #     return Response({'detail': 'No data found'}, status=status.HTTP_204_NO_CONTENT)

        serializer = self.get_serializer(queryset, many=True)
        return self.get_paginated_response(serializer.data)
    

class SalesPersonCountsLeadStatsFilterGenric(generics.ListAPIView):
    permission_classes = [IsAuthenticated,]
    serializer_class = FbLeadAdminSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = SalesPersonCountsLeadStatsFilter

    def get_queryset(self):
        queryset = FbLeads.objects.filter(corporate_visit=True).order_by("-created_at")
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        if not queryset.exists():
            return Response({'detail': 'No data found'}, status=status.HTTP_204_NO_CONTENT)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)