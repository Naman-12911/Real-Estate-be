import django_filters
from .models import WhatsAppMessage

class WhatsAppMessageFilter(django_filters.FilterSet):
    # Example filter for the city field
    project_name = django_filters.CharFilter(
        field_name='project_name__project_name',
        lookup_expr='exact'  # This is optional, used to perform case-insensitive partial match
    )

    property_type = django_filters.CharFilter(
        field_name='project_type__property_type',
        lookup_expr='exact'  # This is optional, used to perform case-insensitive partial match
    )

    class Meta:
        model = WhatsAppMessage
        fields = ['project_name','property_type']




