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
from django.utils.timezone import make_naive

class LeadCountsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get start_date and end_date from query parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # Initialize the base queryset
        queryset = FbLeads.objects.all()

        # Apply date filtering if start_date and end_date are provided
        if start_date and end_date:
            queryset = queryset.filter(created_at__range=[start_date, end_date])

        # Create a naive datetime object for June 1, 2024
        # june_1_2024 = datetime(2024, 6, 1)

        # Filter queryset to include only records created after June 1, 2024
        queryset = queryset.filter()

        # Get counts for each field
        site_visit_count = queryset.filter(site_visit=True).count()
        dump_lead_count = queryset.filter(dump_lead=True).count()
        booked_count = queryset.filter(booked=True).count()
        corporate_visit_count = queryset.filter(corporate_visit=True).count()
        interested_count = queryset.filter(intersted=True).count()
        total_count = queryset.count()
        lead_yet_to_be_contacted = total_count - (
            site_visit_count + dump_lead_count + booked_count + corporate_visit_count + interested_count
        )


        # Prepare response data
        data = {
            'site_visit_count': site_visit_count,
            'dump_lead_count': dump_lead_count,
            'booked_count': booked_count,
            'corporate_visit_count': corporate_visit_count,
            'interested_count': interested_count,
            'total_count': total_count,
            'lead_yet_to_be_contacted': lead_yet_to_be_contacted  # New field for unfed leads
        }

        return Response(data)
    

class SourceTypeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        medium = request.query_params.get('medium')
        if medium is None or medium == '':
            sources = MediumOfLead.objects.all()
            all_medium = []
            for source in sources:
                all_medium.append(source.medium.replace(" ", "_"))
            return Response({"sources":all_medium}, status=200)
            
        else:
            medium_obj = MediumOfLead.objects.get(medium=medium)
            sources = LeadSource.objects.filter(medium_of_lead=medium_obj)
            all_source = []
            for source in sources:
                all_source.append(f'{source.lead_source.replace(" ", "_")}')
            
            return Response({"sources":all_source}, status=200)

class SourceCountAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            # Get the lead source to filter by from query parameters
            lead_source_name = request.query_params.get('lead_source')

            # Get the start and end date from query parameters
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')

            # Convert the dates to datetime objects if provided
            if start_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            if end_date:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')

            # Get all MediumOfLead objects
            mediums = MediumOfLead.objects.all()

            # Initialize list to store counts
            medium_counts = []

            # Loop through each MediumOfLead and count the associated FbLeads dynamically
            for medium in mediums:
                # Initialize dictionary for the current medium
                medium_info = {'all_sources': []}

                # Get all sources for the current medium
                sources = LeadSource.objects.filter(medium_of_lead=medium)

                # Initialize total counts for the current medium
                total_count = 0
                total_interested = 0
                total_dump = 0
                total_site_visit = 0
                total_permanent_dump = 0
                total_booked = 0
                total_corporate_visit = 0
                total_block_enquiry = 0
                total_call_not_received = 0
                total_do_not_call = 0
                total_good_lead = 0
                total_re_visit = 0
                total_poor_lead = 0
                total_may_be = 0
                total_untouched = 0

                # Loop through each source and count the associated FbLeads dynamically
                for source in sources:
                    # Build the query for leads, including date filtering
                    leads_query = FbLeads.objects.filter(lead_source=source)

                    # Apply date filtering if start_date and end_date are provided
                    if start_date and end_date:
                        leads_query = leads_query.filter(created_at__range=(start_date, end_date))
                    elif start_date:
                        leads_query = leads_query.filter(created_at__gte=start_date)
                    elif end_date:
                        leads_query = leads_query.filter(created_at__lte=end_date)

                    # Filter by lead source if specified
                    if lead_source_name:
                        leads_query = leads_query.filter(lead_source__lead_source=lead_source_name)

                    # Count the leads for the source
                    count = leads_query.count()
                    data_dict = {'name': source.lead_source.replace(" ", "_"), 'total_leads': count}
                    total_count += count

                    # Include counts for all other activities
                    interested_count = leads_query.filter(intersted=True).count()
                    dump_count = leads_query.filter(dump_lead=True).count()
                    site_visit_count = leads_query.filter(site_visit=True).count()
                    permanent_dump_count = leads_query.filter(permanent_dump_lead=True).count()
                    booked_count = leads_query.filter(booked=True).count()
                    corporate_visit_count = leads_query.filter(corporate_visit=True).count()
                    block_enquiry_count = leads_query.filter(block_enquiry=True).count()
                    call_not_received_count = leads_query.filter(call_not_recevied=True).count()
                    do_not_call_count = leads_query.filter(do_not_call=True).count()
                    good_lead_count = leads_query.filter(good_lead=True).count()
                    re_visit_count = leads_query.filter(re_visit=True).count()
                    poor_lead_count = leads_query.filter(poor_lead=True).count()
                    may_be_count = leads_query.filter(may_be=True).count()

                    # Add counts for all other activities to the dictionary
                    data_dict.update({
                        'interested_leads': interested_count,
                        'dump_leads': dump_count,
                        'site_visit_leads': site_visit_count,
                        'permanent_dump_leads': permanent_dump_count,
                        'booked_leads': booked_count,
                        'corporate_visit_leads': corporate_visit_count,
                        'block_enquiry_leads': block_enquiry_count,
                        'call_not_received_leads': call_not_received_count,
                        'do_not_call_leads': do_not_call_count,
                        'good_leads': good_lead_count,
                        're_visit_leads': re_visit_count,
                        'poor_leads': poor_lead_count,
                        'may_be_leads': may_be_count,
                    })

                    # Update total counts for the current medium
                    total_interested += interested_count
                    total_dump += dump_count
                    total_site_visit += site_visit_count
                    total_permanent_dump += permanent_dump_count
                    total_booked += booked_count
                    total_corporate_visit += corporate_visit_count
                    total_block_enquiry += block_enquiry_count
                    total_call_not_received += call_not_received_count
                    total_do_not_call += do_not_call_count
                    total_good_lead += good_lead_count
                    total_re_visit += re_visit_count
                    total_poor_lead += poor_lead_count
                    total_may_be += may_be_count

                    # Calculate untouched leads for the current source
                    total_touched_leads_source = (
                        interested_count + dump_count + site_visit_count + permanent_dump_count +
                        booked_count + corporate_visit_count + block_enquiry_count +
                        call_not_received_count + do_not_call_count + good_lead_count +
                        re_visit_count + poor_lead_count + may_be_count
                    )
                    untouched_leads_source = count - total_touched_leads_source
                    data_dict['lead_yet_to_be_contacted'] = untouched_leads_source

                    medium_info['all_sources'].append(data_dict)

                # Calculate untouched leads for the current medium
                total_touched_leads = (
                    total_interested + total_dump + total_site_visit + total_permanent_dump +
                    total_booked + total_corporate_visit + total_block_enquiry +
                    total_call_not_received + total_do_not_call + total_good_lead +
                    total_re_visit + total_poor_lead + total_may_be
                )
                lead_yet_to_be_contacted = total_count - total_touched_leads

                # Add total count for the current medium to the dictionary
                medium_info.update({
                    'total_count': total_count,
                    'interested_leads': total_interested,
                    'dump_leads': total_dump,
                    'site_visit_leads': total_site_visit,
                    'permanent_dump_leads': total_permanent_dump,
                    'booked_leads': total_booked,
                    'corporate_visit_leads': total_corporate_visit,
                    'block_enquiry_leads': total_block_enquiry,
                    'call_not_received_leads': total_call_not_received,
                    'do_not_call_leads': total_do_not_call,
                    'good_leads': total_good_lead,
                    're_visit_leads': total_re_visit,
                    'poor_leads': total_poor_lead,
                    'may_be_leads': total_may_be,
                    'lead_yet_to_be_contacted': lead_yet_to_be_contacted,
                    'name': medium.medium.replace(' ', '_')
                })

                # Add the medium's information to the medium_counts list
                medium_counts.append(medium_info)

            # Return the counts
            return Response(medium_counts, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class MediumOfLeadCountAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        # Get start date and end date from query parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # Convert start date and end date strings to datetime objects if provided
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

        # Get all LeadSource objects
        lead_sources = MediumOfLead.objects.all()

        # Prepare a dictionary to store counts for each LeadSource
        source_counts = {}

        # Initialize total count
        total_count = 0

        # Loop through each LeadSource and count the associated FbLeads dynamically
        for source in lead_sources:
            # Apply date filtering if start_date and end_date are provided
            leads_query = FbLeads.objects.filter(lead_source=source)
            if start_date:
                leads_query = leads_query.filter(created_time__gte=start_date)
            if end_date:
                leads_query = leads_query.filter(created_time__lte=end_date)

            # Count the leads
            count = leads_query.count()
            total_count += count
            source_counts[source.lead_source] = count
            source_name = source.lead_source.replace(" ", "_")
            source_counts[source_name] = count

        # Add total count to the response
        source_counts['total_count'] = total_count

        # Return the counts
        return Response(source_counts)
    

class SourceCountFbLeadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the lead source and date range from query parameters
        lead_source_name = request.query_params.get('lead_source_name')
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        # Check if the lead source name is provided
        if lead_source_name:
            # Filter LeadSource object by lead source name
            lead_source = LeadSource.objects.filter(lead_source=lead_source_name).first()

            # If lead source exists, get counts for different fields
            if lead_source:
                fb_leads = FbLeads.objects.filter(lead_source=lead_source)

                # Apply date filtering if start_date and end_date are provided
                if start_date_str and end_date_str:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                    fb_leads = fb_leads.filter(created_at__range=[start_date, end_date])

                interested_count = fb_leads.filter(intersted=True).count()
                corporate_visit_count = fb_leads.filter(corporate_visit=True).count()
                dump_lead_count = fb_leads.filter(dump_lead=True).count()
                site_visit_count = fb_leads.filter(site_visit=True).count()
                lead_source_count = fb_leads.values('lead_source').distinct().count()

                # Prepare response data
                data = {
                    'interested_count': interested_count,
                    'corporate_visit_count': corporate_visit_count,
                    'dump_lead_count': dump_lead_count,
                    'site_visit_count': site_visit_count,
                    'lead_source_count': lead_source_count,
                }
                return Response(data)
            else:
                return Response({'error': 'Lead source not found'}, status=404)
        else:
            return Response({'error': 'Lead source name is required'}, status=400)