from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.http.response import Http404
from rest_framework.response import Response
from rest_framework import status
from social.models import FbLeads, LeadEdit, StatusLead, NotificationStore
from django.utils import timezone
from .serializer import LeadGroupSerializer, NextScheduledLeadSerializer, LeadEditGroupSerializer
from django.db.models import Count, Q, Case, When, IntegerField,F
from datetime import timedelta
from django.db.models.functions import TruncMonth, TruncQuarter, TruncYear
from dateutil.relativedelta import relativedelta
from social.serializer import FbLeadSerializer
from realEstate.pagination import CommonPagination
from django.db.models import Subquery, OuterRef, Count
from datetime import datetime
from rest_framework import status
import re
from django.utils.dateparse import parse_date
from account.models import User

class PRHighlightMetrics(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        all_leads = FbLeads.objects.all() 

        dump_status = StatusLead.objects.get(status_lead='Dump')
        booked_status = StatusLead.objects.get(status_lead='Booked')

        lead_edits = LeadEdit.objects.all()
        leads = FbLeads.objects.all()
        # Exclude leads with any LeadEdit entries having status_of_lead "dump" or "booked"
        excluded_leads = lead_edits.exclude(status_of_lead__in=[dump_status, booked_status]).values_list('fb_leads', flat=True)

        # Get the count of distinct FbLeads that do not have excluded statuses in their LeadEdit entries
        lead_count = leads.exclude(id__in=excluded_leads).distinct().count()
        
        today = timezone.now().date()
        # today_lead = leads.filter(created_at__date=today)
        
        next_scheduled_lead = lead_edits.filter(next_schedule_date__gte=today).exclude(status_of_lead__in=[dump_status, booked_status]).values_list('fb_leads', flat=True)
        # next_scheduled_lead = leads.exclude(id__in=next_scheduled_lead).distinct().count()

        today_tasks = NotificationStore.objects.filter(seen=False,created_at__date=today)
        return Response({'pending': lead_count, 'today_task':today_tasks.count(), 'next_scheduled_leads':len(list(set(next_scheduled_lead)))})


class PRHighlightMetricsNumericDataPending(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            dump_status = StatusLead.objects.get(status_lead='Dump')
            booked_status = StatusLead.objects.get(status_lead='Booked')
            
            lead_edits = LeadEdit.objects.all()
            leads = FbLeads.objects.all()
            excluded_leads = lead_edits.exclude(status_of_lead__in=[dump_status, booked_status]).values_list('fb_leads', flat=True)

            # Get the count of distinct FbLeads that do not have excluded statuses in their LeadEdit entries
            lead_count = leads.exclude(id__in=excluded_leads).distinct()


            # Paginate the results
            paginator = CommonPagination()
            paginator.page_size = 50
            result_page = paginator.paginate_queryset(lead_count, request)
            
            # Serialize the data
            serializer = FbLeadSerializer(result_page, many=True)

            return paginator.get_paginated_response(serializer.data)
        except StatusLead.DoesNotExist:
            return Response({'detail': 'StatusLead not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PRHighlightMetricsNumericDataPendingNextScheduleTask(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        dump_status = StatusLead.objects.get(status_lead='Dump')
        booked_status = StatusLead.objects.get(status_lead='Booked')

        lead_edits = LeadEdit.objects.all()
        leads = FbLeads.objects.all()
        today = timezone.now().date()
        next_scheduled_leads = lead_edits.filter(next_schedule_date__gte=today).exclude(status_of_lead__in=[dump_status, booked_status]).values_list('fb_leads', flat=True)
        paginator = CommonPagination()
        paginator.page_size = 50

       
        next_scheduled_leads_data = FbLeadSerializer(FbLeads.objects.filter(id__in=next_scheduled_leads).distinct(), many=True).data
        result_page = paginator.paginate_queryset(next_scheduled_leads_data, request)

        return paginator.get_paginated_response(result_page)


class PRHighlightMetricsNumericDataPendingTodayTask(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
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

            # Paginate the results
            paginator = CommonPagination()
            paginator.page_size = 50
            result_page = paginator.paginate_queryset(leads, request)

            # Serialize the data
            serializer = FbLeadSerializer(result_page, many=True)

            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class LeadsOverview(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        all_leads = FbLeads.objects.all()
        today = timezone.now().date()
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if not start_date and not end_date:
            start_date = today
            end_date = today

        # Filter leads within the date range
        leads = FbLeads.objects.filter(created_at__date__range=[start_date, end_date])

        # Group by date and lead source, then count the number of leads in each group
        lead_counts = leads.values('created_at__date', 'lead_source__lead_source').annotate(lead_count=Count('id')).order_by('created_at__date', 'lead_source__lead_source')

        # Prepare the response data
        data = []
        for lead_count in lead_counts:
            data.append({
                'date': lead_count['created_at__date'],
                'lead_source': lead_count['lead_source__lead_source'],
                'lead_count': lead_count['lead_count'],
            })

        return Response(data)

class TaskOverview(APIView):
    permission_classes = [IsAuthenticated]

    # def get(self, request):
    #     start_date = datetime(2024, 6, 1)
    #     today = timezone.now().date()

    #     notifications = NotificationStore.objects.filter(seen=False, created_at__date=today)
    #     lead_ids = []
    #     for notification in notifications:
    #         match = re.search(r'Lead ID:(\d+)', notification.message)
    #         if match:
    #             lead_ids.append(int(match.group(1)))

    #     lead_groups = FbLeads.objects.filter(
    #         id__in=lead_ids,assigned_to__is_active=True,assigned_to__sales_employee=True).exclude(booked=True).exclude(dump_lead=True).values('assigned_to__name').annotate(
    #         lead_count=Count('assigned_to__id')
    #     ).order_by('-lead_count')
    #     serializer = LeadGroupSerializer(lead_groups, many=True)

    #     return Response(serializer.data)
   

    def get(self, request):
            # Get the current date
        current_date = datetime.now().date()
        def get_object(self, pk):
            try:
                return LeadEdit.objects.get(pk=pk)
            except LeadEdit.DoesNotExist:
                raise Http404

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
            user_tasks = [{"assigned_to": user.name, "lead_count": user.notification_count} for user in users_with_tasks]

            return Response(user_tasks)
        else:
                # Return a response indicating that the calculation should occur after June 1st, 2024
            return Response({'detail': 'The calculation should occur after June 1st, 2024.'}, status=400)
    def extract_lead_id(self, text):
        import re
        match = re.search(r'\b\d+\b', text)  # Adjust the regex based on your exact ID format
        return int(match.group()) if match else None


class UpcomingSiteVisit(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        lead_edits = LeadEdit.objects.filter(user__is_active=True)
        leads = FbLeads.objects.all()
        
        today = timezone.now().date()
        
        # Get next scheduled leads
        next_scheduled_leads = lead_edits.filter(next_schedule_date__gte=today, next_schedule_mode__mode_lead="Site visit").order_by('next_schedule_date')
        
        # Serialize next scheduled leads
        next_scheduled_leads_data = NextScheduledLeadSerializer(next_scheduled_leads, many=True).data

        return Response(next_scheduled_leads_data)

class LeadsHighlighted(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        all_leads = FbLeads.objects.all().exclude(Q(dump_lead=True)).order_by("-created_at")

        # Filter leads created today
        leads_today = all_leads.filter(created_at__date=today)
        
        # Filter leads created in the last 7 days
        day_7 = today - timedelta(days=6)
        leads_7_day = all_leads.filter(created_at__date__range=[day_7, today])

        # Get booked status
        booked_status = StatusLead.objects.get(status_lead='Booked')

        # Get the latest LeadEdit for each lead
        latest_lead_edit_subquery = LeadEdit.objects.filter(
            fb_leads=OuterRef('pk')
        ).order_by('-created_at').values('pk')[:1]

        # Filter leads based on the latest LeadEdit status being 'Booked'
        leads_booked = all_leads.filter(
            leadedit__pk__in=Subquery(latest_lead_edit_subquery),
            leadedit__status_of_lead=booked_status
        ).distinct()
        

        # Count booked leads
        if not start_date and not end_date:
            lead_count_booked = leads_booked.count()
        else:
            lead_count_booked = leads_booked.filter(
                created_at__date__range=[start_date, end_date]
            ).count()
        leads_booked_count = leads_booked.count()
        leads_7_day_data = FbLeadSerializer(leads_7_day, many=True).data


        # Prepare the response data
        data = {
            "leads_today": leads_today.count(),
            "leads_7_day": leads_7_day.count(),
            "booking": leads_booked_count,
            "leads_7_day_data": leads_7_day_data,
        }

        return Response(data)


# class LeadsHighlightedNumericData(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         all_leads = FbLeads.objects.all()
#         today = timezone.now().date()
#         start_date = request.GET.get('start_date')
#         end_date = request.GET.get('end_date')

#         leads = all_leads.filter(created_at=today)
#         lead_edits = LeadEdit.objects.all()

#         # Filter leads within the date range
#         day_7 = today - timedelta(days=7)
#         leads_7 = all_leads.filter(created_at__gte=day_7)

#         # Group by date and lead source, then count the number of leads in each group
#         booked_status = StatusLead.objects.get(status_lead='Booked')

#         # Get the excluded leads
#         excluded_leads = lead_edits.filter(status_of_lead__in=[booked_status]).values_list('fb_leads', flat=True)

#         # Get filtered leads excluding excluded leads
#         filtered_leads = leads.exclude(id__in=excluded_leads).distinct()

#         # Today's leads
#         today_leads = leads.filter(created_at__date=today)

#         # Next scheduled leads
#         next_scheduled_leads = lead_edits.filter(next_schedule_date__gte=today).exclude(status_of_lead__in=[booked_status]).values_list('fb_leads', flat=True)

#         # Today's tasks
#         today_tasks = NotificationStore.objects.filter(seen=False)

#         # Paginate the results
#         filtered_leads_paginator = Paginator(filtered_leads, 50)
#         today_leads_paginator = Paginator(today_leads, 50)
#         next_scheduled_leads_paginator = Paginator(FbLeads.objects.filter(id__in=next_scheduled_leads).distinct(), 50)
#         today_tasks_paginator = Paginator(today_tasks, 50)

#         # Get page number from request
#         filtered_leads_page_number = request.GET.get('filtered_leads_page', 1)
#         today_leads_page_number = request.GET.get('today_leads_page', 1)
#         next_scheduled_leads_page_number = request.GET.get('next_scheduled_leads_page', 1)
#         today_tasks_page_number = request.GET.get('today_tasks_page', 1)

#         # Get paginated data
#         filtered_leads_page_obj = filtered_leads_paginator.get_page(filtered_leads_page_number)
#         today_leads_page_obj = today_leads_paginator.get_page(today_leads_page_number)
#         next_scheduled_leads_page_obj = next_scheduled_leads_paginator.get_page(next_scheduled_leads_page_number)
#         today_tasks_page_obj = today_tasks_paginator.get_page(today_tasks_page_number)

#         # Serialize the data
#         filtered_leads_data = FbLeadSerializer(filtered_leads_page_obj, many=True).data
#         today_leads_data = FbLeadSerializer(today_leads_page_obj, many=True).data
#         next_scheduled_leads_data = FbLeadSerializer(next_scheduled_leads_page_obj, many=True).data
#         today_tasks_data = NotificationStoreSerializer(today_tasks_page_obj, many=True).data

#         return Response({
#             'filtered_leads': {
#                 'paginator': {
#                     'total_pages': filtered_leads_paginator.num_pages,
#                     'current_page': filtered_leads_page_obj.number,
#                     'has_next': filtered_leads_page_obj.has_next(),
#                     'has_previous': filtered_leads_page_obj.has_previous()
#                 },
#                 'data': filtered_leads_data,
#             },
#             'today_leads': {
#                 'paginator': {
#                     'total_pages': today_leads_paginator.num_pages,
#                     'current_page': today_leads_page_obj.number,
#                     'has_next': today_leads_page_obj.has_next(),
#                     'has_previous': today_leads_page_obj.has_previous()
#                 },
#                 'data': today_leads_data,
#             },
#             'next_scheduled_leads': {
#                 'paginator': {
#                     'total_pages': next_scheduled_leads_paginator.num_pages,
#                     'current_page': next_scheduled_leads_page_obj.number,
#                     'has_next': next_scheduled_leads_page_obj.has_next(),
#                     'has_previous': next_scheduled_leads_page_obj.has_previous()
#                 },
#                 'data': next_scheduled_leads_data,
#             },
#             'today_tasks': {
#                 'paginator': {
#                     'total_pages': today_tasks_paginator.num_pages,
#                     'current_page': today_tasks_page_obj.number,
#                     'has_next': today_tasks_page_obj.has_next(),
#                     'has_previous': today_tasks_page_obj.has_previous()
#                 },
#                 'data': today_tasks_data,
#             },
#         })
class LeadsSvBook(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        all_leads = FbLeads.objects.all()

        # Get booked status
        booked_status = StatusLead.objects.get(status_lead='Booked')

        # Get the latest LeadEdit for each lead
        latest_lead_edit_subquery = LeadEdit.objects.filter(
            fb_leads=OuterRef('pk')
        ).order_by('-created_at').values('pk')[:1]

        # Filter leads based on the latest LeadEdit status being 'Booked'
        leads_booked = all_leads.filter(
            leadedit__pk__in=Subquery(latest_lead_edit_subquery),
            leadedit__status_of_lead=booked_status
        ).exclude(Q(dump_lead=True))

        # Count leads
        if not start_date and not end_date:
            lead_count_book = leads_booked.count()
            lead_count_sv = all_leads.filter(site_visit=True).distinct().count()
        else:
            lead_count_book = leads_booked.filter(created_at__date__range=[start_date, end_date]).count()
            lead_count_sv = all_leads.filter(created_at__date__range=[start_date, end_date], site_visit=True).distinct().count()

        return Response({'booking_sceured':lead_count_book, "site visits":lead_count_sv})

class LeadsSvBookNumericData(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        leads = FbLeads.objects.all()
        lead_edits = LeadEdit.objects.all()

        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        booked_status = StatusLead.objects.get(status_lead='Booked')
        site_visit_status = StatusLead.objects.get(status_lead='Site Visit')

        if not start_date and not end_date:
            booked_leads = leads.filter(booked=True).distinct()
            site_visit_leads = leads.filter(site_visit=True).distinct()
        else:
            booked_leads = leads.filter(created_at__date__range=[start_date, end_date], booked=True).distinct()
            site_visit_leads = leads.filter(created_at__date__range=[start_date, end_date], site_visit=True).distinct()

        # Serialize the data
        booked_leads_data = FbLeadSerializer(booked_leads, many=True).data
        site_visit_leads_data = FbLeadSerializer(site_visit_leads, many=True).data

        return Response({
            'booking_sceured': booked_leads_data,
            'site_visits': site_visit_leads_data
        })

class LeadSourceAna(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        all_leads = FbLeads.objects.all()
        today = timezone.now().date()
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if not start_date and not end_date:
            start_date = today
            end_date = today

        # Filter leads within the date range
        leads = all_leads.filter(created_at__date__range=[start_date, end_date])

        # Group by date and lead source, then count the number of leads in each group
        lead_counts = leads.values('lead_source__lead_source').annotate(lead_count=Count('id')).order_by('lead_source__lead_source')

        data = []
        for lead_count in lead_counts:
            data.append({
                'lead_source': lead_count['lead_source__lead_source'],
                'lead_count': lead_count['lead_count'],
            })

        return Response(data)

class AgentPerformanceReport(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        # Define the default start date
        default_start_date = datetime(2024, 6, 1)
        
        # Get start_date and end_date from request query parameters
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        # Convert query parameters to datetime objects or use default values
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d") if start_date_str else default_start_date
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d") if end_date_str else timezone.now()
        except ValueError:
            return Response({'detail': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

        # Filter FbLeads based on the date range and assigned_to being active salespersons
        leads = FbLeads.objects.filter(
            created_at__range=[start_date, end_date],
            assigned_to__is_active=True,
            assigned_to__sales_employee=True
        )

        # Annotate counts
        lead_counts = leads.values('assigned_to__name').annotate(
            booked_count=Count(Case(When(booked=True, then=1), output_field=IntegerField())),
            site_visit_count=Count(Case(When(site_visit=True, then=1), output_field=IntegerField())),
            total_count=Count('id')
        ).order_by('assigned_to__name')

        # Serialize the data
        serializer = LeadEditGroupSerializer(lead_counts, many=True)

        return Response(serializer.data)


class TopPerformingAgent(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
         # Convert start_date and end_date to date objects if they exist
        if start_date:
            start_date = parse_date(start_date)
        if end_date:
            end_date = parse_date(end_date)

        # Get StatusLead objects for 'Booked' and 'Site Visit'
        booked_status = StatusLead.objects.get(status_lead='Booked')

        # Query FbLeads based on the date range and assigned_to
        if  start_date and  end_date:
            leads = FbLeads.objects.filter(created_at__range=[start_date, end_date])
        else:
            leads = FbLeads.objects.all()

        lead_counts = leads.filter(assigned_to__is_active=True).values('assigned_to__name').annotate(
            booked_count=Count(Case(When(booked=True, then=1), output_field=IntegerField())),
            site_visit_count=Count(Case(When(site_visit=True, then=1), output_field=IntegerField())),
            total_count=Count('id')
        ).order_by('assigned_to__name')

        # Get the top entries by each count
        top_booked = lead_counts.order_by('-booked_count')[:1]
        top_site_visit = lead_counts.order_by('-site_visit_count')[:1]
        top_total = lead_counts.order_by('-total_count')[:1]

        # Combine the results into one queryset
        combined_results = list(top_booked) + list(top_site_visit) + list(top_total)

        # Serialize the combined data
        serializer = LeadEditGroupSerializer(combined_results, many=True)

        return Response(serializer.data)

class AllTimeLeads(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        # Get StatusLead objects for 'Booked' and 'Site Visit'
        booked_status = StatusLead.objects.get(status_lead='Booked')

        # Query FbLeads based on the date range and assigned_to
        if not start_date and not end_date:
            leads = FbLeads.objects.filter(created_at__range=[start_date, end_date])
        else:
            leads = FbLeads.objects.all()
        total_count = leads.count()

        return Response({"total_leads":total_count})

class PerformanceTrend(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        period = request.GET.get('period', 'all')  # Default to 'all'
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        # Calculate date range based on the period type
        if period == 'month':
            start_date = timezone.now() - relativedelta(months=12)
            trunc_period = TruncMonth('created_at')
        elif period == 'quarter':
            start_date = timezone.now() - relativedelta(months=12)
            trunc_period = TruncQuarter('created_at')

        elif period == 'year':
            start_date = timezone.now() - relativedelta(years=10)
            trunc_period = TruncYear('created_at')

        else:
            # Default large range if no period specified
            start_date = timezone.now() - relativedelta(years=10)
            trunc_period = TruncYear('created_at')


        # Ensure end_date is always set to now
        end_date = timezone.now()

        # Query FbLeads based on the date range
        leads = FbLeads.objects.filter(created_at__range=[start_date, end_date])

        # Annotate counts for booked leads, site visit leads, and total leads grouped by the selected period
        lead_counts = leads.annotate(period=trunc_period).values('period').annotate(
            booked_count=Count(Case(When(booked=True, then=1), output_field=IntegerField())),
            site_visit_count=Count(Case(When(site_visit=True, then=1), output_field=IntegerField())),
            total_count=Count('id')
        ).order_by('period')

        return Response(lead_counts)

class PlatformComp(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        period = request.GET.get('period', 'all')  # Default to 'all'
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        # Calculate date range based on the period type
        if period == 'month':
            start_date = timezone.now() - relativedelta(months=12)
            trunc_period = TruncMonth('created_at')
        elif period == 'quarter':
            start_date = timezone.now() - relativedelta(months=12)
            trunc_period = TruncQuarter('created_at')

        elif period == 'year':
            start_date = timezone.now() - relativedelta(years=10)
            trunc_period = TruncYear('created_at')

        else:
            # Default large range if no period specified
            start_date = timezone.now() - relativedelta(years=10)
            trunc_period = TruncYear('created_at')

        # Ensure end_date is always set to now
        end_date = timezone.now()

        # Query FbLeads based on the date range
        leads = FbLeads.objects.filter(created_at__range=[start_date, end_date])

        # Annotate counts for booked leads, site visit leads, and total leads grouped by the selected period
        lead_counts = leads.annotate(period=trunc_period).values('period', 'lead_source__lead_source').annotate(
            booked_count=Count(Case(When(booked=True, then=1), output_field=IntegerField())),
            site_visit_count=Count(Case(When(site_visit=True, then=1), output_field=IntegerField())),
            total_count=Count('id')
        ).order_by('period', 'lead_source__lead_source')

        return Response(lead_counts)


class StatusCountOfLeads(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        # Fetch date filters from request query parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # Convert the start_date and end_date to datetime objects
        if start_date:
            start_date = parse_date(start_date)
        if end_date:
            end_date = parse_date(end_date)

        # Fetch the latest LeadEdit for each FbLeads
        latest_lead_edit = LeadEdit.objects.filter(
            fb_leads=OuterRef('fb_leads')
        ).order_by('-created_at')

        # Apply date filters to the queryset
        if start_date and end_date:
            latest_lead_edit = latest_lead_edit.filter(
                created_at__date__range=(start_date, end_date)
            )
        elif start_date:
            latest_lead_edit = latest_lead_edit.filter(
                created_at__date__gte=start_date
            )
        elif end_date:
            latest_lead_edit = latest_lead_edit.filter(
                created_at__date__lte=end_date
            )

        latest_lead_edit_per_fb_lead = LeadEdit.objects.filter(
            pk__in=Subquery(latest_lead_edit.values('pk')[:1])
        )

        status_lead_counts = latest_lead_edit_per_fb_lead.filter(
            status_of_lead__isnull=False
        ).values('status_of_lead').annotate(
            count=Count('status_of_lead')
        ).annotate(
            status_name=F('status_of_lead__status_lead')
        ).order_by('status_of_lead')

        return Response(status_lead_counts, status=status.HTTP_200_OK)

class TotalLeadDumpCorporateSiteVisitCount(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        # Fetch date filters from request query parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # Convert the start_date and end_date to datetime objects
        if start_date:
            start_date = parse_date(start_date)
        if end_date:
            end_date = parse_date(end_date)

        # Build the filter criteria based on the date range
        date_filter = {}
        if start_date and end_date:
            date_filter['created_at__date__range'] = (start_date, end_date)
        elif start_date:
            date_filter['created_at__date__gte'] = start_date
        elif end_date:
            date_filter['created_at__date__lte'] = end_date

        # Count dump leads with date filter
        dump_leads_count = FbLeads.objects.filter(dump_lead=True, **date_filter).count()
        
        # Count permanent dump leads with date filter
        permanent_dump_leads_count = FbLeads.objects.filter(dump_lead=True, permanent_dump_lead=True, **date_filter).count()

        # Count corporate visits with date filter
        corporate_visit_count = FbLeads.objects.filter(corporate_visit=True, **date_filter).count()

        # Count site visits with date filter
        site_visit_count = FbLeads.objects.filter(site_visit=True, **date_filter).count()

        # Count total leads with date filter
        total_leads_count = FbLeads.objects.filter(**date_filter).count()

        response_data = {
            'site_visit': site_visit_count,
            'corporate_visit': corporate_visit_count,
            'dump_leads': dump_leads_count,
            'permanent_dump_leads': permanent_dump_leads_count,
            'total_leads': total_leads_count
        }

        return Response(response_data, status=status.HTTP_200_OK)


#  count of site visit  according to project

class TotalSiteVisitAccordingToProject(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        # Fetch date filters from request query parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # Convert the start_date and end_date to datetime objects
        if start_date:
            start_date = parse_date(start_date)
        if end_date:
            end_date = parse_date(end_date)

        # Build the filter criteria based on the date range
        date_filter = {}
        if start_date and end_date:
            date_filter['created_at__date__range'] = (start_date, end_date)
        elif start_date:
            date_filter['created_at__date__gte'] = start_date
        elif end_date:
            date_filter['created_at__date__lte'] = end_date

        # Filter FbLeads where site_visit=True and apply date filter
        fb_leads = FbLeads.objects.filter(site_visit=True, **date_filter)

        # Initialize counters
        project_counts = {"CI Grand": 0, "CI ESTATE": 0}
        both_projects_count = 0
        total_visits = 0
        leads_with_single_project = {"CI Grand": 0, "CI ESTATE": 0}
        leads_with_both_projects = set()
        unique_leads_count = set()

        for fb_lead in fb_leads:
            projects = fb_lead.project_name.all()
            project_names = [project.project_name for project in projects]
            unique_projects = set(project_names)
            unique_leads_count.add(fb_lead.id)
            
            # Check if lead has both projects
            if len(project_names) > 1:
                both_projects_count += 1
                leads_with_both_projects.add(fb_lead.id)
                for project_name in project_names:
                    if project_name in project_counts:
                        project_counts[project_name] += 1
            else:
                # Only one project for this lead
                for project_name in project_names:
                    if project_name in project_counts:
                        project_counts[project_name] += 1
                        leads_with_single_project[project_name] += 1

        # Total visits count (considering each project for every lead)
        total_visits = len(unique_leads_count)

        # Prepare response data
        response_data = [
            {"project_name": "CI Grand", "count": leads_with_single_project["CI Grand"]},
            {"project_name": "CI ESTATE", "count": leads_with_single_project["CI ESTATE"]},
            {"project_name": "Both Projects Count", "count": both_projects_count},
            {"project_name": "Total Site Visits", "count": total_visits}
        ]

        return Response(response_data, status=status.HTTP_200_OK)