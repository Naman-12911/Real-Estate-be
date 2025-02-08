from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import *
from .serializer import *
from rest_framework.permissions import IsAuthenticated, AllowAny
from .filters import FbLeadsFilter,FbLeadsFilterPhoneNumber,LeadSourceFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import status
from rest_framework.generics import ListAPIView
from django_filters import rest_framework as filters
from realEstate.pagination import CommonPagination
from django.db.models import Q,IntegerField
from django.utils.dateparse import parse_date
from django.db.models import OuterRef, Subquery
from account.models import User

class FbLeadLeadEditAPIView(APIView):
    permission_classes = [IsAuthenticated,]
    def get(self, request, fb_lead_id, format=None):
        # Retrieve the FbLeads instance based on the provided id
        fb_lead = get_object_or_404(FbLeads, id=fb_lead_id)
        
        # Retrieve LeadEdit objects related to the fb_lead
        lead_edit_data = LeadEdit.objects.filter(fb_leads=fb_lead).order_by("-created_at")
        
        # Serialize the lead_edit_data
        serializer = LeadEditSerializer(lead_edit_data, many=True)
        data = serializer.data
        for i in data:
            i['user_name'] = User.objects.get(id=i['user']).name
        return Response(data)
    

class FbLeadFilterList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FbLeadSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = FbLeadsFilter
    pagination_class = CommonPagination  # Add pagination class

    def get_queryset(self):
        user = self.request.user
        queryset = FbLeads.objects.filter(assigned_to=user).exclude(dump_lead=True).order_by("-updated_at")
        lead_edits = LeadEdit.objects.all()
        status_of_lead = self.request.query_params.get('status_of_lead')
        status_of_lead_warm_hot_cold = self.request.query_params.get('status_of_lead_warm_hot_cold')
        
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

        if status_of_lead or status_of_lead_warm_hot_cold:
            fb_lead_ids = lead_edits.values_list('fb_leads_id', flat=True)
            queryset = queryset.filter(id__in=fb_lead_ids)

        return queryset
        

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is None:
            return Response({'detail': 'No data found'}, status=status.HTTP_204_NO_CONTENT)

        serializer = self.get_serializer(page, many=True)
        # for item in serializer.data:
        #     raw_data = item.get('raw', {})
        #     if "whatsapp_no./_phone_no." in raw_data:
        #         item['alt_phone_number'] = raw_data["whatsapp_no./_phone_no."]
        
        return self.get_paginated_response(serializer.data)
    

class FbLeadFilterPhoneNumberList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FbLeadPostSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = FbLeadsFilterPhoneNumber
    # pagination_class = CommonPagination  # Add pagination class

    def get_queryset(self):
        queryset = FbLeads.objects.all().order_by("-created_at")
        return queryset

    def list(self, request, *args, **kwargs):
        phone_number = request.GET.get('phone_number')
        if not phone_number or phone_number=="":
            return Response({'detail': 'No data found'}, status=status.HTTP_204_NO_CONTENT)

        queryset = self.filter_queryset(self.get_queryset())
        #page = self.paginate_queryset(queryset)  # Use paginate_queryset to get the paginated queryset
        
        if not queryset.exists():
            return Response({'detail': 'No data found'}, status=status.HTTP_204_NO_CONTENT)

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        for i in data:
            raw = i.get('raw')
            if raw and isinstance(raw, dict) and 'whatsapp_no./_phone_no.' in raw:
                i['alt_phone_number'] = raw['whatsapp_no./_phone_no.']

        return Response(data)
    

# class FbLeadFilterDumpList(generics.ListAPIView):
#     permission_classes = [IsAuthenticated,]
#     serializer_class = FbLeadSerializer
#     filter_backends = [DjangoFilterBackend, SearchFilter]
#     filterset_class = FbLeadsFilter
#     pagination_class = CommonPagination  # Add pagination class
    
#     def get_queryset(self):
#         queryset = FbLeads.objects.filter(dump_lead=True).order_by("-created_at")
#         return queryset

#     def list(self, request, *args, **kwargs):
#         queryset = self.filter_queryset(self.get_queryset())
#         page = self.paginate_queryset(queryset)  # Use paginate_queryset to get the paginated queryset
        
#         if not queryset.exists():
#             return Response({'detail': 'No data found'}, status=status.HTTP_204_NO_CONTENT)

#         serializer = self.get_serializer(queryset, many=True)
#         return self.get_paginated_response(serializer.data)
    

class FbLeadFilterDumpList(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CommonPagination  # Use your pagination class

    def get(self, request):
        # Retrieve query parameters for date and full_name filtering
        start_date_str = request.query_params.get('created_at__lte')
        end_date_str = request.query_params.get('created_at__gte')
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
        status_of_lead_warm_hot_cold = request.query_params.get('status_of_lead_warm_hot_cold')
        get_site_visit_to_name = request.query_params.get('get_site_visit_to_name')

        # Parse the date strings into date objects
        start_date = parse_date(start_date_str) if start_date_str else None
        end_date = parse_date(end_date_str) if end_date_str else None

        # Create queryset with dump_lead filter and optional date and full_name filters
        queryset = FbLeads.objects.filter(dump_lead=True).exclude(permanent_dump_lead=True).order_by("-updated_at")
        # if not request.user.admin:
        queryset = queryset.filter(Q(assigned_to=request.user) | Q(user=request.user))

        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        if full_name:
            queryset = queryset.filter(full_name__icontains=full_name)
        if phone_number:
            queryset = queryset.filter(phone_number__icontains=phone_number)
        if dump_lead:
            queryset = queryset.exclude(dump_lead=True)
        if permanent_dump_lead:
            queryset = queryset.filter(permanent_dump_lead=permanent_dump_lead == 'True')
        if project_name:
            queryset = queryset.filter(project_name__project_name__icontains=project_name)
        if agent_name:
            queryset = queryset.filter(user__name__icontains=agent_name)
        if project_type:
            queryset = queryset.filter(project_type_name__project_type__icontains=project_type)
        if lead_source:
            queryset = queryset.filter(lead_source__lead_source__icontains=lead_source)
        if get_site_visit_to_name:
            queryset = queryset.filter(site_visit_to__name__icontains=get_site_visit_to_name)

        lead_edits = LeadEdit.objects.all()
        if description:
            lead_edits = lead_edits.filter(description__icontains=description)
        # if lead_status:
        #     lead_edits = lead_edits.filter(status_of_lead__status_lead__icontains=lead_status)
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

        # Get the fb_leads ids from filtered LeadEdit records
        fb_leads_ids = lead_edits.values_list('fb_leads_id', flat=True).distinct()
        queryset = queryset.filter(id__in=fb_leads_ids)

        # Paginate the filtered queryset
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        # Serialize the paginated queryset
        serializer = FbLeadSerializer(paginated_queryset, many=True)

        # Return the paginated response
        return paginator.get_paginated_response(serializer.data)

# from django.db.models.functions import GroupConcat

class FbLeadFilterSiteVisit(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FbLeadSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = FbLeadsFilter
    pagination_class = CommonPagination  # Add pagination class

    def get_queryset(self):
        user = self.request.user
        queryset = FbLeads.objects.filter(Q(site_visit_to=user) | Q(assigned_to=user)).filter(site_visit=True)

        # Apply filters
        status_of_lead = self.request.query_params.get('status_of_lead')
        visit_number = self.request.query_params.get('visit_number')
        if status_of_lead:
            latest_lead_edit_subquery = LeadEdit.objects.filter(
                fb_leads=OuterRef('pk')
            ).order_by('-created_at').values('pk')[:1]

            lead_edits = LeadEdit.objects.filter(
                pk__in=Subquery(latest_lead_edit_subquery),
                status_of_lead__status_lead__exact=status_of_lead
            )
            fb_lead_ids = lead_edits.values_list('fb_leads_id', flat=True)
            queryset = queryset.filter(id__in=fb_lead_ids)

        if visit_number:
            max_site_visits_subquery = LeadEdit.objects.filter(
                fb_leads=OuterRef('pk')
            ).order_by('-visit_number').values('visit_number')[:1]

            queryset = queryset.annotate(
                max_site_visits=Subquery(max_site_visits_subquery)
            ).filter(max_site_visits=visit_number)

        # Annotate with latest visit_date
        latest_visit_date_subquery = LeadEdit.objects.filter(
            fb_leads=OuterRef('pk')
        ).order_by('-visit_date').values('visit_date')[:1]

        queryset = queryset.annotate(
            latest_visit_date=Subquery(latest_visit_date_subquery)
        ).order_by('-latest_visit_date')

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)  # Use paginate_queryset to get the paginated queryset
        
        # if not queryset.exists():
        #     return Response({'detail': 'No data found'}, status=status.HTTP_204_NO_CONTENT)

        serializer = self.get_serializer(queryset, many=True)
        serialized_data = serializer.data
    
        for data_item, lead_edit_instance in zip(serialized_data, queryset):
            try:
                data_item['visited_by'] =  LeadEdit.objects.get(fb_leads=lead_edit_instance.pk).visited_by.name
            except Exception as e:
                data_item['visited_by'] = None
        for i in serialized_data:
            if 'raw' in i:
                if i['raw']:
                    if "whatsapp_no./_phone_no." in i['raw']:
                        i['alt_phone_number'] = i['raw']['whatsapp_no./_phone_no.']
        return self.get_paginated_response(serialized_data)
    

# filter for lead of medium

class LeadSourceFilterListApiview(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset =LeadSource.objects.all()
    serializer_class = LeadSourceSerializer
    filter_backends = [filters.DjangoFilterBackend,SearchFilter]
    filterset_class = LeadSourceFilter
    search_fields = ['medium_of_lead',]
    #pagination_class = CommonPagination  # Add pagination class

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).order_by("lead_source")
        #page = self.paginate_queryset(queryset)  # Use paginate_queryset to get the paginated queryset
        
        if not queryset.exists():
            return Response({'detail': 'No data found'}, status=status.HTTP_204_NO_CONTENT)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)