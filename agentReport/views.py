from django.shortcuts import render
from django.db.models import Count
from django.shortcuts import render
from .models import *
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializer import *
from django.http.response import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from collections import defaultdict
from django.db.models.functions import Trim
from django.db.models import Q, Count
from datetime import datetime
from django.utils.timezone import make_aware, make_naive


class AgentReportAPIview(APIView):
    permission_classes = [IsAuthenticated,]

    # def get(self, request, format=None):
    #     try:
    #         # Get the user ID from the request query parameters
    #         assigned_to_id = request.query_params.get('user_id')

    #         # Initialize the FbLeads queryset with a date filter
    #         #fb_leads_queryset = FbLeads.objects.filter(created_at__gte=make_naive(make_aware(datetime(2024, 6, 1))))
    #         fb_leads_queryset = FbLeads.objects.filter(assigned_to__sales_employee=True, assigned_to__is_active=True)

    #         # If the user_id parameter exists, filter by that user ID
    #         if assigned_to_id:
    #             fb_leads_queryset = fb_leads_queryset.filter(assigned_to_id=assigned_to_id)

    #         # Get distinct users who have status lead entries
    #         users_with_status_lead = fb_leads_queryset.values('assigned_to__id', 'assigned_to__name')

    #         # Get the status lead data for each user
    #         data = []
    #         for user in users_with_status_lead:
    #             # Get the related fb_leads for the user filtered by the date
    #             fb_leads_for_user = FbLeads.objects.filter(
    #                 Q(user=user['assigned_to__id'])
    #             )

    #             # Calculate counts for each status field
    #             status_counts_dict = {
    #                 "Dump": fb_leads_for_user.filter(assigned_to=user['assigned_to__id'], dump_lead=True).count(),
    #                 "Intersted": fb_leads_for_user.filter(assigned_to=user['assigned_to__id'], intersted=True).count(),
    #                 "Booked": fb_leads_for_user.filter(assigned_to=user['assigned_to__id'], booked=True).count(),
    #                 "SiteVisit": fb_leads_for_user.filter(assigned_to=user['assigned_to__id'], site_visit=True).count(),
    #                 "corporate_visit": fb_leads_for_user.filter(assigned_to=user['assigned_to__id'], corporate_visit=True).count(),
    #                 "TotalLeads": fb_leads_queryset.filter(assigned_to=user['assigned_to__id']).count()
    #             }
    #             # Construct user data with counts
    #             user_data = {
    #                 'agent_id': user['assigned_to__id'],
    #                 'agent_name': user['assigned_to__name'],
    #                 'status_counts': status_counts_dict
    #             }
    #             data.append(user_data)

    #         return Response(data, status=status.HTTP_200_OK)

    #     except Exception as e:
    #         return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, format=None):
        try:
            # Get the user ID from the request query parameters
            assigned_to_id = request.query_params.get('user_id')

            # Initialize the FbLeads queryset with a date filter
            fb_leads_queryset = FbLeads.objects.filter(
                assigned_to__sales_employee=True,
                assigned_to__is_active=True
            )

            # If the user_id parameter exists, filter by that user ID
            if assigned_to_id:
                fb_leads_queryset = fb_leads_queryset.filter(assigned_to_id=assigned_to_id)

            # Get distinct users who have status lead entries
            users_with_status_lead = fb_leads_queryset.values('assigned_to__id', 'assigned_to__name').distinct()

            # Get the status lead data for each user
            data = []
            for user in users_with_status_lead:
                # Get the related fb_leads for the user
                fb_leads_for_user = fb_leads_queryset.filter(assigned_to=user['assigned_to__id'])

                # Calculate counts for each status field
                total_leads = fb_leads_for_user.count()
                dump_lead_count = fb_leads_for_user.filter(dump_lead=True).count()
                intersted_count = fb_leads_for_user.filter(intersted=True).count()
                booked_count = fb_leads_for_user.filter(booked=True).count()
                site_visit_count = fb_leads_for_user.filter(site_visit=True).count()
                corporate_visit_count = fb_leads_for_user.filter(corporate_visit=True).count()

                # Calculate lead_yet_to_be_contacted
                lead_yet_to_be_contacted = total_leads - (
                    dump_lead_count + intersted_count + booked_count + site_visit_count + corporate_visit_count
                )

                # Construct status counts dictionary
                status_counts_dict = {
                    "Dump": dump_lead_count,
                    "Intersted": intersted_count,
                    "Booked": booked_count,
                    "SiteVisit": site_visit_count,
                    "corporate_visit": corporate_visit_count,
                    "TotalLeads": total_leads,
                    "lead_yet_to_be_contacted": lead_yet_to_be_contacted
                }
                
                # Construct user data with counts
                user_data = {
                    'agent_id': user['assigned_to__id'],
                    'agent_name': user['assigned_to__name'],
                    'status_counts': status_counts_dict
                }
                data.append(user_data)

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





class AgentSiteVisitsAPIview(APIView):
    permission_classes = [IsAuthenticated,]

    def get(self, request, format=None):
        try:
            # Get all distinct assigned users
            assigned_users = FbLeads.objects.values_list('assigned_to', flat=True).distinct()

            # Create a defaultdict to store site visits for each assigned user
            user_site_visits = defaultdict(list)

            # Define the date filter for LeadEdit instances
            # date_filter = datetime(2024, 6, 1)

            # Iterate over assigned users
            for user_id in assigned_users:
                # Get LeadEdit instances associated with the user and have site visit
                lead_edits = LeadEdit.objects.filter(user=user_id, visit_number__isnull=False)
                # lead_edits = LeadEdit.objects.filter(user=user_id, visit_number__isnull=False, created_at__gte=date_filter)

                # Iterate over the LeadEdit instances to group them by visit number
                for lead_edit in lead_edits:
                    visit_number = lead_edit.visit_number
                    # Get or create a site visit dictionary for the visit number
                    site_visit_data = next((item for item in user_site_visits[user_id] if item['visit_number'] == visit_number), None)
                    if site_visit_data is None:
                        site_visit_data = {'visit_number': visit_number, 'leads': []}
                        user_site_visits[user_id].append(site_visit_data)
                    # Add lead edit data to the site visit dictionary
                    site_visit_data['leads'].append(LeadEditSerializer(lead_edit).data)

            # Serialize the data and return response
            serialized_data = {str(user_id): SiteVisitSerializer(user_site_visits[user_id], many=True).data for user_id in user_site_visits.keys()}
            return Response(serialized_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)