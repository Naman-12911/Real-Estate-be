from rest_framework import  serializers
from social.models import *
from django.utils import timezone
from datetime import timedelta
from civilWorker.models import CivilStatges


class FbLeadViewLeadsExcelFileSerializer(serializers.ModelSerializer):
    project_name = serializers.StringRelatedField(many=True)  ####
    project_type_name = serializers.StringRelatedField(many=True)  ###
    lead_source = serializers.SerializerMethodField()
    lead_status = serializers.SerializerMethodField()
    HOT_WARM_COLD =  serializers.SerializerMethodField()
    visited_by =  serializers.SerializerMethodField()

    class Meta:
        model = FbLeads
        fields = ['project_name','HOT_WARM_COLD','lead_status','lead_source','project_type_name']

    def to_representation(self, instance):
        # response = super().to_representation(instance)
        response = {}
        response['Project Name'] = self.get_project_names(instance)
        # response['Lead Source'] = self.get_lead_source(instance)
        response['Enquiry Date'] = instance.created_at
        response['Last Updated Date And Time'] = instance.updated_at
        response['Customer Name'] = instance.full_name
        response['Phone Number'] = instance.phone_number
        response['Current Assigend Agent'] = self.get_assigned_to_name(instance)
        response['Executive Name'] = self.get_agent_name(instance)
        response['Project Type'] = self.get_project_type_names(instance)
        response['Lead Source'] = instance.lead_source
        response['Lead Status'] = self.get_lead_status(instance)
        response['HOT/WARM/COLD'] = self.get_HOT_WARM_COLD(instance)
        response['Feedback'] = instance.feedback 
        response['Expected Booking'] = "Yes" if instance.expected_booking else "No"
        response['Admin Status'] = instance.status_acc_admin
        response['Admin Comment'] = instance.feedback_acc_admin 
       
        
        return response

    def get_agent_name(self, instance):
        return instance.user.name if instance.user else None

    def get_assigned_to_name(self, instance):
        return instance.assigned_to.name if instance.assigned_to else None

    def get_project_type_names(self, instance):
        names = []
        if instance.project_type_name.exists():
            for project_type in instance.project_type_name.all():
                names.append(project_type.property_type)
        return names

    def get_project_names(self, instance):
        names = []
        if instance.project_name.exists():
            for project in instance.project_name.all():
                names.append(project.project_name)
        return names
   
    def get_lead_source(self, instance):
        return instance.lead_source.lead_source if instance.lead_source else None

    def get_site_visit_to_name(self, instance):
        return instance.site_visit_to.name if instance.site_visit_to else None
    # feedback and source of lead to fetch using reverse forigen key concept
    def get_lead_status(self, instance):
        lead_edit_instance = LeadEdit.objects.filter(fb_leads=instance).order_by('-created_at').first()
        if lead_edit_instance and lead_edit_instance.status_of_lead:
            return lead_edit_instance.status_of_lead.status_lead
        return None
    

    def get_HOT_WARM_COLD(self, instance):
        lead_edit_instance = LeadEdit.objects.filter(fb_leads=instance).order_by('-created_at').first()
        if lead_edit_instance:
            return getattr(lead_edit_instance, 'status_of_lead_warm_hot_cold', None) if getattr(lead_edit_instance, 'status_of_lead_warm_hot_cold', None) else None
        return getattr(instance, 'status_of_lead_warm_hot_cold', None) if getattr(instance, 'status_of_lead_warm_hot_cold', None) else None



class FbLeadDumpLeadsExcelFileSerializer(serializers.ModelSerializer):
    project_name = serializers.StringRelatedField(many=True)  ####
    project_type_name = serializers.StringRelatedField(many=True)  ###
    lead_source = serializers.SerializerMethodField()
    lead_status = serializers.SerializerMethodField()
    HOT_WARM_COLD =  serializers.SerializerMethodField()
    visited_by =  serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = FbLeads
        fields = ['project_name','HOT_WARM_COLD','lead_status','visited_by','lead_source','project_type_name']

    def to_representation(self, instance):
        # response = super().to_representation(instance)
        response = {}
        response['Project Name'] = self.get_project_names(instance)
        # response['Lead Source'] = self.get_lead_source(instance)
        response['status'] = self.get_status(instance)
        response['Enquiry Date'] = instance.created_at
        response['Last Updated Date And Time'] = instance.updated_at
        response['Customer Name'] = instance.full_name
        response['Phone Number'] = instance.phone_number
        response['visited By'] = self.get_visited_by(instance)
        response['Current Assigend Agent'] = self.get_assigned_to_name(instance)
        response['Executive Name'] = self.get_agent_name(instance)
        response['Project Type'] = self.get_project_type_names(instance)
        response['Lead Source'] = instance.lead_source
        response['Lead Status'] = self.get_lead_status(instance)
        response['HOT/WARM/COLD'] = self.get_HOT_WARM_COLD(instance)
        response['Feedback'] = instance.feedback 
        response['Expected Booking'] = "Yes" if instance.expected_booking else "No"
        response['Admin Status'] = instance.status_acc_admin
        response['Admin Comment'] = instance.feedback_acc_admin 
       
        
        return response

    def get_agent_name(self, instance):
        return instance.user.name if instance.user else None

    def get_assigned_to_name(self, instance):
        return instance.assigned_to.name if instance.assigned_to else None

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


    def get_project_type_names(self, instance):
        names = []
        if instance.project_type_name.exists():
            for project_type in instance.project_type_name.all():
                names.append(project_type.property_type)
        return names

    def get_project_names(self, instance):
        names = []
        if instance.project_name.exists():
            for project in instance.project_name.all():
                names.append(project.project_name)
        return names
       
   
    def get_lead_source(self, instance):
        return instance.lead_source.lead_source if instance.lead_source else None

    def get_site_visit_to_name(self, instance):
        return instance.site_visit_to.name if instance.site_visit_to else None
    # feedback and source of lead to fetch using reverse forigen key concept
    def get_lead_status(self, instance):
        lead_edit_instance = LeadEdit.objects.filter(fb_leads=instance).order_by('-created_at').first()
        if lead_edit_instance and lead_edit_instance.status_of_lead:
            return lead_edit_instance.status_of_lead.status_lead
        return None
    
    def get_visited_by(self, instance):
        lead_edit_instance = LeadEdit.objects.filter(fb_leads=instance).order_by('-created_at').first()
        if lead_edit_instance and lead_edit_instance.visited_by:
            return lead_edit_instance.visited_by.name
        return None

    def get_HOT_WARM_COLD(self, instance):
        lead_edit_instance = LeadEdit.objects.filter(fb_leads=instance).order_by('-created_at').first()
        if lead_edit_instance:
            return getattr(lead_edit_instance, 'status_of_lead_warm_hot_cold', None) if getattr(lead_edit_instance, 'status_of_lead_warm_hot_cold', None) else None
        return getattr(instance, 'status_of_lead_warm_hot_cold', None) if getattr(instance, 'status_of_lead_warm_hot_cold', None) else None


class FbLeadSiteVistExcelFileSerializer(serializers.ModelSerializer):
    project_name = serializers.StringRelatedField(many=True)  ####
    project_type_name = serializers.StringRelatedField(many=True)  ###
    lead_source = serializers.SerializerMethodField()
    lead_status = serializers.SerializerMethodField()
    HOT_WARM_COLD =  serializers.SerializerMethodField()
    visitedBy =  serializers.SerializerMethodField()
    visitNumber = serializers.SerializerMethodField()
    visitDate = serializers.SerializerMethodField()

    class Meta:
        model = FbLeads
        fields = ['project_name','HOT_WARM_COLD','lead_status','visitedBy','lead_source','project_type_name','visitNumber','visitDate']

    def to_representation(self, instance):
        # response = super().to_representation(instance)
        response = {}
        response['Project Name'] = self.get_project_names(instance)
        # response['Lead Source'] = self.get_lead_source(instance)
        response['Enquiry Date'] = instance.created_at
        response['Last Updated Date And Time'] = instance.updated_at
        response['Customer Name'] = instance.full_name
        response['Phone Number'] = instance.phone_number
        response['visited By'] = self.get_visited_by(instance)
        response['Current Assigend Agent'] = self.get_assigned_to_name(instance)
        response['Executive Name'] = self.get_agent_name(instance)
        response['Project Type'] = self.get_project_type_names(instance)
        response['Lead Source'] = instance.lead_source
        response['Lead Status'] = self.get_lead_status(instance)
        response['HOT/WARM/COLD'] = self.get_HOT_WARM_COLD(instance)
        response['Feedback'] = instance.feedback 
        response['Expected Booking'] = "Yes" if instance.expected_booking else "No"
        response['Admin Status'] = instance.status_acc_admin
        response['Admin Comment'] = instance.feedback_acc_admin 
        response['Visit Number'] = self.get_visit_number(instance)
        response['Visit Date'] = self.get_visit_date(instance)
        return response

    def get_agent_name(self, instance):
        return instance.user.name if instance.user else None

    def get_assigned_to_name(self, instance):
        return instance.assigned_to.name if instance.assigned_to else None

    def get_visited_by(self, instance):
        return instance.site_visit_to.name if instance.site_visit_to else None

    def get_project_type_names(self, instance):
        names = []
        if instance.project_type_name.exists():
            for project_type in instance.project_type_name.all():
                names.append(project_type.property_type)
        return names

    def get_project_names(self, instance):
        names = []
        if instance.project_name.exists():
            for project in instance.project_name.all():
                names.append(project.project_name)
        return names

   
    def get_lead_source(self, instance):
        return instance.lead_source.lead_source if instance.lead_source else None

    def get_site_visit_to_name(self, instance):
        return instance.site_visit_to.name if instance.site_visit_to else None
    # feedback and source of lead to fetch using reverse forigen key concept
    def get_lead_status(self, instance):
        lead_edit_instance = LeadEdit.objects.filter(fb_leads=instance).order_by('-created_at').first()
        if lead_edit_instance and lead_edit_instance.status_of_lead:
            return lead_edit_instance.status_of_lead.status_lead
        return None
    
    def get_visitedBy(self, instance):
        lead_edit_instance = LeadEdit.objects.filter(fb_leads=instance).order_by('-created_at').first()
        if lead_edit_instance and lead_edit_instance.visited_by:
            return lead_edit_instance.visited_by.name
        return None
    
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


    def get_HOT_WARM_COLD(self, instance):
        lead_edit_instance = LeadEdit.objects.filter(fb_leads=instance).order_by('-created_at').first()
        if lead_edit_instance:
            return getattr(lead_edit_instance, 'status_of_lead_warm_hot_cold', None) if getattr(lead_edit_instance, 'status_of_lead_warm_hot_cold', None) else None
        return getattr(instance, 'status_of_lead_warm_hot_cold', None) if getattr(instance, 'status_of_lead_warm_hot_cold', None) else None

class FbLeadCorporateLeadsExcelFileSerializer(serializers.ModelSerializer):
    project_name = serializers.StringRelatedField(many=True)  ####
    project_type_name = serializers.StringRelatedField(many=True)  ###
    lead_source = serializers.SerializerMethodField()
    lead_status = serializers.SerializerMethodField()
    HOT_WARM_COLD =  serializers.SerializerMethodField()
    visited_by =  serializers.SerializerMethodField()

    class Meta:
        model = FbLeads
        fields = ['HOT_WARM_COLD','lead_status','visited_by','lead_source']

    def to_representation(self, instance):
        # response = super().to_representation(instance)
        response = {}
        response['Project Name'] = self.get_project_names(instance)
        # response['Lead Source'] = self.get_lead_source(instance)
        response['Enquiry Date'] = instance.created_at
        response['Last Updated Date And Time'] = instance.updated_at
        response['Customer Name'] = instance.full_name
        response['Phone Number'] = instance.phone_number
        response['visited By'] = self.get_visited_by(instance)
        response['Current Assigend Agent'] = self.get_assigned_to_name(instance)
        response['Executive Name'] = self.get_agent_name(instance)
        response['Project Type'] = self.get_project_type_names(instance)
        response['Lead Source'] = instance.lead_source
        response['Lead Status'] = self.get_lead_status(instance)
        response['HOT/WARM/COLD'] = self.get_HOT_WARM_COLD(instance)
        response['Feedback'] = instance.feedback 
        response['Expected Booking'] = "Yes" if instance.expected_booking else "No"
        response['Admin Status'] = instance.status_acc_admin
        response['Admin Comment'] = instance.feedback_acc_admin 
       
        
        return response

    def get_agent_name(self, instance):
        return instance.user.name if instance.user else None

    def get_assigned_to_name(self, instance):
        return instance.assigned_to.name if instance.assigned_to else None


    def get_project_type_names(self, instance):
        names = []
        if instance.project_type_name.exists():
            for project_type in instance.project_type_name.all():
                names.append(project_type.property_type)
        return names

    def get_project_names(self, instance):
        names = []
        if instance.project_name.exists():
            for project in instance.project_name.all():
                names.append(project.project_name)
        return names


   
    def get_lead_source(self, instance):
        return instance.lead_source.lead_source if instance.lead_source else None

    def get_site_visit_to_name(self, instance):
        return instance.site_visit_to.name if instance.site_visit_to else None
    # feedback and source of lead to fetch using reverse forigen key concept
    def get_lead_status(self, instance):
        lead_edit_instance = LeadEdit.objects.filter(fb_leads=instance).order_by('-created_at').first()
        if lead_edit_instance and lead_edit_instance.status_of_lead:
            return lead_edit_instance.status_of_lead.status_lead
        return None
    
    def get_visited_by(self, instance):
        lead_edit_instance = LeadEdit.objects.filter(fb_leads=instance).order_by('-created_at').first()
        if lead_edit_instance and lead_edit_instance.visited_by:
            return lead_edit_instance.visited_by.name
        return None

    def get_HOT_WARM_COLD(self, instance):
        lead_edit_instance = LeadEdit.objects.filter(fb_leads=instance).order_by('-created_at').first()
        if lead_edit_instance:
            return getattr(lead_edit_instance, 'status_of_lead_warm_hot_cold', None) if getattr(lead_edit_instance, 'status_of_lead_warm_hot_cold', None) else None
        return getattr(instance, 'status_of_lead_warm_hot_cold', None) if getattr(instance, 'status_of_lead_warm_hot_cold', None) else None


# excel files for civil workers

class CivilStatgesExcelFilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CivilStatges
        fields = "__all__"
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['name'] = self.get_user_name(instance)
        response['unit_no'] = self.get_unit_number(instance)
        response['square_fit'] = self.get_unit_number_area(instance)
        return response
    def get_user_name(self, instance):
        return instance.user.name if instance.user else None
    def get_unit_number(self, instance):
        return instance.unit.unit_no if instance.unit else None
    def get_unit_number_area(self, instance):
        return instance.unit.square_fit if instance.unit else None
