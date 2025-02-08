from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http.response import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from social.serializer import FbLeadSerializer
from social.models import FbLeads,LeadSource,MediumOfLead
from django.utils.timezone import make_aware
from datetime import datetime
from propertyStatus.models import UnitNo
from propertyStatus.serializer import UnitNoSerializer
from django.utils.timezone import now
from django.db.models import Count
from datetime import datetime, timedelta
from account.models import User

class SourceCountOverviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get start date and end date from query parameters
            start_date_str = request.query_params.get('start_date')
            end_date_str = request.query_params.get('end_date')

            # Convert start date and end date strings to datetime objects if provided
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None

            # Get the lead source to filter by from query parameters
            lead_source_name = request.query_params.get('lead_source')

            # Get all MediumOfLead objects
            mediums = MediumOfLead.objects.all()

            # Initialize dictionary to store counts
            medium_counts = []

            # Loop through each MediumOfLead and count the associated FbLeads dynamically
            for medium in mediums:
                # Initialize dictionary for the current medium
                medium_info = {'all_sources': []}

                # Get all sources for the current medium
                sources = LeadSource.objects.filter(medium_of_lead=medium)

                # Initialize total count for the current medium
                total_count = 0
                total_intrest = 0
                total_dump = 0
                total_site_visit = 0

                # Loop through each source and count the associated FbLeads dynamically
                for source in sources:
                    # Apply date filtering if start_date and end_date are provided
                    leads_query = FbLeads.objects.filter(lead_source=source)
                    if start_date:
                        leads_query = leads_query.filter(created_at__gte=start_date)
                    if end_date:
                        leads_query = leads_query.filter(created_at__lte=end_date)

                    # Filter by lead source if specified
                    if lead_source_name:
                        leads_query = leads_query.filter(lead_source__lead_source=lead_source_name)

                    # Count the leads for the source
                    count = leads_query.count()
                    data_dict = {}
                    data_dict['name'] = f'{source.lead_source.replace(" ", "_")}'
                    data_dict['total_leads'] = count
                    total_count += count

                    # Include counts for other activities (interested, dump, site visit) if needed
                    interested_count = leads_query.filter(intersted=True).count()
                    dump_count = leads_query.filter(dump_lead=True).count()
                    site_visit_count = leads_query.filter(site_visit=True).count()

                    # Add counts for other activities to the dictionary
                    data_dict['interested_leads'] = interested_count
                    total_intrest += interested_count

                    data_dict['dump_leads'] = dump_count
                    total_dump += dump_count

                    data_dict['site_visit_leads'] = site_visit_count
                    total_site_visit += site_visit_count

                    medium_info['all_sources'].append(data_dict)
                
                # Add total count for the current medium to the dictionary
                medium_info['total_count'] = total_count
                medium_info['interested_leads'] = total_intrest
                medium_info['dump_leads'] = total_dump
                medium_info['site_visit_leads'] = total_site_visit
                medium_info['name'] = medium.medium.replace(' ', '_')

                # Add the medium's information to the medium_counts dictionary
                medium_counts.append(medium_info)

            # Return the counts
            return Response(medium_counts, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class BookedAvailableUnit(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        # Query for booked units, available units, and hold units
        booked_units = UnitNo.objects.filter(booked=True)
        available_units = UnitNo.objects.filter(available=True)
        hold_units = UnitNo.objects.filter(hold=True)

        # Count of each type
        booked_count = booked_units.count()
        available_count = available_units.count()
        hold_count = hold_units.count()

        # Serialize the data
        booked_units_serialized = UnitNoSerializer(booked_units, many=True).data
        available_units_serialized = UnitNoSerializer(available_units, many=True).data
        hold_units_serialized = UnitNoSerializer(hold_units, many=True).data

        # Prepare the response
        response_data = {
            'booked_units': {
                'count': booked_count,
                'units': booked_units_serialized,
            },
            'available_units': {
                'count': available_count,
                'units': available_units_serialized,
            },
            'hold_units': {
                'count': hold_count,
                'units': hold_units_serialized,
            }
        }

        return Response(response_data)
    


class TopPerformerAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        # Get the current date
        today = now()

        # Calculate the first and last day of the previous month
        first_day_of_current_month = today.replace(day=1)
        last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
        first_day_of_previous_month = last_day_of_previous_month.replace(day=1)

        # Get optional date filter from query parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            start_date = first_day_of_previous_month
        
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            end_date = last_day_of_previous_month

        # Filter bookings by date
        bookings = FbLeads.objects.filter(booked=True, created_time__range=[start_date, end_date])

        # Annotate the count of bookings per user and get top 5 performers
        top_performers = bookings.values('assigned_to').annotate(bookings_count=Count('id')).order_by('-bookings_count')[:5]

        performers_data = []
        for performer in top_performers:
            user_id = performer['assigned_to']
            bookings_count = performer['bookings_count']
            if user_id:
                user = User.objects.get(id=user_id)
                performers_data.append({
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'bookings_count': bookings_count,
                })

        response_data = {
            'top_performers': performers_data
        }

        return Response(response_data)