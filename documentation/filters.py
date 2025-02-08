import django_filters
from .models import Receipt

class ReceiptFilters(django_filters.FilterSet):
    unit_number = django_filters.CharFilter(field_name='unit_number__unit_no', lookup_expr='exact')

    class Meta:
        model = Receipt
        fields = ['unit_number']
    

class ReceiptCancelFilters(django_filters.FilterSet):
    personal_details = django_filters.CharFilter(field_name='payment_stage__personal_deatils__id', lookup_expr='exact')

    class Meta:
        model = Receipt
        fields = ['personal_details']