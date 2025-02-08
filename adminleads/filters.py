import django_filters
from social.models import FbLeads,LeadEdit
from django.db.models import OuterRef, Subquery

class FbLeadsCorporateFilter(django_filters.FilterSet):
    # Example filter for the city field
    city = django_filters.CharFilter(lookup_expr='icontains')
    ad_name = django_filters.CharFilter(lookup_expr='icontains')
    adset_name = django_filters.CharFilter(lookup_expr='icontains')
    campaign_name = django_filters.CharFilter(lookup_expr='icontains')
    custom_disclaimer_responses = django_filters.CharFilter(lookup_expr='icontains')
    full_name = django_filters.CharFilter(lookup_expr='icontains')
    form_name = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    phone_number = django_filters.CharFilter(lookup_expr='icontains')
    page_name = django_filters.CharFilter(lookup_expr='icontains')
    form = django_filters.CharFilter(lookup_expr='icontains')
    job_title = django_filters.CharFilter(lookup_expr='icontains')
    platform = django_filters.CharFilter(lookup_expr='icontains')
    partner_name = django_filters.CharFilter(lookup_expr='icontains')
    select_available_price = django_filters.CharFilter(lookup_expr='icontains')
    alternative_number = django_filters.CharFilter(lookup_expr='icontains')
    created_at__gte = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at__lte = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    assigned_to_name = django_filters.CharFilter(field_name='assigned_to__name', lookup_expr='icontains')
    project_name = django_filters.CharFilter(field_name='project_name__project_name',lookup_expr='icontains')
    # add lead edit feilds for reverse forigen key concept
   
    expected_booking = django_filters.BooleanFilter(field_name='expected_booking')
    status_of_lead_warm_hot_cold = django_filters.CharFilter(method='filter_by_status_of_lead_warm_hot_cold')
    get_site_visit_to_name = django_filters.CharFilter(field_name='site_visit_to__name', lookup_expr='exact')
    feedback = django_filters.CharFilter(field_name='feedback', lookup_expr='icontains')
    project_type_name = django_filters.CharFilter(field_name='project_type_name__property_type',lookup_expr='exact')
    lead_source = django_filters.CharFilter(field_name='lead_source__medium_of_lead',lookup_expr='exact')

    class Meta:
        model = FbLeads
        fields = ['city', 'ad_name', 'adset_name', 'campaign_name', 'custom_disclaimer_responses', 
                  'full_name', 'form_name', 'email', 'phone_number', 'page_name', 'form', 
                  'job_title', 'platform', 'partner_name', 'select_available_price', 'alternative_number',
                  'created_at__gte', 'created_at__lte', 'dump_lead','assigned_to_name','expected_booking','status_of_lead_warm_hot_cold','get_site_visit_to_name','feedback','project_type_name',
                  'lead_source']

    def filter_by_status_of_lead_warm_hot_cold(self, queryset, name, value):
        # Subquery to get the latest LeadEdit for each FbLeads
        latest_lead_edit_subquery = LeadEdit.objects.filter(
            fb_leads=OuterRef('pk')
        ).order_by('-created_at').values('status_of_lead_warm_hot_cold')[:1]

        # Filter LeadEdit by status_of_lead_warm_hot_cold value
        lead_edits = LeadEdit.objects.filter(
            pk__in=Subquery(latest_lead_edit_subquery),
            status_of_lead_warm_hot_cold=value
        )

        # Get FbLeads IDs from filtered LeadEdit
        fb_lead_ids = lead_edits.values_list('fb_leads_id', flat=True)

        # Filter the queryset by FbLeads IDs
        return queryset.filter(id__in=fb_lead_ids)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.filters['status_of_lead'].field.queryset = LeadEdit.objects.all()
        self.filters['status_of_lead_warm_hot_cold'].field.queryset = LeadEdit.objects.all()




class SalesPersonCountsLeadStatsFilter(django_filters.FilterSet):
    created_at__gte = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at__lte = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = FbLeads
        fields = ['created_at__gte', 'created_at__lte']


