from rest_framework import serializers
from account.models import User
from .models import *
from propertyStatus.serializer import UnitNoSerializer
from bookingForm.models import Booking


class SiteWorkersSerializer(serializers.ModelSerializer):
    unit_number = serializers.CharField(source='unit_no.unit_no', read_only=True)
    project_name = serializers.CharField(source='projects.project_name', read_only=True)
    final_amount = serializers.SerializerMethodField()
    class Meta:
        model = SiteWorkers
        fields = '__all__'
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['unit_no'] = UnitNoSerializer(instance.unit_no).data
        response['final_amount'] = self.get_final_amount(instance)
        
        return response
    
    def get_final_amount(self, instance):
        total_charges = 0

        # Get the related Booking instance for the current SiteWorkers instance
        booking_instance = Booking.objects.filter(unit_no=instance.unit_no).first()
        if booking_instance:
            if booking_instance.booking_amount=="":
                booking_instance.booking_amount = 0
            total_charges = (
                int(booking_instance.maintainance_charges_2_year) +
                int(booking_instance.external_electrical_charges) +
                booking_instance.water_connection_charges +
                booking_instance.corner_plot_charges +
                booking_instance.park_face_charges +
                booking_instance.registry_extra_charges +
                booking_instance.mutation_charges +
                booking_instance.socity_maintaince_charges +
                booking_instance.other_charges +
                booking_instance.wide_road_facing_charges +
                booking_instance.booking_amount
            )

        unit_cost = instance.unit_no.unit_cost
        if unit_cost:
            total_amount = total_charges + float(unit_cost)
        else:
            total_amount = total_charges

        return total_amount
    
    def filter_queryset(self, queryset):
        final_amount_min = self.context['request'].query_params.get('final_amount_min')
        final_amount_max = self.context['request'].query_params.get('final_amount_max')

        if final_amount_min is not None:
            queryset = queryset.filter(final_amount__gte=float(final_amount_min))

        if final_amount_max is not None:
            queryset = queryset.filter(final_amount__lte=float(final_amount_max))

        return queryset


class MonthlyExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyExpense
        fields = '__all__'



