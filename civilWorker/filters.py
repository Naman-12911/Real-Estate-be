
from django_filters import rest_framework as filters
from .models import *
import django_filters
from django.db.models import F

class ConstructorProfileFilter(django_filters.FilterSet):
    bank_name = django_filters.CharFilter(field_name='bank_name', lookup_expr='icontains')
    gst = django_filters.CharFilter(field_name='gst', lookup_expr='icontains')
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    hsncode = django_filters.CharFilter(field_name='hsncode', lookup_expr='exact')
    unit = django_filters.CharFilter(method='filter_by_unit_number')
    created_at__gte = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at__lte = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    class Meta:
        model = ConstructorProfile
        fields = ['bank_name','gst','name','hsncode','created_at__gte','created_at__lte','unit']
    def filter_by_unit_number(self, queryset, name, value):
        return queryset.filter(unit__unit_no__iexact=value)

class CivilStatgesFilter(django_filters.FilterSet):
    unit = django_filters.NumberFilter(field_name='unit__unit_no',lookup_expr='exact')
    updated_at__gte = django_filters.DateFilter(field_name='updated_at', lookup_expr='gte')
    updated_at__lte = django_filters.DateFilter(field_name='updated_at', lookup_expr='lte')
    contractor_id = django_filters.CharFilter(field_name="constructor_profile__id",lookup_expr='exact')
    order_by = filters.OrderingFilter(
        fields=(
            ('updated_at', 'updated_at'),
        ),
        field_labels={
            'updated_at': 'Updated At',
        },
        method='filter_order_by'
    )

    def filter_order_by(self, queryset, name, value):
        if value == ['updated_at'] or value == ['-updated_at']:
            return queryset.order_by(F('updated_at').desc() if value == ['-updated_at'] else F('updated_at').asc())
        return queryset
    class Meta:
        model = CivilStatges
        fields = ['updated_at__gte','updated_at__lte','unit','order_by','contractor_id']


class BillsFilter(django_filters.FilterSet):
    unit = django_filters.NumberFilter(field_name='unit__id',lookup_expr='exact')
    class Meta:
        model = Bills
        fields = ['unit',]


class MiscellaneousFilter(django_filters.FilterSet):
    unit = django_filters.NumberFilter(field_name='unit__id',lookup_expr='exact')
    class Meta:
        model = Miscellaneous
        fields = ['unit',]


class RemarksFilter(django_filters.FilterSet):
    unit = django_filters.NumberFilter(field_name='unit__id',lookup_expr='exact')
    class Meta:
        model = Remarks
        fields = ['unit',]

class ExcelFilesDownloadFilter(django_filters.FilterSet):
    constructor_profile = django_filters.NumberFilter(field_name='constructor_profile__id',lookup_expr='exact')
    bill_no = django_filters.NumberFilter(field_name='bill_no',lookup_expr='exact')
    created_at_gte = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at_lte = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    class Meta:
        model = ExcelFilesCivilStages
        fields = ['constructor_profile','created_at_gte','created_at_lte','bill_no']
    


class InvoiceCivilStagesFilter(django_filters.FilterSet):
    constructor_profile = django_filters.NumberFilter(field_name='constructor_profile__id',lookup_expr='exact')
    bill_no = django_filters.NumberFilter(field_name='bill_no',lookup_expr='exact')
    created_at_gte = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at_lte = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    class Meta:
        model = InvoiceCivilStages
        fields = ['constructor_profile','created_at_gte','created_at_lte','bill_no']