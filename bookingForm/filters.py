import django_filters
from .models import PersonalDeatils

class PersonalDeatilsFilters(django_filters.FilterSet):
    applicant_name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = PersonalDeatils
        fields = ['applicant_name',]
    

