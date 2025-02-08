from rest_framework import fields, serializers
from social.models import *
from propertyStatus.serializer import ProjectSerializer, PhaseSerializer, ProjectTypeSerializer
from django.utils import timezone
from datetime import datetime, timedelta
from social.models import LeadEdit
from datetime import datetime, date


class FbLeadAdminSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()
    phase_name = serializers.SerializerMethodField()
    project_type_name = serializers.SerializerMethodField()
    preferred_location = serializers.SerializerMethodField()
    feedback = serializers.SerializerMethodField()
    budget = serializers.SerializerMethodField()
    lead_source = serializers.SerializerMethodField()
    by_medium = serializers.SerializerMethodField()
    class Meta :
        model = FbLeads
        fields = "__all__"
   
    def get_assigned_to_name(self, instance):
        assigned_to_id = instance.assigned_to_id
        if assigned_to_id:
            assigned_to_user = User.objects.filter(id=assigned_to_id).first()
            if assigned_to_user:
                return assigned_to_user.name
            else:
                print(f"No user found with ID: {assigned_to_id}")
        else:
            print("No assigned_to ID found")
        return None
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['agent_name'] = self.get_agent_name(instance)
        response['assigned_to_name'] = self.get_assigned_to_name(instance)
        response['get_site_visit_to_name'] = self.get_site_visit_to_name(instance)
        response['get_corporate_visit_to_name'] = self.get_corporate_visit_to_name(instance)
        
        return response

    def get_agent_name(self, instance):
        return instance.user.name if instance.user else None
    
    def get_site_visit_to_name(self, instance):
        return instance.site_visit_to.name if instance.site_visit_to else None

    def get_corporate_visit_to_name(self, instance):
        return instance.corporate_visit_to.name if instance.corporate_visit_to else None

    def get_project_name(self, instance):
        names = []
        if instance.project_name:
            if type(instance.project_name)==list:
                for i in instance.project_name:
                    names.append(i.project_name)
            elif type(instance.project_name)==str:
                names.append(instance.project_name.project_name)
        return names

    def get_phase_name(self, instance):
        #return instance.phase_name.phase_name if instance.phase_name else None
        return None

    def get_project_type_name(self, instance):
        names = []
        if instance.project_type_name:
            if type(instance.project_type_name)==list:
                for i in instance.project_type_name:
                    names.append(i.property_type)
            elif type(instance.project_name)==str:
                names.append(instance.project_type_name.property_type)
        return names
        return instance.project_type_name.property_type if instance.project_type_name else None

    def get_preferred_location(self, instance):
        return instance.preferred_location.preferred_location if instance.preferred_location else None

    def get_feedback(self, instance):
            # First, attempt to get the latest LeadEdit feedback if it exists
        lead_edit_instance = LeadEdit.objects.filter(fb_leads=instance).exclude(feedback__isnull=True).exclude(feedback__exact='').order_by('-created_at').first()
        if lead_edit_instance:
            return lead_edit_instance.status_of_lead.status_lead if lead_edit_instance.status_of_lead else None
        
        # If no valid LeadEdit feedback exists, fall back to the FbLeads feedback
        return instance.feedback if instance.feedback else None
    def get_budget(self, instance):
        return instance.budget.max_budget if instance.budget else None

    def get_lead_source(self, instance):
        return instance.lead_source.lead_source if instance.lead_source else None

    def get_by_medium(self, instance):
        return instance.by_medium.medium if instance.by_medium else None

    def get_status(self, instance):
        now = timezone.now()
        last_lead_edit = instance.leadedit_set.last()  # Get the last lead edit related to this fb lead
        if last_lead_edit:
            last_update_time = last_lead_edit.created_at
            # Check if the last update was more than 2 minutes ago
            if now - last_update_time > timedelta(hours=48):
                return 'Delayed'
        else:
            # No lead edit record found, check if the fb_lead was created more than 2 minutes ago
            if now - instance.created_time > timedelta(hours=48):
                return 'Delayed'
        return 'Not Delayed'  # Return 'Not Delayed' if lead is updated within last 2 minutes



    

class LeadEditAdminSerializer(serializers.ModelSerializer):
    mode_name = serializers.CharField(source='mode.mode_lead', read_only=True)
    status_of_lead_name = serializers.CharField(source='status_of_lead.status_lead', read_only=True)
    reason_for_dump = serializers.CharField(source='reason_for_dump.reason_of_dump', read_only=True)
    next_schedule_mode_name = serializers.CharField(source='next_schedule_mode.mode_lead', read_only=True)
    reason_for_site_visit_name = serializers.CharField(source='reason_for_site_visit.reason_of_site_visit',read_only=True)
    prject_name = serializers.CharField(source='project.project_name',read_only=True)
    class Meta :
        model = LeadEdit
        fields = '__all__'
    # def to_representation(self, instance):
    #     response = super().to_representation(instance)
    #     response['agent_name'] = self.get_agent_name(instance)
    #     # response['mode'] = ModeLeadSerializer(instance.mode).data
    #     # response['status_of_lead'] = StatusLeadSerializer(instance.status_of_lead).data
    #     # response['feedback'] = FeedBackSerializer(instance.feedback).data
    #     # response['next_schedule_mode'] = ModeLeadSerializer(instance.next_schedule_mode).data

    # def get_agent_name(self, instance):
    #     return instance.user.name if instance.user else None



class NextSheduleTrackSerializer(serializers.ModelSerializer):
    #agent_name = serializers.SerializerMethodField()
    shedule_count = serializers.SerializerMethodField()
    delay = serializers.SerializerMethodField()
    class Meta:
        model = LeadEdit
        fields = ['id','next_schedule_date','shedule_count','user','created_at','delay']
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['agent_name'] = self.get_agent_name(instance)
        return response

    def get_agent_name(self, instance):
        return instance.user.name if instance.user else None
    def get_shedule_count(self, obj):
        # Get the count of messages for the user associated with the message
        user = obj.user
        if user:
            return LeadEdit.objects.filter(user=user).count()
        return 0
    def get_delay(self, obj):
            # Specific reference date to ignore dates older than this
        ignore_before_date = datetime.strptime("22/5/2024", "%d/%m/%Y").date()
        if obj.next_schedule_date:
            # If next_schedule_date is older than ignore_before_date, ignore it
            if obj.next_schedule_date > ignore_before_date:
                return 0
            # Use today's date as the reference date
            reference_date = date.today()
            # Calculate the delay between the reference date and the next schedule date
            delay = (reference_date - obj.next_schedule_date).days
            return delay
        return 0
    

class NextBookingSerializer(serializers.ModelSerializer):
    #agent_name = serializers.SerializerMethodField()
    shedule_count = serializers.SerializerMethodField()
    class Meta:
        model = LeadEdit
        fields = ['id','date_of_booking','shedule_count','user','created_at']
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['agent_name'] = self.get_agent_name(instance)
        return response

    def get_agent_name(self, instance):
        return instance.user.name if instance.user else None
    def get_shedule_count(self, obj):
        # Get the count of messages for the user associated with the message
        user = obj.user
        if user:
            return LeadEdit.objects.filter(user=user,date_of_booking__isnull=False).count()
        return 0