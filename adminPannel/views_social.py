from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from social.serializer import *
from rest_framework.permissions import IsAuthenticated
from social.filters import FbLeadsFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import status
from realEstate.pagination import CommonPagination
from django.db.models import Q
from adminleads.filters import FbLeadsCorporateFilter
from django.utils.dateparse import parse_date
from django.db.models import OuterRef, Subquery
# from django.db.models.functions import GroupConcat

class FbLeadFilterSiteVisit(generics.ListAPIView):
    permission_classes = [IsAuthenticated,]
    serializer_class = FbLeadSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = FbLeadsFilter
    pagination_class = CommonPagination  # Add pagination class
    
    def get_queryset(self):
        queryset = FbLeads.objects.filter(site_visit=True).order_by("-created_at")
        lead_edits = LeadEdit.objects.all()
        status_of_lead = self.request.query_params.get('status_of_lead')
        status_of_lead_warm_hot_cold = self.request.query_params.get('status_of_lead_warm_hot_cold')
        visit_number = self.request.query_params.get('visit_number')

        if status_of_lead:
            latest_lead_edit_subquery = LeadEdit.objects.filter(
                fb_leads=OuterRef('fb_leads')
            ).order_by('-created_at').values('pk')[:1]

            lead_edits = lead_edits.filter(
                pk__in=Subquery(latest_lead_edit_subquery),
                status_of_lead__status_lead__exact=status_of_lead
        )

        if status_of_lead_warm_hot_cold:
            latest_lead_edit_subquery = LeadEdit.objects.filter(
                fb_leads=OuterRef('fb_leads')
            ).order_by('-created_at').values('pk')[:1]

            lead_edits = lead_edits.filter(
                pk__in=Subquery(latest_lead_edit_subquery),
                status_of_lead_warm_hot_cold__exact=status_of_lead_warm_hot_cold
        )
        if visit_number:
            max_site_visits_subquery = LeadEdit.objects.filter(
                fb_leads=OuterRef('pk')
            ).order_by('-visit_number').values('visit_number')[:1]

            queryset = queryset.annotate(
                max_site_visits=Subquery(max_site_visits_subquery)
            ).filter(max_site_visits=visit_number)
        
        fb_lead_ids = lead_edits.values_list('fb_leads_id', flat=True)
        queryset = queryset.filter(id__in=fb_lead_ids)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)  # Get the paginated queryset

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            serialized_data = serializer.data

            for data_item, lead_edit_instance in zip(serialized_data, page):
                try:
                    data_item['visited_by'] = LeadEdit.objects.get(fb_leads=lead_edit_instance.pk).visited_by.name
                except Exception as e:
                    data_item['visited_by'] = None
            
            for i in serialized_data:
                if 'raw' in i and i['raw']:
                    if "whatsapp_no./_phone_no." in i['raw']:
                        i['alt_phone_number'] = i['raw']['whatsapp_no./_phone_no.']

            return self.get_paginated_response(serialized_data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            serialized_data = serializer.data

            for data_item, lead_edit_instance in zip(serialized_data, page):
                try:
                    data_item['visited_by'] = LeadEdit.objects.get(fb_leads=lead_edit_instance.pk).visited_by.name
                except Exception as e:
                    data_item['visited_by'] = None
            
            for i in serialized_data:
                if 'raw' in i and i['raw']:
                    if "whatsapp_no./_phone_no." in i['raw']:
                        i['alt_phone_number'] = i['raw']['whatsapp_no./_phone_no.']
                        
            return Response(serializer.data, status=status.HTTP_200_OK)




class FbLeadFilterCorporate(generics.ListAPIView):
    permission_classes = [IsAuthenticated,]
    serializer_class = FbLeadSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = FbLeadsCorporateFilter
    pagination_class = CommonPagination

    def get_queryset(self):
        user = self.request.user
        queryset = FbLeads.objects.filter(corporate_visit=True).order_by("-created_at")
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
        
        serializer = self.get_serializer(queryset, many=True)
        return self.get_paginated_response(serializer.data or [])

    

class FbLeadFilterDumpList(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CommonPagination  # Use your pagination class

    def get(self, request):
        # Retrieve query parameters for date and assigned_to filtering
        start_date_str = request.query_params.get('created_at__lte')
        end_date_str = request.query_params.get('created_at__gte')
        assigned_user = request.query_params.get('assigned_to_name')
        full_name = request.query_params.get('full_name')
        phone_number = request.query_params.get('phone_number')
        dump_lead = request.query_params.get('dump_lead')
        permanent_dump_lead = request.query_params.get('permanent_dump_lead')
        project_name = request.query_params.get('project_name')
        agent_name = request.query_params.get('agent_name')
        project_type = request.query_params.get('project_type')
        lead_source = request.query_params.get('lead_source')
        description = request.query_params.get('description')
        status_of_lead = request.query_params.get('status_of_lead')
        feedback = request.query_params.get('feedback')
        status_of_lead_warm_hot_cold = request.query_params.get('status_of_lead_warm_hot_cold')

        # Parse the date strings into date objects
        start_date = parse_date(start_date_str) if start_date_str else None
        end_date = parse_date(end_date_str) if end_date_str else None

        
        
        # Create initial queryset for FbLeads with dump_lead filter
        queryset = FbLeads.objects.filter(dump_lead=True).order_by("-updated_at")
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        if assigned_user:
            queryset = queryset.filter(assigned_to__name__exact=assigned_user)
        if full_name:
            queryset = queryset.filter(full_name__icontains=full_name)
        if phone_number:
            queryset = queryset.filter(phone_number__icontains=phone_number)
        if dump_lead:
            queryset = queryset.filter(dump_lead=True)
        if permanent_dump_lead:
            queryset = queryset.filter(permanent_dump_lead=True)
        if project_name:
            queryset = queryset.filter(project_name__project_name__icontains=project_name)
        if agent_name:
            queryset = queryset.filter(user__name__icontains=agent_name)
        if project_type:
            queryset = queryset.filter(project_type_name__project_type__icontains=project_type)
        if lead_source:
            queryset = queryset.filter(lead_source__lead_source__icontains=lead_source)
        if feedback:
            queryset = queryset.filter(feedback__icontains=feedback)
        

        # Filter on LeadEdit table
        lead_edits = LeadEdit.objects.all()
        if description:
            lead_edits = lead_edits.filter(description__icontains=description)
        if status_of_lead:
            latest_lead_edit_subquery = LeadEdit.objects.filter(
                fb_leads=OuterRef('fb_leads')
            ).order_by('-created_at').values('pk')[:1]

            lead_edits = lead_edits.filter(
                pk__in=Subquery(latest_lead_edit_subquery),
                status_of_lead__status_lead__exact=status_of_lead
            )

        # Get the fb_leads ids from filtered LeadEdit records
        # fb_leads_ids = lead_edits.values_list('fb_leads_id', flat=True).distinct()
        
        # Filter the FbLeads queryset with these ids
        queryset = queryset.filter(id__in=queryset)

        # Paginate the filtered queryset
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        # Serialize the paginated queryset
        serializer = FbLeadSerializer(paginated_queryset, many=True)

        # Return the paginated response
        return paginator.get_paginated_response(serializer.data)

