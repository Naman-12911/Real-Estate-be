import django_filters
from .models import Phase,UnitNo

class PhaseFilter(django_filters.FilterSet):
    project_name = django_filters.CharFilter(field_name='unit__projects__project_name', lookup_expr='icontains')
    phase_name = django_filters.CharFilter(field_name='phase_name', lookup_expr='icontains')
    available = django_filters.BooleanFilter(field_name='unit__available',lookup_expr='exact')
    booked = django_filters.BooleanFilter(field_name='unit__booked',lookup_expr='exact')
    hold = django_filters.BooleanFilter(field_name='unit__hold',lookup_expr='exact')

    class Meta:
        model = Phase
        fields = ['project_name', 'phase_name', 'available', 'booked', 'hold']


class unitFilter(django_filters.FilterSet):
    available = django_filters.BooleanFilter(field_name='available')
    class Meta:
        model = UnitNo
        fields = ['available']


class PhaseFilter(django_filters.FilterSet):
    project_id = django_filters.NumberFilter(field_name='unit__projects__id')
    project_name = django_filters.CharFilter(field_name='unit__projects__project_name', lookup_expr='icontains')
    available = django_filters.BooleanFilter(field_name='unit__available',lookup_expr='exact')
    booked = django_filters.BooleanFilter(field_name='unit__booked',lookup_expr='exact')
    hold = django_filters.BooleanFilter(field_name='unit__hold',lookup_expr='exact')

    class Meta:
        model = Phase
        fields = ['project_id', 'project_name','available', 'booked', 'hold']