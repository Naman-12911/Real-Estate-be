import django_filters
from .models import SiteWorkers
from propertyStatus.models import Project,UnitNo

class SiteWorkersFilters(django_filters.FilterSet):
    project_name = django_filters.NumberFilter(field_name='project_name')
    unit_no = django_filters.NumberFilter(field_name='unit_no__unit_no', lookup_expr='exact')
    order_by = django_filters.OrderingFilter(
        fields=(
            ('worker_update_date', 'worker_update_date'),
        ),
    )

    class Meta:
        model = SiteWorkers
        fields =[ 'project_name', 'unit_no','order_by']
    

