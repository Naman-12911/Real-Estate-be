from django.shortcuts import render
from rest_framework.views import APIView
from account.models import User
from  social.models import FbLeads,LeadEdit
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
# Create your views here.

class TransferDataToAnotherAgent(APIView):
    def post(self, request):
        # Extract user IDs from the request data
        old_user_id = request.data.get('old_user_id')
        new_user_id = request.data.get('new_user_id')

        # Get the old and new users
        old_user = get_object_or_404(User, id=old_user_id)
        new_user = get_object_or_404(User, id=new_user_id)

        # Transfer FbLeads
        FbLeads.objects.filter(user=old_user).update(user=new_user)
        FbLeads.objects.filter(assigned_to=old_user).update(assigned_to=new_user)
        FbLeads.objects.filter(site_visit_to=old_user).update(site_visit_to=new_user)
        FbLeads.objects.filter(corporate_visit_to=old_user).update(corporate_visit_to=new_user)

        # Transfer LeadEdit
        LeadEdit.objects.filter(user=old_user).update(user=new_user)
        LeadEdit.objects.filter(visited_by=old_user).update(visited_by=new_user)
        
        # Update only if specific fields match old_user
        FbLeads.objects.filter(assigned_to=old_user).update(assigned_to=new_user)
        FbLeads.objects.filter(site_visit_to=old_user).update(site_visit_to=new_user)
        FbLeads.objects.filter(corporate_visit_to=old_user).update(corporate_visit_to=new_user)
        LeadEdit.objects.filter(visited_by=old_user).update(visited_by=new_user)

        # Return a success response
        return Response({"message": "Leads transferred successfully"}, status=status.HTTP_200_OK) 