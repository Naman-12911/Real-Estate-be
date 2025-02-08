import django_filters
from bookingForm.models import PersonalDeatils

class ProfileSearchFilters(django_filters.FilterSet):
    applicant_name = django_filters.CharFilter(field_name='applicant_name', lookup_expr='exact')
    unit_no = django_filters.CharFilter(field_name='booking__unit_no__unit_no', lookup_expr='exact')
    project = django_filters.CharFilter(field_name='booking__project_name__project_name', lookup_expr='icontains')

    class Meta:
        model = PersonalDeatils
        fields = ['applicant_name', 'unit_no', 'project']