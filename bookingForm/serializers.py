from rest_framework import serializers
from account.models import User
from .models import Booking,PersonalDeatils,CoApplicantForm,AllDocument,CancelBooking,CancelRefund
from django.contrib.sites.shortcuts import get_current_site
from propertyStatus.serializer import UnitNoSerializer, ProjectSerializer
from propertyStatus.models import UnitNo

class CoApplicantFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoApplicantForm
        fields = '__all__'

class BookingSerializers(serializers.ModelSerializer):
    agent_name = serializers.CharField(source='user.name', read_only=True)
    project_names = serializers.CharField(source='project_name.project_name', read_only=True)
    type_names = serializers.CharField(source='type_name.property_type', read_only=True)
    unit_nos = serializers.CharField(source='unit_no.unit_no', read_only=True)
    tax_types = serializers.CharField(source='tax_type.tax_type', read_only=True)
    personal_details_id = serializers.SerializerMethodField()
    personal_details = serializers.SerializerMethodField()
    # co_applicants_ids = serializers.SerializerMethodField()  # Use plural to indicate multiple co-applicants
    co_applicants = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = '__all__'

    def get_user(self, instance):
        return instance.user.name if instance.user else None

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['user'] = self.get_user(instance)
        return response

    def get_personal_details_id(self, instance):
        return instance.personaldeatils_set.first().id if instance.personaldeatils_set.exists() else None
    
    def get_personal_details(self, instance):
        return instance.personaldeatils_set.first().id if instance.personaldeatils_set.exists() else None

    # def get_co_applicants_ids(self, instance):
    #     co_applicants_ids = []
    #     personal_details = instance.personaldeatils_set.all()
    #     for personal_detail in personal_details:
    #         co_applicants_ids.extend(list(personal_detail.coapplicantform_set.values_list('id', flat=True)))
    #     return co_applicants_ids
    def get_co_applicants(self, instance):
        co_applicants_data = []
        personal_details = instance.personaldeatils_set.all()
        for personal_detail in personal_details:
            co_applicants = personal_detail.coapplicantform_set.all()
            co_applicants_data.extend(CoApplicantFormSerializer(co_applicant).data for co_applicant in co_applicants)
        return co_applicants_data

    def to_representation(self, instance):
        if instance.govt_extra_charges=="":
            instance.govt_extra_charges = 0
        if instance.interst_rate=="":
            instance.interst_rate = 0
        if instance.Annual_income=="":
            instance.Annual_income = 0
        if instance.booking_amount=="":
            instance.booking_amount = 0
        if instance.unit_cost=="":
            instance.unit_cost = 0
        response = super().to_representation(instance)
        response['personal_details_id'] = self.get_personal_details_id(instance)
        response['get_co_applicants'] = self.get_co_applicants(instance)
        return response

class AllDocumentserializers(serializers.ModelSerializer):
    class Meta:
        model = AllDocument
        fields = '__all__'


class BookingPersonalDeatils(serializers.ModelSerializer):
    document_url = serializers.SerializerMethodField()
    class Meta:
        model = PersonalDeatils
        fields = '__all__'

    def get_user(self, instance):
        return instance.user.name if instance.user else None

    def get_document_url(self, instance):
        request = self.context.get('request')
        if request and instance.document:
            return request.build_absolute_uri(instance.document.url)
        return None
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['user'] = self.get_user(instance)
        response['booking'] = BookingSerializers(instance.booking).data
        response['document_name'] = AllDocumentserializers(instance.document_name).data
        response['document_url'] = self.get_document_url(instance)  # Corrected line
        return response  

class CoApplicantFormSerializers(serializers.ModelSerializer):
    class Meta:
        model = CoApplicantForm
        fields = '__all__'

    def get_user(self, instance):
        return instance.user.name if instance.user else None
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['user'] = self.get_user(instance)
        response['personal_deatils'] = BookingPersonalDeatils(instance.personal_deatils).data
        return response

class CancelRefundSerializers(serializers.ModelSerializer):
    class Meta:
        model = CancelRefund
        fields = '__all__'

class CancelBookingSerializers(serializers.ModelSerializer):
    refund = serializers.SerializerMethodField()
    # booking = serializers.SerializerMethodField()
    personal_details = serializers.SerializerMethodField()
    unit_no = serializers.SerializerMethodField()

    class Meta:
        model = CancelBooking
        fields = '__all__'

    def get_refund(self, instance):
        return CancelRefundSerializers(CancelRefund.objects.filter(cancelbooking=instance, deleted=False), many=True).data
    
    def get_personal_details(self, instance):
        return BookingPersonalDeatils(PersonalDeatils.objects.get(booking=instance.booking)).data
    
    def get_unit_no(self, instance):
        if instance.unit_no:
            return UnitNoSerializer(UnitNo.objects.get(pk=instance.unit_no.pk)).data
        else:
            return []