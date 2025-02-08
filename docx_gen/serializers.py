from rest_framework import serializers

from bookingForm.models import CoApplicantForm, Booking, AllDocument, PersonalDeatils
from propertyStatus.models import UnitNo


class DocxCoApplicantFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoApplicantForm
        fields = '__all__'


class DocxBookingSerializers(serializers.ModelSerializer):
    agent_name = serializers.CharField(source='user.name', read_only=True)
    project_names = serializers.CharField(source='project_name.project_name', read_only=True)
    type_names = serializers.CharField(source='type_name.property_type', read_only=True)
    unit_nos = serializers.CharField(source='unit_no.unit_no', read_only=True)
    tax_types = serializers.CharField(source='tax_type.tax_type', read_only=True)
    personal_details_id = serializers.SerializerMethodField()
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

    def get_co_applicants(self, instance):
        co_applicants_data = []
        personal_details = instance.personaldeatils_set.all()
        for personal_detail in personal_details:
            co_applicants = personal_detail.coapplicantform_set.all()
            co_applicants_data.extend(
                DocxCoApplicantFormSerializer(co_applicant).data for co_applicant in co_applicants)
        return co_applicants_data

    def to_representation(self, instance):
        if instance.govt_extra_charges == "":
            instance.govt_extra_charges = 0
        if instance.interst_rate == "":
            instance.interst_rate = 0
        if instance.Annual_income == "":
            instance.Annual_income = 0
        if instance.booking_amount == "":
            instance.booking_amount = 0
        if instance.unit_cost == "":
            instance.unit_cost = 0
        response = super().to_representation(instance)
        response['personal_details_id'] = self.get_personal_details_id(instance)
        response['get_co_applicants'] = self.get_co_applicants(instance)
        return response


class DocxAllDocumentserializers(serializers.ModelSerializer):
    class Meta:
        model = AllDocument
        fields = '__all__'


class DocxUnitNoSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='projects.project_name', read_only=True)

    class Meta:
        model = UnitNo
        fields = '__all__'


class DocxBookingPersonalDeatils(serializers.ModelSerializer):
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
        response['booking'] = DocxBookingSerializers(instance.booking).data
        response['unit_no'] = DocxUnitNoSerializer(instance.booking.unit_no).data
        response['document_name'] = DocxAllDocumentserializers(instance.document_name).data
        response['document_url'] = self.get_document_url(instance)  # Corrected line
        return response


class DocxCoApplicantFormSerializers(serializers.ModelSerializer):
    class Meta:
        model = CoApplicantForm
        fields = '__all__'

    def get_user(self, instance):
        return instance.user.name if instance.user else None

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['user'] = self.get_user(instance)
        response['personal_deatils'] = DocxBookingPersonalDeatils(instance.personal_deatils).data
        return response
