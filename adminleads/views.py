from django.shortcuts import render
from social.models import *
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializer import *
from django.http.response import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from datetime import datetime, timedelta
from dateutil.parser import parse
from django.utils import timezone
from django.db.models import Q, Count
from account.models import FCMTokens
from django.db.models import Count
from social.fcm_manager import sendPush
from social.serializer import NotificationStoreSerializer
from social.serializer import FbLeadSerializer
from realEstate.pagination import CommonPagination
from django.db.models import Count,F
from rest_framework import generics
from django.utils.timezone import make_aware, make_naive
from social.serializer import LeadEditSerializer
from account.models import User
from django.db.models import Q, Max
from django.db.models import OuterRef, Subquery
import logging
logger = logging.getLogger(__name__)


# Create your views here.
# class Fb_ViewAdminAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get_object(self, pk):
#         try:
#             return FbLeads.objects.get(pk=pk)
#         except FbLeads.DoesNotExist:
#             raise Http404

#     def get(self, request, pk=None, format=None):
#         if pk:
#             data = self.get_object(pk)
#             serializer = FbLeadAdminSerializer(data)
#             return Response(serializer.data)
#         else:
#             full_name = request.query_params.get('full_name')
#             assigned_user = request.query_params.get('assigned_to_name')
#             created_at_gte = request.query_params.get('created_at_gte')
#             created_at_lte = request.query_params.get('created_at_lte')
#             phone_number = request.query_params.get('phone_number')
#             project_name = request.query_params.get('project_name')
#             agent_name = request.query_params.get('agent_name')
#             project_type = request.query_params.get('project_name')
#             lead_source = request.query_params.get('project_name')
#             description = request.query_params.get('description')
#             lead_status = request.query_params.get('status_of_lead')

#             fb_leads = FbLeads.objects.exclude(Q(dump_lead=True)).order_by('-created_at')

#             if full_name:
#                 fb_leads = fb_leads.filter(full_name__icontains=full_name)
#             if created_at_gte:
#                 fb_leads = fb_leads.filter(created_at__gte=created_at_gte)
#             if created_at_lte:
#                 fb_leads = fb_leads.filter(created_at__lte=created_at_lte)
#             if phone_number:
#                 fb_leads = fb_leads.filter(phone_number__icontains=phone_number)
#             if assigned_user:
#                 fb_leads = fb_leads.filter(assigned_to__name__icontains=assigned_user)
#             if project_name:
#                 fb_leads = fb_leads.filter(project_name__project_name__icontains=project_name)
#             if agent_name:
#                 fb_leads = fb_leads.filter(user__name__icontains=agent_name)
#             if project_type:
#                 fb_leads = fb_leads.filter(project_type_name__project_type__icontains=project_type)
#             if lead_source:
#                 fb_leads = fb_leads.filter(lead_source__lead_source__icontains=lead_source)

#             latest_lead_edit = LeadEdit.objects.filter(fb_leads=OuterRef('pk')).order_by('-created_at')

#             fb_leads = fb_leads.annotate(
#                 latest_lead_edit_description=Subquery(latest_lead_edit.values('description')[:1]),
#                 latest_lead_edit_status=Subquery(latest_lead_edit.values('status_of_lead__status_lead')[:1])
#             )

#             if description:
#                 fb_leads = fb_leads.filter(latest_lead_edit_description__icontains=description)
#             if lead_status:
#                 fb_leads = fb_leads.filter(latest_lead_edit_status__icontains=lead_status)

#             fb_leads = fb_leads.order_by('-created_at')
#             paginator = CommonPagination()
#             paginator.page_size = 50

#             result_page = paginator.paginate_queryset(fb_leads, request)
#             data = []
#             now = timezone.now()
#             thirty_day_minutes_ago = now - timedelta(days=30)
#             for fb_lead in result_page:
#                 last_lead_edit = fb_lead.leadedit_set.last()
#                 if last_lead_edit:
#                     last_update_time = last_lead_edit.created_at
#                     if now - last_update_time > timedelta(hours=48):
#                         fb_lead.status = 'Delayed'
#                 else:
#                     if now - fb_lead.created_time > timedelta(hours=48):
#                         fb_lead.status = 'Delayed'
#                 if fb_lead.created_time < thirty_day_minutes_ago and not last_lead_edit:
#                     fb_lead.dump_lead = True
#                 fb_lead.save()
#                 data.append(fb_lead)

#             serializer = FbLeadSerializer(data, many=True)
#             return paginator.get_paginated_response(serializer.data)

class Fb_ViewAdminAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return FbLeads.objects.get(pk=pk)
        except FbLeads.DoesNotExist:
            raise Http404

    def get(self, request, pk=None, format=None):
        if pk:
            data = self.get_object(pk)
            serializer = FbLeadAdminSerializer(data)
            return Response(serializer.data)
        else:
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
            re_assigned = request.query_params.get('re_assigned')
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
            if status_of_lead or status_of_lead_warm_hot_cold or description:
                fb_leads_ids = lead_edits.values_list('fb_leads_id', flat=True).distinct()

                fb_leads = FbLeads.objects.filter(id__in=fb_leads_ids).exclude(Q(dump_lead=True)).order_by('-created_at')
            else:
                fb_leads = FbLeads.objects.all().exclude(Q(dump_lead=True)).order_by('-created_at')
            if full_name:
                fb_leads = fb_leads.filter(full_name__icontains=full_name)
            if created_at_gte:
                try:
                    created_at_gte_parsed = parse(created_at_gte).date()
                    fb_leads = fb_leads.filter(created_at__gte=created_at_gte_parsed)
                except ValueError:
                    pass  # Handle invalid date format if needed
            if created_at_lte:
                try:
                    created_at_lte_parsed = parse(created_at_lte).date()
                    fb_leads = fb_leads.filter(created_at__lte=created_at_lte_parsed)
                except ValueError:
                    pass  # Handle invalid date format if needed
            if phone_number:
                fb_leads = fb_leads.filter(phone_number__icontains=phone_number)
            if assigned_user:
                fb_leads = fb_leads.filter(assigned_to__name__icontains=assigned_user)
            if project_name:
                fb_leads = fb_leads.filter(project_name__project_name__icontains=project_name)
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
            if re_assigned:
                fb_leads = fb_leads.filter(dump_lead=False, permanent_dump_lead=True)

            fb_leads = fb_leads.order_by('-created_at')
            paginator = CommonPagination()
            paginator.page_size = 50

            result_page = paginator.paginate_queryset(fb_leads, request)
            data = []
            now = timezone.now()
            thirty_day_minutes_ago = now - timedelta(days=30)
            for fb_lead in result_page:
                last_lead_edit = fb_lead.leadedit_set.last()
                if last_lead_edit:
                    last_update_time = last_lead_edit.created_at
                    if now - last_update_time > timedelta(hours=48):
                        fb_lead.status = 'Delayed'
                else:
                    if now - fb_lead.created_time > timedelta(hours=48):
                        fb_lead.status = 'Delayed'
                if fb_lead.created_time < thirty_day_minutes_ago and not last_lead_edit:
                    fb_lead.dump_lead = True
                fb_lead.save()
                data.append(fb_lead)

            serializer = FbLeadSerializer(data, many=True)
            return paginator.get_paginated_response(serializer.data)


    
    def patch(self, request, pk=None, format=None):
                # Get the todo to update
            FbLeads_to_update = FbLeads.objects.get(pk=pk)
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            # request.data['user'] = request.user.id

            serializer = FbLeadAdminSerializer(instance=FbLeads_to_update,data=mutable_data, partial=True)
            token_query = FCMTokens.objects.filter(user=FbLeads_to_update.assigned_to)

            fcm_tokens = [i.device_token for i in token_query if i.device_token!=""]
            notification_data = {"sent_to":FbLeads_to_update.assigned_to, "head":"Facebook Lead Update", "message":"Lead has been updated successfully."}
            notiserializer = NotificationStoreSerializer(data=notification_data)
            if notiserializer.is_valid():
                notiserializer.save()
            try:
                sendPush("Facebook Lead Update", "Lead has been updated successfully.", fcm_tokens)
            except Exception as e:
                print("Error while sending push notification",e)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = Response()

            response.data = {
                'message': 'Fb Leads upated Successfully',
                'data': serializer.data
            }

            return response
    def delete(self, request, pk, format=None):
        FbLeads_to_delete =  FbLeads.objects.get(pk=pk)

            # delete the todo
        FbLeads_to_delete.delete()

        return Response({
            'message': 'Fb Leads upated Successfully',
        })
    
# from django.utils.dateparse import parse_datetime
class TotalCountsLeadStatsAPIView(APIView):
    permission_classes = [IsAuthenticated,]
    def get(self, request, format=None):
        try:
            # Get start_date and end_date from query parameters
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')

            # Parse start_date and end_date strings to datetime objects
            # start_date = parse_datetime(start_date_str) if start_date_str else None
            # end_date = parse_datetime(end_date_str) if end_date_str else None

            # Initialize the base queryset
            queryset = FbLeads.objects.values('assigned_to__name').annotate(
                assigned_to_name=models.F('assigned_to__name'),
                total_leads=Count('id'),
                total_delayed_leads=Count('id', filter=models.Q(dump_lead=True)),
                total_site_visits=Count('id', filter=models.Q(site_visit=True)),
                total_corporate_visits=Count('id', filter=models.Q(corporate_visit=True))
            )

            # Apply date filtering if start_date and end_date are provided
            if start_date and end_date:
                queryset = queryset.filter(created_at__gte=start_date, created_at__lte=end_date)

            # Response data
            data = [{
                'user': stat['assigned_to_name'],
                'stats': {
                    'total_leads': stat['total_leads'],
                    'total_delayed_leads': stat['total_delayed_leads'],
                    'total_site_visits': stat['total_site_visits'],
                    'total_corporate_visits': stat['total_corporate_visits']
                }
            } for stat in queryset]

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LeadEditAPIView(APIView):
    permission_classes = [IsAuthenticated,]
    def get_object(self, pk):
        try:
            return LeadEdit.objects.get(pk=pk)
        except LeadEdit.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
        
        if pk:
            data = self.get_object(pk)
            serializer = LeadEditAdminSerializer(data)
            return Response(serializer.data)

        else:
            data = LeadEdit.objects.all().order_by('-created_at')
            serializer = LeadEditAdminSerializer(data, many=True)

            return Response(serializer.data)
    
    
    def post(self, request):
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            
            serializer = LeadEditAdminSerializer(data=mutable_data)

            # Check if the data passed is valid
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Return Response to User

            response = Response()

            response.data = {
                'message': 'Lead Edit Created Successfully',
                'data': serializer.data
            }
            return response
    
    def patch(self, request, pk=None, format=None):
        try:
            # Get the LeadEdit instance to update
            lead_edit_instance = LeadEdit.objects.get(pk=pk)
            
            # Check if the status_of_lead is 'Dump' in the request data
            status_lead_id = request.data.get('status_of_lead', None)
            if status_lead_id:
                status_lead_instance = StatusLead.objects.get(pk=status_lead_id)
                if status_lead_instance.status_lead.lower() == 'dump':
                # Update the LeadEdit instance
                    serializer = LeadEditAdminSerializer(instance=lead_edit_instance, data=request.data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    
                    # Update the related FbLeads instance to mark it as 'Dump'
                    fb_lead_instance = lead_edit_instance.fb_leads
                    fb_lead_instance.dump_lead = True
                    fb_lead_instance.save()

                    return Response({
                        'message': 'Lead Edit with dump lead updated successfully',
                        'data': serializer.data
                    })
            
                elif status_lead_instance.status_lead.lower() == 'site visit':
                        # Update the LeadEdit instance
                        serializer = LeadEditAdminSerializer(instance=lead_edit_instance, data=request.data, partial=True)
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                        
                        # Update the related FbLeads instance to mark it as 'Site Visit'
                        fb_lead_instance = lead_edit_instance.fb_leads
                        fb_lead_instance.site_visit = True
                        fb_lead_instance.save()

                        return Response({
                            'message': 'Lead Edit with site visit updated successfully',
                            'data': serializer.data
                        })

            
            else:
                serializer = LeadEditAdminSerializer(instance=lead_edit_instance, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                
                return Response({
                    'message': 'Lead Edit updated successfully',
                    'data': serializer.data
                })

        except LeadEdit.DoesNotExist:
            return Response({'message': 'Lead Edit not found'}, status=status.HTTP_404_NOT_FOUND)
    def delete(self, request, pk, format=None):
        LeadEdit_to_delete =  LeadEdit.objects.get(pk=pk)

            # delete the todo
        LeadEdit_to_delete.delete()

        return Response({
            'message': 'Lead Edit upated Successfully',
        })


# ALl dump lead
class FbDumpViewAdminAPIView(APIView):
    permission_classes = [IsAuthenticated,]
    def get_object(self, pk):
        try:
            return FbLeads.objects.get(pk=pk)
        except FbLeads.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
        
        if pk:
            data = self.get_object(pk)
            serializer = FbLeadAdminSerializer(data)
            return Response(serializer.data)

        else:
            data = FbLeads.objects.filter(dump_lead=True).order_by('-created_at')
            serializer = FbLeadAdminSerializer(data, many=True)

            return Response(serializer.data)
    
            

class FbCorporateAdminVisitAPIView(APIView):
    permission_classes = [IsAuthenticated,]
    def get_object(self, pk):
        try:
            return FbLeads.objects.get(pk=pk)
        except FbLeads.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
        
        if pk:
            data = self.get_object(pk)
            serializer = FbLeadAdminSerializer(data)
            return Response(serializer.data)

        else:
            data = FbLeads.objects.filter(corporate_visit=True).order_by('-created_at')
            serializer = FbLeadAdminSerializer(data, many=True)

            return Response(serializer.data)


class FbSiteVisitViewAdminAPIView(APIView):
    permission_classes = [IsAuthenticated,]
    def get_object(self, pk):
        try:
            return FbLeads.objects.get(pk=pk)
        except FbLeads.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
        
        if pk:
            data = self.get_object(pk)
            serializer = FbLeadAdminSerializer(data)
            return Response(serializer.data)

        else:
            data = FbLeads.objects.filter(
                Q(site_visit=True)
            ).order_by('-created_at')
            serializer = FbLeadAdminSerializer(data, many=True)

            return Response(serializer.data)
        



class SalesPersonCountsLeadStatsAPIView(APIView):
    permission_classes = [IsAuthenticated,]

    def get(self, request, format=None):
        try:
            # Get start_date and end_date from query parameters
            start_date_str = request.query_params.get('start_date')
            end_date_str = request.query_params.get('end_date')

            # Convert start_date and end_date strings to datetime objects
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None

            # Initialize the base queryset
            queryset = FbLeads.objects.filter(assigned_to__sales_employee=True, assigned_to__is_active=True).distinct()

            # Apply date filtering if start_date and end_date are provided
            if start_date and end_date:
                queryset = queryset.filter(created_at__range=[start_date, end_date])

            # Aggregate counts for each assigned user
            stats_by_user = queryset.values('assigned_to__name').annotate(
                assigned_to_name=models.F('assigned_to__name'),
                assigned_to_id=models.F('assigned_to__id'),
                total_leads=Count('assigned_to__id'),
                total_delayed_leads=Count('assigned_to__id', filter=models.Q(dump_lead=True)),
                total_site_visits=Count('assigned_to__id', filter=models.Q(site_visit=True)),
                total_corporate_visits=Count('assigned_to__id', filter=models.Q(corporate_visit=True)),
                total_dump_lead=Count('assigned_to__id', filter=models.Q(dump_lead=True)),
                total_booked=Count('assigned_to__id', filter=models.Q(booked=True)),
                total_intersted=Count('assigned_to__id', filter=models.Q(intersted=True)),
                created_at=models.Min('created_at')
            )

            # Response data
            data = [{
                'user': stat['assigned_to_name'],
                'id': stat['assigned_to_id'],
                'stats': {
                    'total_leads': stat['total_leads'],
                    'total_delayed_leads': stat['total_delayed_leads'],
                    'total_site_visits': stat['total_site_visits'],
                    'total_corporate_visits': stat['total_corporate_visits'],
                    'total_dump_lead': stat['total_dump_lead'],
                    'total_booked': stat['total_booked'],
                    'total_intersted': stat['total_intersted'],
                }
            } for stat in stats_by_user]

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        


class NextSheduleTrackAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return LeadEdit.objects.get(pk=pk)
        except LeadEdit.DoesNotExist:
            raise Http404
        
    def get(self, request):
            # Get the current date
        current_date = datetime.now().date()

            # Check if the current date is after June 1st, 2024
        if current_date > datetime(2024, 6, 1).date():
            # Perform the calculation
            # date filter to add after 2 june 2024
            leads_filter_date = datetime(2023, 6, 2)
            sales_users = User.objects.filter(
                Q(sales_employee=True) &
                Q(is_active=True) 
            )
           # all_leads = LeadEdit.objects.filter(created_at__gte=leads_filter_date)
            users_with_tasks = sales_users.annotate(
                notification_count=Count('notificationstore', filter=Q(notificationstore__seen=False,notificationstore__created_at__gte=leads_filter_date))
            )
                
            user_tasks = [{"name": user.name, "count": user.notification_count} for user in users_with_tasks]

            return Response(user_tasks)
        else:
                # Return a response indicating that the calculation should occur after June 1st, 2024
            return Response({'detail': 'The calculation should occur after June 1st, 2024.'}, status=400)

    
                


class BookingDoneAPIview(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return LeadEdit.objects.get(pk=pk)
        except LeadEdit.DoesNotExist:
            raise Http404

    def get(self, request, pk=None, format=None):
        # Get the current date
        current_date = timezone.now().date()

        # Check if the current date is after June 1st, 2024
        if current_date > datetime(2024, 6, 1).date():
            # Proceed with the calculation

            if pk:
                lead_edit = self.get_object(pk)
                serializer = LeadEditSerializer(lead_edit)
                return Response(serializer.data)
            else:
                start_date = request.query_params.get('start_date')
                end_date = request.query_params.get('end_date')

                # Filter leads based on date range
                leads_filter_date = datetime(2024, 6, 2)
                fb_leads = FbLeads.objects.filter(created_at__gte=leads_filter_date)

                if start_date and end_date:
                    try:
                        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
                        end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
                        fb_leads = fb_leads.filter(created_at__range=[start_datetime, end_datetime])
                    except ValueError:
                        return Response({'detail': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

                # Get all users who are salespersons
                salespersons = User.objects.filter(
                    Q(sales_employee=True) & Q(is_active=True)
                )

                # Prepare the response data
                response_data = []
                for agent in salespersons:
                    # Filter the booked leads for each agent separately
                    agent_booked_leads = fb_leads.filter(assigned_to=agent, booked=True)
                    booked_count = agent_booked_leads.count()

                    response_data.append({
                        'agent_id': agent.id,
                        'agent_name': agent.name,
                        'shedule_count': booked_count
                    })

                return Response(response_data, status=200)
        else:
            # Return a response indicating that the calculation should occur after June 1st, 2024
            return Response({'detail': 'The calculation should occur after June 1st, 2024.'}, status=400)
            




class LeadEditDataAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LeadEditSerializer

    def get_queryset(self):
        # Get the FbLeads ID from the request query parameters
        fb_lead_id = self.request.query_params.get('fb_lead_id')

        # Filter LeadEdit queryset by FbLeads ID
        queryset = LeadEdit.objects.filter(fb_leads__id=fb_lead_id)

        # Annotate queryset to count different modes for each user
        queryset = queryset.values('user').annotate(
            call_count=Count('mode__mode_lead', filter=models.Q(mode__mode_lead='Call')),
            site_visit_count=Count('mode__mode_lead', filter=models.Q(mode__mode_lead='Site Visit'))
        )

        # Annotate queryset with the maximum count for each user
        queryset = queryset.annotate(
            max_call_count=F('call_count'),
            max_site_visit_count=F('site_visit_count')
        )

        return queryset


