from rest_framework import  serializers
from .models import *
from django.utils import timezone
from datetime import timedelta

class FbLeadSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    project_name = serializers.StringRelatedField(many=True)
    phase_name = serializers.SerializerMethodField()
    project_type_name = serializers.StringRelatedField(many=True)
    preferred_location = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    budget = serializers.SerializerMethodField()
    lead_source = serializers.SerializerMethodField()
    by_medium = serializers.SerializerMethodField()
    status_of_lead = serializers.SerializerMethodField()
    visit_date =  serializers.SerializerMethodField()
    status_of_lead_warm_hot_cold =  serializers.SerializerMethodField()
    visit_number =  serializers.SerializerMethodField()

    class Meta:
        model = FbLeads
        fields = "__all__"

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['agent_name'] = self.get_agent_name(instance)
        response['assigned_to_name'] = self.get_assigned_to_name(instance)
        response['get_site_visit_to_name'] = self.get_site_visit_to_name(instance)
        response['get_corporate_visit_to_name'] = self.get_corporate_visit_to_name(instance)
        return response

    def get_agent_name(self, instance):
        return instance.user.name if instance.user else None

    def get_assigned_to_name(self, instance):
        return instance.assigned_to.name if instance.assigned_to else None

    def get_phase_name(self, instance):
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

    def get_preferred_location(self, instance):
        return instance.preferred_location.preferred_location if instance.preferred_location else None


    def get_budget(self, instance):
        return instance.budget.max_budget if instance.budget else None

    def get_lead_source(self, instance):
        return instance.lead_source.lead_source if instance.lead_source else None

    def get_by_medium(self, instance):
        return instance.by_medium.medium if instance.by_medium else None

    def get_site_visit_to_name(self, instance):
        return instance.site_visit_to.name if instance.site_visit_to else None

    def get_corporate_visit_to_name(self, instance):
        return instance.corporate_visit_to.name if instance.corporate_visit_to else None

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
        return 'Not Delayed' 

    # feedback and source of lead to fetch using reverse forigen key concept
    def get_status_of_lead(self, instance):
        lead_edit_instance = LeadEdit.objects.filter(fb_leads=instance).order_by('-created_at').first()
        if lead_edit_instance and lead_edit_instance.status_of_lead:
            return lead_edit_instance.status_of_lead.status_lead
        return None

        
    def get_description(self, instance):
        lead_edit_instance = LeadEdit.objects.filter(fb_leads=instance).order_by('-created_at').first()
        if lead_edit_instance:
            return getattr(lead_edit_instance, 'description', None) if getattr(lead_edit_instance, 'description', None) else None
        return getattr(instance, 'description', None) if getattr(instance, 'description', None) else None
    
    def get_visit_date(self, instance):
        lead_edits = LeadEdit.objects.filter(fb_leads=instance).order_by('-created_at')
        
        # Iterate through the list to find the visit_number
        for lead_edit_instance in lead_edits:
            visit_date = getattr(lead_edit_instance, 'visit_date', None)
            if visit_date is not None:
                return visit_date
        
        # If no visit_number is found in LeadEdit instances, return the visit_number from the FbLeads instance
        return getattr(instance, 'visit_date', None)

    def get_visit_number(self, instance):
    # Retrieve the list of LeadEdit instances ordered by creation date, most recent first
        lead_edits = LeadEdit.objects.filter(fb_leads=instance).order_by('-created_at')
        
        # Iterate through the list to find the visit_number
        for lead_edit_instance in lead_edits:
            visit_number = getattr(lead_edit_instance, 'visit_number', None)
            if visit_number is not None:
                return visit_number
        
        # If no visit_number is found in LeadEdit instances, return the visit_number from the FbLeads instance
        return getattr(instance, 'visit_number', None) 

    def get_status_of_lead_warm_hot_cold(self, instance):
        lead_edit_instance = LeadEdit.objects.filter(fb_leads=instance).order_by('-created_at').first()
        if lead_edit_instance:
            return getattr(lead_edit_instance, 'status_of_lead_warm_hot_cold', None) if getattr(lead_edit_instance, 'status_of_lead_warm_hot_cold', None) else None
        return getattr(instance, 'status_of_lead_warm_hot_cold', None) if getattr(instance, 'status_of_lead_warm_hot_cold', None) else None


    
    
class FbLeadPostSerializer(serializers.ModelSerializer):
    class Meta :
        model = FbLeads
        fields = "__all__"
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['agent_name'] = self.get_agent_name(instance)
        response['assigned_to_name'] = self.get_assigned_to_name(instance)
        response['site_visit_to_name'] = self.get_site_visit_to_name(instance)
        response['corporate_visit_to_name'] = self.get_corporate_visit_to_name(instance)
        return response
    def get_assigned_to_name(self, instance):
        return instance.assigned_to.name if instance.assigned_to else None
    
    def get_site_visit_to_name(self, instance):
        return instance.site_visit_to.name if instance.site_visit_to else None
    
    def get_corporate_visit_to_name(self, instance):
        return instance.corporate_visit_to.name if instance.corporate_visit_to else None
    
    def get_agent_name(self, instance):
        return instance.user.name if instance.user else None


class LeadSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadSource
        fields = "__all__"

class MediumOfLeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediumOfLead
        fields = "__all__"

class preferredLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = preferredLocation
        fields = "__all__"

class ReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reason
        fields = "__all__"

class BudgetSerializer(serializers.ModelSerializer):
    class Meta :
        model = Budget
        fields = '__all__' 

class ModeLeadSerializer(serializers.ModelSerializer):
    class Meta :
        model = ModeLead
        fields = '__all__' 
    
class StatusLeadSerializer(serializers.ModelSerializer):
    class Meta :
        model = StatusLead
        fields = '__all__' 

class ReasonSiteVisitSerializer(serializers.ModelSerializer):
    class Meta :
        model = ReasonSiteVisit
        fields = '__all__' 
    

class LeadEditSerializer(serializers.ModelSerializer):
    mode_name = serializers.CharField(source='mode.mode_lead', read_only=True)
    status_of_lead_name = serializers.CharField(source='status_of_lead.status_lead', read_only=True)
    reason_for_dump = serializers.CharField(source='reason_for_dump.reason_of_dump', read_only=True)
    next_schedule_mode_name = serializers.CharField(source='next_schedule_mode.mode_lead', read_only=True)
    reason_for_site_visit_name = serializers.CharField(source='reason_for_site_visit.reason_of_site_visit',read_only=True)
    prject_name = serializers.CharField(source='project.project_name',read_only=True,allow_null=True, required=False)
    site_visit_to = serializers.CharField(source='fb_leads.site_visit_to',read_only=True)
    corporate_visit_to = serializers.CharField(source='fb_leads.corporate_visit_to',read_only=True)
    visited_by = serializers.PrimaryKeyRelatedField(read_only=True) 
    class Meta :
        model = LeadEdit
        fields = '__all__'
    # def create(self, validated_data):
    #     # Extract related data from validated_data
    #     fb_leads_data = validated_data.pop('fb_leads')
    #     user_data = validated_data.pop('user')

    #     # Retrieve FbLeads instance and user instance
    #     fb_leads_instance = FbLeads.objects.get(id=fb_leads_data['id'])
    #     user_instance = User.objects.get(id=user_data['id'])

    #     # Create and return LeadEdit instance
    #     lead_edit_instance = LeadEdit.objects.create(
    #         fb_leads=fb_leads_instance,
    #         user=user_instance,
    #         **validated_data
    #     )
    #     return lead_edit_instance

class NotificationStoreSerializer(serializers.ModelSerializer):
    
    class Meta :
        model = NotificationStore
        fields = '__all__' 

class FBleads99(serializers.ModelSerializer):
    class Meta:
        models = FbLeads
        fields = ['full_name','Type','phone_number','PhoneVerificationStatus','email','Query','CalledOn','Time','Duration','CallStatus','url','receiveddate',
            'interestedin','responetype','username','EmailVerificationStatus','Questionnaire','productcode','producttype',
            'IntentVerificationStatus','LeadScore','FollowupCurrentStatus','ProdType','city','project','rescom','Bhk','PropertySnapshot',
            'ParentProductDetails','SetIsParentProductTypeResponse','CompactLabel','Duplicate','lead_source','by_medium']


class FBleadsHomeonline(serializers.ModelSerializer):
    class Meta:
        models = FbLeads
        fields = ['full_name','phone_number','email','property_title','purpose_of_property','property','locality','details',
            'responetype','receiveddate','lead_source','by_medium']

class FBleadsHousing(serializers.ModelSerializer):
    class Meta:
        models = FbLeads
        fields = ["service_type","property_type",'receiveddate','full_name','phone_number','email',"seller_id","seller_name","configuration",
            "price","address",'lead_source','by_medium']
