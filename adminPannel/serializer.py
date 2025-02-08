from rest_framework import serializers
from social.models import FbLeads, LeadEdit

class NextScheduledLeadSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(source='fb_leads.assigned_to.name')
    date_of_visit = serializers.DateField(source='next_schedule_date')
    name = serializers.CharField(source='fb_leads.full_name')

    class Meta:
        model = LeadEdit
        fields = ['agent_name', 'date_of_visit', 'name']

class FbLeadsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FbLeads
        fields = '__all__'  # Include all fields or specify a subset

class LeadGroupSerializer(serializers.Serializer):
    assigned_to = serializers.CharField(source='assigned_to__name')
    lead_count = serializers.IntegerField()
    
    # leads = FbLeadsSerializer(many=True)

class LeadEditGroupSerializer(serializers.Serializer):
    assigned_to__name = serializers.CharField()
    booked_count = serializers.IntegerField()
    site_visit_count = serializers.IntegerField()
    total_count = serializers.IntegerField()