from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.http import HttpResponse
from django.utils.dateparse import parse_date
from io import BytesIO
import pandas as pd
from social.models import FbLeads
from datetime import datetime
from django.db.models import F, Prefetch
from social.models import FbLeads, LeadEdit, StatusLead, NotificationStore
from social.serializer import FbLeadSerializer
from django.utils.dateparse import parse_date
from dateutil.parser import parse
from django.db.models import OuterRef, Subquery,Q
from .serializer import *
from django.utils import timezone
import re
from workers.models import *
from workers.serializer import *
from rest_framework.response import Response
from rest_framework import status
from bookingForm.models import Booking
from django.db.models import Sum
from django.utils import timezone
from django.db.models import F, Case, When, BooleanField
from civilWorker.serializer import *
from civilWorker.models import *

class AllLeadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Extract query parameters
        full_name = request.query_params.get('full_name')
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        assigned_user = request.query_params.get('assigned_to_name')
        assigned_user = request.query_params.get('assigned_to_name')
        start_date_str = request.query_params.get('start_date')
        phone_number = request.query_params.get('phone_number')
        project_name = request.query_params.get('project_name')
        agent_name = request.query_params.get('agent_name')
        project_type_name = request.query_params.get('project_type_name')
        lead_source = request.query_params.get('lead_source')
        description = request.query_params.get('description')
        status_of_lead_warm_hot_cold = request.query_params.get('status_of_lead_warm_hot_cold')
        status_of_lead = request.query_params.get('status_of_lead')
        expected_booking = request.query_params.get('expected_booking')
        feedback = request.query_params.get('feedback')
        start_date = parse_date(start_date_str) if start_date_str else None
        end_date = parse_date(end_date_str) if end_date_str else None
        re_assigned = request.query_params.get('re_assigned')
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
        if status_of_lead_warm_hot_cold:
            latest_lead_edit_subquery = LeadEdit.objects.filter(
                fb_leads=OuterRef('fb_leads')
            ).order_by('-created_at').values('pk')[:1]

            lead_edits = lead_edits.filter(
                pk__in=Subquery(latest_lead_edit_subquery),
                status_of_lead_warm_hot_cold__exact=status_of_lead_warm_hot_cold
            )

        fb_leads_ids = lead_edits.values_list('fb_leads_id', flat=True).distinct()

        fb_leads = FbLeads.objects.filter(id__in=fb_leads_ids).exclude(Q(dump_lead=True)).order_by('-created_at')

        if full_name:
            fb_leads = fb_leads.filter(full_name__icontains=full_name)
        if start_date:
            fb_leads = fb_leads.filter(created_at__gte=start_date)
        if end_date:
            fb_leads = fb_leads.filter(created_at__lte=end_date)
        if phone_number:
            fb_leads = fb_leads.filter(phone_number__icontains=phone_number)
        if assigned_user:
            fb_leads = fb_leads.filter(assigned_to__name__icontains=assigned_user)
        if project_name:
            fb_leads = fb_leads.filter(project_name__project_name__icontains=project_name)
        if agent_name:
            fb_leads = fb_leads.filter(user__name__icontains=agent_name)
        if project_type_name:
            fb_leads = fb_leads.filter(project_type_name__property_type__exact=project_type_name)
        if lead_source:
           fb_leads = fb_leads.filter(lead_source__lead_source__exact=lead_source)
        if feedback:
            fb_leads = fb_leads.filter(feedback__icontains=feedback)
        if expected_booking:
            fb_leads = fb_leads.filter(expected_booking=expected_booking)
        if re_assigned:
                fb_leads = fb_leads.filter(dump_lead=False, permanent_dump_lead=True)

        serializer = FbLeadViewLeadsExcelFileSerializer(fb_leads, many=True)
        leads_df = pd.DataFrame(serializer.data)

        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            leads_df.to_excel(writer, index=False, sheet_name='Leads')
        
        # Set the position to the start of the stream
        output.seek(0)

        # Create a HttpResponse with the Excel file
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=leads_{}.xlsx'.format(datetime.now().strftime('%Y%m%d_%H%M%S'))

        return response

class AllDumpAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        # Extract query parameters
        full_name = request.query_params.get('full_name')
        assigned_user = request.query_params.get('assigned_to_name')
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        phone_number = request.query_params.get('phone_number')
        project_name = request.query_params.get('project_name')
        agent_name = request.query_params.get('agent_name')
        project_type_name = request.query_params.get('project_type_name')
        lead_source = request.query_params.get('lead_source')
        description = request.query_params.get('description')
        status_of_lead_warm_hot_cold = request.query_params.get('status_of_lead_warm_hot_cold')
        status_of_lead = request.query_params.get('status_of_lead')
        expected_booking = request.query_params.get('expected_booking')
        feedback = request.query_params.get('feedback')
        get_site_visit_to_name = request.query_params.get('get_site_visit_to_name')
        start_date = parse_date(start_date_str) if start_date_str else None
        end_date = parse_date(end_date_str) if end_date_str else None
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
        if status_of_lead_warm_hot_cold:
            latest_lead_edit_subquery = LeadEdit.objects.filter(
                fb_leads=OuterRef('fb_leads')
            ).order_by('-created_at').values('pk')[:1]

            lead_edits = lead_edits.filter(
                pk__in=Subquery(latest_lead_edit_subquery),
                status_of_lead_warm_hot_cold__exact=status_of_lead_warm_hot_cold
            )

        fb_leads_ids = lead_edits.values_list('fb_leads_id', flat=True).distinct()

        fb_leads = FbLeads.objects.filter(id__in=fb_leads_ids).filter(dump_lead=True).order_by('-created_at')

        if full_name:
            fb_leads = fb_leads.filter(full_name__icontains=full_name)
        if start_date:
            fb_leads = fb_leads.filter(created_at__gte=start_date)
        if end_date:
            fb_leads = fb_leads.filter(created_at__lte=end_date)
        if phone_number:
            fb_leads = fb_leads.filter(phone_number__icontains=phone_number)
        if assigned_user:
            fb_leads = fb_leads.filter(assigned_to__name__icontains=assigned_user)
        if project_name:
            fb_leads = fb_leads.filter(project_name__project_name__icontains=project_name)
        if agent_name:
            fb_leads = fb_leads.filter(user__name__icontains=agent_name)
        if project_type_name:
            fb_leads = fb_leads.filter(project_type_name__property_type__exact=project_type_name)
        if lead_source:
           fb_leads = fb_leads.filter(lead_source__lead_source__exact=lead_source)
        if feedback:
            fb_leads = fb_leads.filter(feedback__icontains=feedback)
        if expected_booking:
            fb_leads = fb_leads.filter(expected_booking=expected_booking)
        if get_site_visit_to_name:
            queryset = queryset.filter(site_visit_to__name__icontains=get_site_visit_to_name)

        # Create DataFrame
        # leads_df = pd.DataFrame(leads_data)
        serializer = FbLeadDumpLeadsExcelFileSerializer(fb_leads, many=True)
        leads_df = pd.DataFrame(serializer.data)

        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            leads_df.to_excel(writer, index=False, sheet_name='Leads')
        
        # Set the position to the start of the stream
        output.seek(0)

        # Create a HttpResponse with the Excel file
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=leads_{}.xlsx'.format(datetime.now().strftime('%Y%m%d_%H%M%S'))

        return response

class AllSiteVisitAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        # Extract query parameters
        full_name = request.query_params.get('full_name')
        assigned_user = request.query_params.get('assigned_to_name')
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        phone_number = request.query_params.get('phone_number')
        project_name = request.query_params.get('project_name')
        agent_name = request.query_params.get('agent_name')
        project_type_name = request.query_params.get('project_type_name')
        lead_source = request.query_params.get('lead_source')
        description = request.query_params.get('description')
        status_of_lead_warm_hot_cold = request.query_params.get('status_of_lead_warm_hot_cold')
        status_of_lead = request.query_params.get('status_of_lead')
        expected_booking = request.query_params.get('expected_booking')
        feedback = request.query_params.get('feedback')
        get_site_visit_to_name = request.query_params.get('get_site_visit_to_name')
        visited_by = request.query_params.get('visited_by')
        visit_number = request.query_params.get('visit_number')
        # Parse the date strings into date objects
        start_date = parse_date(start_date_str) if start_date_str else None
        end_date = parse_date(end_date_str) if end_date_str else None
        lead_edits = LeadEdit.objects.all()

        if description:
            lead_edits = lead_edits.filter(description__icontains=description)
        if visited_by:
            visited_by = lead_edits.filter(visited_by__name__exact=visited_by)

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
           

        fb_leads_ids = lead_edits.values_list('fb_leads_id', flat=True).distinct()

        fb_leads = FbLeads.objects.filter(id__in=fb_leads_ids).filter(site_visit=True).order_by('-created_at')

        if full_name:
            fb_leads = fb_leads.filter(full_name__icontains=full_name)
            # if created_at_gte:
            #     fb_leads = fb_leads.filter(created_at__gte=created_at_gte)
            # if created_at_lte:
            #     fb_leads = fb_leads.filter(created_at__lte=created_at_lte)
       
        if start_date:
            fb_leads = fb_leads.filter(created_at__gte=start_date)
        if end_date:
            fb_leads = fb_leads.filter(created_at__lte=end_date)
        if phone_number:
            fb_leads = fb_leads.filter(phone_number__icontains=phone_number)
        if assigned_user:
            fb_leads = fb_leads.filter(assigned_to__name__exact=assigned_user)
        if project_name:
            fb_leads = fb_leads.filter(project_name__project_name__exact=project_name)
        if agent_name:
            fb_leads = fb_leads.filter(user__name__exact=agent_name)
        if project_type_name:
            fb_leads = fb_leads.filter(project_type_name__property_type__exact=project_type_name)
        if lead_source:
           fb_leads = fb_leads.filter(lead_source__lead_source__exact=lead_source)
        if feedback:
            fb_leads = fb_leads.filter(feedback__icontains=feedback)
        if expected_booking:
            fb_leads = fb_leads.filter(expected_booking=expected_booking)
        if get_site_visit_to_name:
            fb_leads = fb_leads.filter(site_visit_to__name__icontains=get_site_visit_to_name)

        serializer = FbLeadSiteVistExcelFileSerializer(fb_leads, many=True)
        leads_data = serializer.data
        leads_df = pd.DataFrame(leads_data)

        # Create DataFrame
        # leads_df = pd.DataFrame(leads_data)

        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            leads_df.to_excel(writer, index=False, sheet_name='Leads')
        
        # Set the position to the start of the stream
        output.seek(0)

        # Create a HttpResponse with the Excel file
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=leads_{}.xlsx'.format(datetime.now().strftime('%Y%m%d_%H%M%S'))

        return response


class AllCorporateVisitAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        # Extract query parameters
        full_name = request.query_params.get('full_name')
        assigned_user = request.query_params.get('assigned_to_name')
        created_at_gte = request.query_params.get('created_at_gte')
        created_at_lte = request.query_params.get('created_at_lte')
        phone_number = request.query_params.get('phone_number')
        project_name = request.query_params.get('project_name')
        agent_name = request.query_params.get('agent_name')
        project_type_name = request.query_params.get('project_type_name')
        lead_source = request.query_params.get('lead_source')
        description = request.query_params.get('description')
        status_of_lead_warm_hot_cold = request.query_params.get('status_of_lead_warm_hot_cold')
        status_of_lead = request.query_params.get('status_of_lead')
        expected_booking = request.query_params.get('expected_booking')
        feedback = request.query_params.get('feedback')
        lead_edits = LeadEdit.objects.all()

        if description:
            lead_edits = lead_edits.filter(description__icontains=description)
            # if status_of_lead:
            #     lead_edits = lead_edits.filter(status_of_lead__status_lead__exact=status_of_lead)

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
           
            # if status_of_lead_warm_hot_cold:
            #     lead_edits = lead_edits.filter(status_of_lead_warm_hot_cold=status_of_lead_warm_hot_cold)

        fb_leads_ids = lead_edits.values_list('fb_leads_id', flat=True).distinct()

        fb_leads = FbLeads.objects.filter(id__in=fb_leads_ids).filter(corporate_visit=True).order_by("-created_at")

        if full_name:
            fb_leads = fb_leads.filter(full_name__icontains=full_name)
            
        if created_at_gte:
            try:
                created_at_gte_parsed = parse(created_at_gte)
                fb_leads = fb_leads.filter(created_at__gte=created_at_gte_parsed)
            except ValueError:
                pass  # Handle invalid date format if needed
        if created_at_lte:
            try:
                created_at_lte_parsed = parse(created_at_lte)
                fb_leads = fb_leads.filter(created_at__lte=created_at_lte_parsed)
            except ValueError:
                pass
        if phone_number:
            fb_leads = fb_leads.filter(phone_number__icontains=phone_number)
        if assigned_user:
            fb_leads = fb_leads.filter(assigned_to__name__icontains=assigned_user)
        if project_name:
            fb_leads = fb_leads.filter(project_name__project_name__icontains=project_name)
        if agent_name:
            fb_leads = fb_leads.filter(user__name__icontains=agent_name)
        if project_type_name:
            fb_leads = fb_leads.filter(project_type_name__property_type__exact=project_type_name)
        if lead_source:
           fb_leads = fb_leads.filter(lead_source__lead_source__exact=lead_source)
        if feedback:
            fb_leads = fb_leads.filter(feedback__icontains=feedback)
        if expected_booking:
            fb_leads = fb_leads.filter(expected_booking=expected_booking)

        serializer = FbLeadCorporateLeadsExcelFileSerializer(fb_leads, many=True)
        leads_df = pd.DataFrame(serializer.data)

        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            leads_df.to_excel(writer, index=False, sheet_name='Leads')
        
        # Set the position to the start of the stream
        output.seek(0)

        # Create a HttpResponse with the Excel file
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=leads_{}.xlsx'.format(datetime.now().strftime('%Y%m%d_%H%M%S'))

        return response



# Admin dashboard excel files donwload 

class LeadsSvBookFilesForBookedStatus(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        # Get date filter parameters
        start_date_str = request.GET.get('start_date', None)
        end_date_str = request.GET.get('end_date', None)

        # Parse the date strings into datetime objects
        if start_date_str:
            start_date = parse_date(start_date_str)
        else:
            start_date = None

        if end_date_str:
            end_date = parse_date(end_date_str)
        else:
            end_date = None

        # Filter FbLeads based on the dates and dump_lead field
        leads_query = FbLeads.objects.filter(booked=True).exclude(Q(dump_lead=True))
        
        if start_date:
            leads_query = leads_query.filter(created_at__gte=start_date)
        if end_date:
            leads_query = leads_query.filter(created_at__lte=end_date)

        # Annotate foreign key fields to include their related data
        leads_query = leads_query.annotate(
            user_name=F('user__name'),
            assigned_to_name=F('assigned_to__name'),
            site_visit_to_name=F('site_visit_to__name'),
            corporate_visit_to_name=F('corporate_visit_to__name'),
            preferred_location_name=F('preferred_location__preferred_location'),
            reasons_feedback_name=F('reasons_feedback__reason_of_dump'),
            budget_name=F('budget__max_budget'),
            lead_source_name=F('lead_source__lead_source'),
            by_medium_name=F('by_medium__medium'),
        ).prefetch_related(
            Prefetch('project_name'),
            Prefetch('project_type_name')
        )
        

        # Prepare the data for the DataFrame
        leads_data = []
        for lead in leads_query:
            project_names = ", ".join([project.project_name for project in lead.project_name.all()])
            project_type_name = ", ".join([project_type.property_type for project_type in lead.project_type_name.all()])
            
            lead_data = {
                'id': lead.id,
                'user_name': lead.user_name,
                'assigned_to_name': lead.assigned_to_name,
                'site_visit_to_name': lead.site_visit_to_name,
                'corporate_visit_to_name': lead.corporate_visit_to_name,
                'ad_id': lead.ad_id,
                'ad_name': lead.ad_name,
                'adset_id': lead.adset_id,
                'adset_name': lead.adset_name,
                'campaign_id': lead.campaign_id,
                'campaign_name': lead.campaign_name,
                'city': lead.city,
                'custom_disclaimer_responses': lead.custom_disclaimer_responses,
                'created_time': lead.created_time,
                'company_name': lead.company_name,
                'prices_available': lead.prices_available,
                'raw': lead.raw,
                'project_names': project_names,
                'project_type_names': project_type_name,
                'vehicle': lead.vehicle,
                'retailer_item_id': lead.retailer_item_id,
                'fb_from': lead.fb_from,
                'full_name': lead.full_name,
                'form_name': lead.form_name,
                'form_id': lead.form_id,
                'email': lead.email,
                'phone_number': lead.phone_number,
                'page_name': lead.page_name,
                'form': lead.form,
                'page_id': lead.page_id,
                'job_title': lead.job_title,
                'platform': lead.platform,
                'partner_name': lead.partner_name,
                'select_available_price': lead.select_available_price,
                'alternative_number': lead.alternative_number,
                # 'project_names': ', '.join([p.project_name for p in lead.project_names]),
                # 'project_type_name': ', '.join([p.project_type_name for p in lead.project_type_name]),
                'address': lead.address,
                'occupation': lead.occupation,
                'preferred_location_name': lead.preferred_location_name,
                'preferred_location_other': lead.preferred_location_other,
                'reasons_feedback_name': lead.reasons_feedback_name,
                'budget_name': lead.budget_name,
                'lead_source_name': lead.lead_source_name,
                'by_medium_name': lead.by_medium_name,
                'corporate_visit_place': lead.corporate_visit_place,
                'dump_lead': lead.dump_lead,
                'permanent_dump_lead': lead.permanent_dump_lead,
                'site_visit': lead.site_visit,
                'booked': lead.booked,
                'corporate_visit': lead.corporate_visit,
                'intersted': lead.intersted,
                'block_enquiry': lead.block_enquiry,
                'do_not_call': lead.do_not_call,
                'good_lead': lead.good_lead,
                're_visit': lead.re_visit,
                'poor_lead': lead.poor_lead,
                'may_be': lead.may_be,
                'created_at': lead.created_at,
                'Last Updated Date and Time': lead.updated_at,
                'Type': lead.Type,
                'PhoneVerificationStatus': lead.PhoneVerificationStatus,
                'Query': lead.Query,
                'CalledOn': lead.CalledOn,
                'Time': lead.Time,
                'Duration': lead.Duration,
                'CallStatus': lead.CallStatus,
                'url': lead.url,
                'receiveddate': lead.receiveddate,
                'interestedin': lead.interestedin,
                'responetype': lead.responetype,
                # 'name': lead.name,
                'EmailVerificationStatus': lead.EmailVerificationStatus,
                'Questionnaire': lead.Questionnaire,
                'productcode': lead.productcode,
                'producttype': lead.producttype,
                'IntentVerificationStatus': lead.IntentVerificationStatus,
                'LeadScore': lead.LeadScore,
                'FollowupCurrentStatus': lead.FollowupCurrentStatus,
                'ProdType': lead.ProdType,
                'city': lead.city,
                'project': lead.project,
                'rescom': lead.rescom,
                'Bhk': lead.Bhk,
                'PropertySnapshot': lead.PropertySnapshot,
                'ParentProductDetails': lead.ParentProductDetails,
                'SetIsParentProductTypeResponse': lead.SetIsParentProductTypeResponse,
                'CompactLabel': lead.CompactLabel,
                'Duplicate': lead.Duplicate,
                'property_title': lead.property_title,
                'purpose_of_property': lead.purpose_of_property,
                'property': lead.property,
                'locality': lead.locality,
                'details': lead.details,
                'service_type': lead.service_type,
                'property_type': lead.property_type,
                'seller_id': lead.seller_id,
                'seller_name': lead.seller_name,
                'configuration': lead.configuration,
                'price': lead.price,
                'address': lead.address,
                'feedback': lead.feedback,
                'enquiry_date': lead.enquiry_date,
                'status_acc_admin': lead.status_acc_admin,
                'feedback_acc_admin': lead.feedback_acc_admin,
                'expected_booking': lead.expected_booking,
            }
            leads_data.append(lead_data)

        leads_df = pd.DataFrame(leads_data)

        # Create a BytesIO buffer to hold the Excel data
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            leads_df.to_excel(writer, index=False, sheet_name='Leads')
        
        # Set the position to the start of the stream
        output.seek(0)

        # Create a HttpResponse with the Excel file
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=leads_{}.xlsx'.format(datetime.now().strftime('%Y%m%d_%H%M%S'))

        return response




class PRHighlightMetricsPendingTask(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Assuming 'Dump' and 'Booked' are specific statuses you are interested in
        dump_status = StatusLead.objects.get(status_lead='Dump')
        booked_status = StatusLead.objects.get(status_lead='Booked')

        # Fetch all leads and lead edits
        leads = FbLeads.objects.all()
        lead_edits = LeadEdit.objects.all()

        # Exclude leads with any LeadEdit entries having status_of_lead "dump" or "booked"
        excluded_leads = lead_edits.exclude(status_of_lead__in=[dump_status, booked_status]).values_list('fb_leads', flat=True)
        filtered_leads = leads.exclude(id__in=excluded_leads).distinct()
        # Serialize the data
        filtered_leads_data = FbLeadSerializer(filtered_leads, many=True).data

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Write leads data to Excel sheet 'Leads'
            pd.DataFrame(filtered_leads_data).to_excel(writer, index=False, sheet_name='Leads')


        # Set response headers for Excel file download
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=pending_tasks_{}.xlsx'.format(datetime.now().strftime('%Y%m%d_%H%M%S'))

        return response

class PRHighlightMetricsNextSheduleTask(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Assuming 'Dump' and 'Booked' are specific statuses you are interested in
        dump_status = StatusLead.objects.get(status_lead='Dump')
        booked_status = StatusLead.objects.get(status_lead='Booked')

        # Fetch all leads and lead edits
        leads = FbLeads.objects.all()
        lead_edits = LeadEdit.objects.all()

        # Exclude leads with any LeadEdit entries having status_of_lead "dump" or "booked"
       
        today = timezone.now().date()
        today_leads = leads.filter(created_at__date=today)
        next_scheduled_leads = lead_edits.filter(next_schedule_date__gte=today).exclude(status_of_lead__in=[dump_status, booked_status]).values_list('fb_leads', flat=True)
        
        next_scheduled_leads_data = FbLeadSerializer(FbLeads.objects.filter(id__in=next_scheduled_leads).distinct(), many=True).data
        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Write leads data to Excel sheet 'Leads'
            pd.DataFrame(next_scheduled_leads_data).to_excel(writer, index=False, sheet_name='Leads')


        # Set response headers for Excel file download
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=next_scheduled_tasks_{}.xlsx'.format(datetime.now().strftime('%Y%m%d_%H%M%S'))

        return response


class PRHighlightMetricsTodayTask(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
       
        today = timezone.now().date()

        # Extract lead IDs from unseen notifications created today
        notifications = NotificationStore.objects.filter(seen=False, created_at__date=today)
        lead_ids = []
        for notification in notifications:
            match = re.search(r'Lead ID:(\d+)', notification.message)
            if match:
                lead_ids.append(int(match.group(1)))

        # Fetch leads created today with the extracted lead IDs
        leads = FbLeads.objects.filter(
            id__in=lead_ids
        ).distinct().select_related('user').prefetch_related(
            'assigned_to', 'site_visit_to', 'corporate_visit_to'
        )
        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Write leads data to Excel sheet 'Leads'
            pd.DataFrame(leads).to_excel(writer, index=False, sheet_name='Leads')


        # Set response headers for Excel file download
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=today_tasks_{}.xlsx'.format(datetime.now().strftime('%Y%m%d_%H%M%S'))

        return response


#  site worker excel file 



from datetime import datetime
import pandas as pd
from io import BytesIO

class SiteWorkersData(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        project_name = request.query_params.get('project_name')
        unit_no = request.query_params.get('unit_no')

        queryset = SiteWorkers.objects.filter(deleted=False)

        if project_name:
            queryset = queryset.filter(project_name__icontains=project_name)

        if unit_no:
            queryset = queryset.filter(unit_no__icontains=unit_no)

        if not queryset.exists():
            return Response({'detail': 'No data found'}, status=status.HTTP_204_NO_CONTENT)

        serializer = SiteWorkersSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        # Annotate a new field 'accept_first' to prioritize records with accept=True
        queryset = SiteWorkers.objects.filter(deleted=False).annotate(
            accept_first=Case(
                When(accept=True, then=1),
                default=0,
                output_field=BooleanField()
            )
        ).order_by('-accept_first')  # Order by '-accept_first' to have accept=True records first
         # Filter by project_name and unit_no if provided in query parameters
        project_name = self.request.query_params.get('project_name')
        unit_no = self.request.query_params.get('unit_no')
        if project_name:
            queryset = queryset.filter(project_name=project_name)

        if unit_no:
            queryset = queryset.filter(unit_no=unit_no)
        return queryset

    def calculate_expenses(self, queryset):
        expenses = []
        for qry in queryset:
            if timezone.is_naive(qry.updated_at):
                updated_at = timezone.make_aware(qry.updated_at, timezone.get_current_timezone())
            else:
                updated_at = qry.updated_at

            if (datetime.now() - qry.updated_at).days >= 60:
                # Set delay flags if conditions are met
                if not qry.worker_stage1:
                    qry.delay_stage1 = True
                elif not qry.worker_stage2:
                    qry.delay_stage2 = True
                elif not qry.worker_stage3:
                    qry.delay_stage3 = True
                elif not qry.worker_stage4:
                    qry.delay_stage4 = True
                elif not qry.worker_stage5:
                    qry.delay_stage5 = True
                elif not qry.worker_stage6:
                    qry.delay_stage6 = True
                elif not qry.worker_stage7:
                    qry.delay_stage7 = True
                qry.updated_at = datetime.now()
                qry.save()

            # Fetch booking details
            try:
                booking = Booking.objects.get(unit_no=qry.unit_no, deleted=False, cancelled=False)
            except Booking.DoesNotExist:
                booking = Booking.objects.filter(unit_no=qry.unit_no, deleted=False, cancelled=False).last()

            if booking:
                total_amount = booking.cost_payable_to_company
                expense = {}
                try:
                    # Calculate monthly expenses for the worker
                    all_money = MonthlyExpense.objects.filter(siteworker=qry, deleted=False).values('stage').annotate(
                        total_money=Sum('money'),
                        total_money_rec=Sum('money_rec')
                    )
                    stages = [f'stage{i}' for i in range(1, 8)]
                    for expense_group in all_money:
                        stage = expense_group['stage']
                        if stage in stages:
                            stages.remove(stage)
                        total_money = expense_group['total_money']
                        total_money_rec = expense_group['total_money_rec']
                        expense[stage] = {"total": total_money, "total_rec": total_money_rec}

                    for stage in stages:
                        if '1' in stage:
                            money = float(total_amount) * 0.25
                        elif '2' in stage:
                            money = float(total_amount) * 0.20
                        elif '3' in stage:
                            money = float(total_amount) * 0.20
                        elif '4' in stage:
                            money = float(total_amount) * 0.10
                        elif '5' in stage:
                            money = float(total_amount) * 0.10
                        elif '6' in stage:
                            money = float(total_amount) * 0.10
                        elif '7' in stage:
                            money = float(total_amount) * 0.05
                        expense[stage] = {"total": money, "total_rec": 0}

                except Exception as e:
                    print(e, "last")
                expenses.append(expense)

        return expenses

    def generate_excel(self, data):
        # Convert data into a pandas DataFrame
        df = pd.DataFrame(data)

        # Example: Convert to Excel format
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False)

        # Set the buffer's pointer to the beginning and return the bytes
        excel_buffer.seek(0)
        return excel_buffer.read()
