from django.shortcuts import render
from .models import *
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializer import *
from django.http.response import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q, OuterRef, Subquery, Max, F
from itertools import cycle
from account.models import User, UserHoliday, FCMTokens
from .fcm_manager import sendPush
import time
from operator import itemgetter
from realEstate.pagination import CommonPagination
from django.db.models import Count
from django.utils import timezone
import re
from dateutil.parser import parse
from django.db import transaction

# Create your views here.
class Fb_View(APIView):
    permission_classes = [IsAuthenticated,]
    def get_object(self, pk):
        try:
            return FbLeads.objects.get(pk=pk)
        except FbLeads.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
        # If whats app number  is match then create lead edit other wise not and check the lead is already dump or permanent Dump and normal.
        # if pk:
        #     data = self.get_object(pk)
        #     serializer = FbLeadSerializer(data)
            
        #     if 'raw' in serializer.data:
        #         if serializer.data['raw']:
        #             if "whatsapp_no./_phone_no." in serializer.data['raw']:
        #                 serializer.data['alt_phone_number'] = serializer.data['raw']['whatsapp_no./_phone_no.']

        #     return Response(serializer.data)
        if not pk:
            return Response({"error": "Lead ID not provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Get the FbLeads instance to retrieve
        if pk:
            fb_lead = self.get_object(pk)
            serializer = FbLeadSerializer(fb_lead)
            data = serializer.data

            # Check if 'raw' contains 'whatsapp_no./_phone_no.' and matches the phone number
            if 'raw' in data and data['raw']:
                whatsapp_no = data['raw'].get("whatsapp_no./_phone_no.")
                if whatsapp_no and whatsapp_no == fb_lead.phone_number:
                    # Determine the description based on the lead's status
                    description = "Lead reactivated"
                    if fb_lead.permanent_dump_lead:
                        description = f"Lead reactivated from permanent dump. Lead ID: {fb_lead.id}"
                    elif fb_lead.dump_lead:
                        description = f"Lead reactivated from dump. Lead ID: {fb_lead.id}"
                    else:
                        description = f"Lead reactivated. Lead ID: {fb_lead.id}"

                    # Create or update LeadEdit entry
                    lead_edit_data = {
                        'fb_leads': fb_lead.id,
                        'user': request.user.id,
                        'description': description,
                    }
                    serializer_edit = LeadEditSerializer(data=lead_edit_data)
                    if serializer_edit.is_valid():
                        serializer_edit.save()
                    else:
                        return Response(serializer_edit.errors, status=status.HTTP_400_BAD_REQUEST)

                    # Update fb_lead to set dump_lead and permanent_dump_lead to False
                    fb_lead.dump_lead = False
                    fb_lead.permanent_dump_lead = False
                    fb_lead.updated_at = timezone.now()
                    fb_lead.save()

                    # Add alternative phone number to response if needed
                    data['alt_phone_number'] = whatsapp_no
            return Response(data, status=status.HTTP_200_OK)
        else:
            fb_leads = FbLeads.objects.exclude(
            Q(dump_lead=True) |
            Q(site_visit=True) |
            Q(booked=True) |
            Q(corporate_visit=True)
            ).order_by('-created_at')

            if request.user.sales_employee:
                fb_leads = fb_leads.filter(Q(assigned_to=request.user) | Q(site_visit_to=request.user) | Q(corporate_visit_to=request.user))

            data = []
            now = timezone.now()  # Get the current time in the timezone-aware format
            thirty_day_minutes_ago = now - timedelta(days=30)  # Get the datetime 7 minutes ago
            for fb_lead in fb_leads:
                last_lead_edit = fb_lead.leadedit_set.last()  # Get the last lead edit related to this fb lead
                if last_lead_edit:
                    last_update_time = last_lead_edit.created_at
                    # Check if the last update was more than 48 hours ago
                    if now - last_update_time > timedelta(hours=48):
                        fb_lead.status = 'Delayed'
                else:
                    # No lead edit record found, check if the fb_lead was created more than 48 hours ago
                    if fb_lead.created_time:
                        if now - fb_lead.created_time > timedelta(hours=48):
                            fb_lead.status = 'Delayed'
                
                # Check if the fb_lead was created more than 7 minutes ago
                if fb_lead.created_time:
                    if fb_lead.created_time < thirty_day_minutes_ago and not last_lead_edit:
                        fb_lead.dump_lead = True
                
                fb_lead.save()  # Save the updated fb_lead object
                
                data.append(fb_lead)
            
            serializer = FbLeadSerializer(data, many=True)
            for i in serializer.data:
                if 'raw' in i:
                    if i['raw']:
                        if "whatsapp_no./_phone_no." in i['raw']:
                            i['alt_phone_number'] = i['raw']['whatsapp_no./_phone_no.']
                        
            return Response(serializer.data)
            
            
        
    def post(self, request):
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            mutable_data['assigned_to'] = current_user.id 

            # checking if lead already exists and is dumped.
            if FbLeads.objects.filter(phone_number=mutable_data['phone_number']).exists():
                fb_lead = FbLeads.objects.get(phone_number=mutable_data['phone_number'])
                old_user = fb_lead.assigned_to.name
                if fb_lead.dump_lead:
                    del mutable_data['user']
                    mutable_data['permanent_dump_lead'] = False
                    mutable_data['dump_lead'] = False
                    serializer = FbLeadPostSerializer(instance=fb_lead, data=mutable_data, partial=True)
                    if not serializer.is_valid():
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    serializer.save()
                    fb_lead = FbLeads.objects.get(id=serializer.data['id'])
                    fb_lead.updated_at = timezone.now()
                    fb_lead.save()

                    mutable_data = {
                        "user":request.user.id,
                        "fb_leads":fb_lead.id,
                        "description":f"This dump lead has been updated and transferred from {old_user} to {User.objects.get(id=serializer.data['assigned_to']).name}."
                    }

                    serializer_edit = LeadEditSerializer(data=mutable_data)
                    if serializer_edit.is_valid():
                        serializer_edit.save()
                    
                    notification_data = {"sent_to":serializer.data['assigned_to'], "head":f"Dump Lead: {fb_lead.full_name}", "message":f"Dump lead has been updated and assigned to you. Lead ID:{fb_lead.id}"}
                    notiserializer = NotificationStoreSerializer(data=notification_data)
                    if notiserializer.is_valid():
                        notiserializer.save()

                    try:
                        sendPush(f"Dump Lead: {fb_lead.full_name}", "Dump lead has been updated and assigned to you.", fcm_tokens)
                    except Exception as e:
                        print("Error while sending push notification",e)

                    response = Response()

                    response.data = {
                        'message': 'Lead  Created Successfully',
                        # 'data': serializer.data
                    }
                    return response
            token_query = FCMTokens.objects.filter(user=current_user.id)

            fcm_tokens = [i.device_token for i in token_query if i.device_token!=""]
            

            serializer = FbLeadPostSerializer(data=mutable_data)

            # Check if the data passed is valid
            serializer.is_valid(raise_exception=True)
            serializer.save()
            print(serializer.data)
            # Return Response to User
            notification_data = {"sent_to":current_user.id, "head":f"New Lead: {serializer.data['full_name']}", "message":f"New lead has been assigned to you. Lead ID:{serializer.data['id']}"}
            notiserializer = NotificationStoreSerializer(data=notification_data)
            if notiserializer.is_valid():
                notiserializer.save()

            try:
                sendPush(f"New Lead: {serializer.data['full_name']}", "New lead has been assigned to you.", fcm_tokens)
            except Exception as e:
                print("Error while sending push notification",e)
            response = Response()

            response.data = {
                'message': 'Lead  Created Successfully',
                # 'data': serializer.data
            }
            return response

    
    # def patch(self, request, pk=None, format=None):
    #         # Get the todo to update
    #         FbLeads_to_update = FbLeads.objects.get(pk=pk)
    #         current_user = request.user
    #         mutable_data = request.data.copy()
    #         mutable_data['user'] = current_user.id
    #         # request.data['user'] = request.user.id
    #         if 'project_name' in mutable_data:
    #             print(mutable_data['project_name'])

    #         serializer = FbLeadPostSerializer(instance=FbLeads_to_update, data=mutable_data, partial=True)
    #         token_query = FCMTokens.objects.filter(user=FbLeads_to_update.assigned_to)

    #         fcm_tokens = [i.device_token for i in token_query if i.device_token != ""]
    #         # fcm_tokens = []
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save()
    #         response = Response()
    #         notification_data = {
    #             "sent_to": current_user.id,
    #             "head": "Lead Update",
    #             "message": f"Lead has been updated successfully. Lead ID:{serializer.data['id']}"
    #         }
    #         response.data = {
    #             'message': 'Leads updated Successfully',
    #             'data': serializer.data
    #         }

    #         return response

    def patch(self, request, pk=None, format=None):
        # Get the FbLeads instance to update
        fb_lead_to_update = FbLeads.objects.get(pk=pk)
        current_user = request.user
        mutable_data = request.data.copy()
        mutable_data['user'] = current_user.id
      
        
        # Check if corporate_visit_to is True
        if mutable_data.get('corporate_visit', False) or fb_lead_to_update.corporate_visit:
            # Create LeadEdit entry
            lead_edit_data = {
                'fb_leads': fb_lead_to_update.id,
                'user': current_user.id,
                'description': f"Lead updated with corporate visit"
                # Add other fields as needed
            }
            serializer_edit = LeadEditSerializer(data=lead_edit_data)
            if serializer_edit.is_valid():
                serializer_edit.save()

        # Update FbLeads instance
        serializer = FbLeadPostSerializer(instance=fb_lead_to_update, data=mutable_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Send notification
        # notification_data = {
        #     "sent_to": current_user.id,
        #     "head": "Lead Update",
        #     "message": f"Lead has been updated successfully. Lead ID: {serializer.data['id']}"
        # }
        # notiserializer = NotificationStoreSerializer(data=notification_data)
        # if notiserializer.is_valid():
        #     notiserializer.save()

        # Send push notification
        # try:
        #     token_query = FCMTokens.objects.filter(user=current_user.id)
        #     fcm_tokens = [token.device_token for token in token_query if token.device_token != ""]
        #     #sendPush(f"Lead Update", f"Lead ID: {serializer.data['id']} has been updated.", fcm_tokens)
        # except Exception as e:
        #     print("Error while sending push notification:", e)

        response_data = {
            'message': 'Lead updated Successfully',
            'data': serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)
    
    def delete(self, request, pk, format=None):
        FbLeads_to_delete =  FbLeads.objects.get(pk=pk)

            # delete the todo
        FbLeads_to_delete.delete()

        return Response({
            'message': 'Leads upated Successfully',
        })
    


class LeadSourceAPIView(APIView):
    permission_classes = [IsAuthenticated,]
    def get_object(self, pk):
        try:
            return LeadSource.objects.get(pk=pk)
        except LeadSource.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
        
        if pk:
            data = self.get_object(pk)
            serializer = LeadSourceSerializer(data)
            return Response(serializer.data)

        else:
            data = LeadSource.objects.all().order_by('-created_at')
            serializer = LeadSourceSerializer(data, many=True)

            return Response(serializer.data)
    
    
    def post(self, request):
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            
            serializer = LeadSourceSerializer(data=mutable_data)

            # Check if the data passed is valid
            print()
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Return Response to User

            response = Response()

            response.data = {
                'message': 'Lead Source  Created Successfully',
                'data': serializer.data
            }
            return response
    
    def patch(self, request, pk=None, format=None):
                # Get the todo to update
            LeadSource_to_update = LeadSource.objects.get(pk=pk)
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            # request.data['user'] = request.user.id

            serializer = LeadSourceSerializer(instance=LeadSource_to_update,data=mutable_data, partial=True)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = Response()

            response.data = {
                'message': 'Lead Source upated Successfully',
                'data': serializer.data
            }

            return response
    def delete(self, request, pk, format=None):
        LeadSource_to_delete =  LeadSource.objects.get(pk=pk)

            # delete the todo
        LeadSource_to_delete.delete()

        return Response({
            'message': 'Lead Source upated Successfully',
        })
    
class MediumOfLeadAPIView(APIView):
    permission_classes = [IsAuthenticated,]
    def get_object(self, pk):
        try:
            return MediumOfLead.objects.get(pk=pk)
        except MediumOfLead.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
        
        if pk:
            data = self.get_object(pk)
            serializer = MediumOfLeadSerializer(data)
            return Response(serializer.data)

        else:
            data = MediumOfLead.objects.all().order_by('medium')
            serializer = MediumOfLeadSerializer(data, many=True)

            return Response(serializer.data)
    
    
    def post(self, request):
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            
            serializer = MediumOfLeadSerializer(data=mutable_data)

            # Check if the data passed is valid
            print()
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Return Response to User

            response = Response()

            response.data = {
                'message': 'Medium Of Lead  Created Successfully',
                'data': serializer.data
            }
            return response
    
    def patch(self, request, pk=None, format=None):
                # Get the todo to update
            MediumOfLead_to_update = MediumOfLead.objects.get(pk=pk)
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            # request.data['user'] = request.user.id

            serializer = MediumOfLeadSerializer(instance=MediumOfLead_to_update,data=mutable_data, partial=True)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = Response()

            response.data = {
                'message': 'Medium Of Lead upated Successfully',
                'data': serializer.data
            }

            return response
    def delete(self, request, pk, format=None):
        MediumOfLead_to_delete =  MediumOfLead.objects.get(pk=pk)

            # delete the todo
        MediumOfLead_to_delete.delete()

        return Response({
            'message': 'Medium Of Lead upated Successfully',
        })
    


class preferredLocationAPIView(APIView):
    permission_classes = [IsAuthenticated,]
    def get_object(self, pk):
        try:
            return preferredLocation.objects.get(pk=pk)
        except preferredLocation.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
        
        if pk:
            data = self.get_object(pk)
            serializer = preferredLocationSerializer(data)
            return Response(serializer.data)

        else:
            data = preferredLocation.objects.all().order_by('-created_at')
            serializer = preferredLocationSerializer(data, many=True)

            return Response(serializer.data)
    
    
    def post(self, request):
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            
            serializer = preferredLocationSerializer(data=mutable_data)

            # Check if the data passed is valid
            print()
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Return Response to User

            response = Response()

            response.data = {
                'message': 'preferred Location  Created Successfully',
                'data': serializer.data
            }
            return response
    
    def patch(self, request, pk=None, format=None):
                # Get the todo to update
            preferredLocation_to_update = preferredLocation.objects.get(pk=pk)
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            # request.data['user'] = request.user.id

            serializer = preferredLocationSerializer(instance=preferredLocation_to_update,data=mutable_data, partial=True)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = Response()

            response.data = {
                'message': 'preferred Location upated Successfully',
                'data': serializer.data
            }

            return response
    def delete(self, request, pk, format=None):
        preferredLocation_to_delete =  preferredLocation.objects.get(pk=pk)

            # delete the todo
        preferredLocation_to_delete.delete()

        return Response({
            'message': 'preferred Location upated Successfully',
        })


class ReasonAPIView(APIView):
    permission_classes = [IsAuthenticated,]
    def get_object(self, pk):
        try:
            return Reason.objects.get(pk=pk)
        except Reason.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
       

        if pk:
            data = self.get_object(pk)
            serializer = ReasonSerializer(data)
            return Response(serializer.data)

        else:
            queryset = Reason.objects.all().order_by('-created_at')


            serializer = ReasonSerializer(queryset, many=True)
            return Response(serializer.data)
    
    
    def post(self, request):
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            
            serializer = ReasonSerializer(data=mutable_data)

            # Check if the data passed is valid
            print()
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Return Response to User

            response = Response()

            response.data = {
                'message': 'Feed Back Created Successfully',
                'data': serializer.data
            }
            return response
    
    def patch(self, request, pk=None, format=None):
                # Get the todo to update
            Reason_to_update = Reason.objects.get(pk=pk)
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            # request.data['user'] = request.user.id

            serializer = ReasonSerializer(instance=Reason_to_update,data=mutable_data, partial=True)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = Response()

            response.data = {
                'message': 'Feed Back upated Successfully',
                'data': serializer.data
            }

            return response
    def delete(self, request, pk, format=None):
        Reason_to_delete =  Reason.objects.get(pk=pk)

            # delete the todo
        Reason_to_delete.delete()

        return Response({
            'message': 'Feed Back upated Successfully',
        })
    




class BudgetAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None, format=None):
        if pk:
            data = self.get_object(pk)
            serializer = BudgetSerializer(data)
            return Response(serializer.data)
        else:
            data = Budget.objects.all()

            def convert_budget_to_number(budget):
                # Remove spaces and convert to lower case for uniformity
                budget = budget.replace(' ', '').lower()
                # Find all numbers in the budget string
                numbers = re.findall(r'\d+\.?\d*', budget)
                if numbers:
                    # Take the first number found as the base value
                    value = float(numbers[0])
                    if 'l' in budget:
                        return value * 1e5  # 1 lakh = 100,000
                    elif 'cr' in budget:
                        return value * 1e7  # 1 crore = 10,000,000
                    else:
                        return value  # Return the number itself if no multiplier is found
                return float('inf')  # If no number is found, return a very large number

            # Convert the queryset to a list and sort it using the custom function
            sorted_data = sorted(data, key=lambda budget: convert_budget_to_number(budget.max_budget))

            serializer = BudgetSerializer(sorted_data, many=True)
            return Response(serializer.data)
    
    
    def post(self, request):
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            
            serializer = BudgetSerializer(data=mutable_data)

            # Check if the data passed is valid
            print()
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Return Response to User

            response = Response()

            response.data = {
                'message': 'Budget Created Successfully',
                'data': serializer.data
            }
            return response
    
    def patch(self, request, pk=None, format=None):
                # Get the todo to update
            Budget_to_update = Budget.objects.get(pk=pk)
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            # request.data['user'] = request.user.id

            serializer = BudgetSerializer(instance=Budget_to_update,data=mutable_data, partial=True)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = Response()

            response.data = {
                'message': 'Budget upated Successfully',
                'data': serializer.data
            }

            return response
    def delete(self, request, pk, format=None):
        Budget_to_delete =  Budget.objects.get(pk=pk)

            # delete the todo
        Budget_to_delete.delete()

        return Response({
            'message': 'Budget upated Successfully',
        })
    

class StatusLeadAPIView(APIView):
    permission_classes = [IsAuthenticated,]
    def get_object(self, pk):
        try:
            return StatusLead.objects.get(pk=pk)
        except StatusLead.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
        
        if pk:
            data = self.get_object(pk)
            serializer = StatusLeadSerializer(data)
            return Response(serializer.data)

        else:
            data = StatusLead.objects.all().order_by('status_lead')
            
            serializer = StatusLeadSerializer(data, many=True)

            return Response(serializer.data)
    
    
    def post(self, request):
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            
            serializer = StatusLeadSerializer(data=mutable_data)

            # Check if the data passed is valid
            print()
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Return Response to User

            response = Response()

            response.data = {
                'message': 'Status Lead Created Successfully',
                'data': serializer.data
            }
            return response
    
    def patch(self, request, pk=None, format=None):
                # Get the todo to update
            StatusLead_to_update = StatusLead.objects.get(pk=pk)
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            # request.data['user'] = request.user.id

            serializer = StatusLeadSerializer(instance=StatusLead_to_update,data=mutable_data, partial=True)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = Response()

            response.data = {
                'message': 'Status Lead upated Successfully',
                'data': serializer.data
            }

            return response
    def delete(self, request, pk, format=None):
        StatusLead_to_delete =  StatusLead.objects.get(pk=pk)

            # delete the todo
        StatusLead_to_delete.delete()

        return Response({
            'message': 'Status Lead upated Successfully',
        })


class ModeLeadAPIView(APIView):
    permission_classes = [IsAuthenticated,]
    def get_object(self, pk):
        try:
            return ModeLead.objects.get(pk=pk)
        except ModeLead.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
        
        if pk:
            data = self.get_object(pk)
            serializer = ModeLeadSerializer(data)
            return Response(serializer.data)

        else:
            data = ModeLead.objects.all().order_by('-created_at')
            serializer = ModeLeadSerializer(data, many=True)

            return Response(serializer.data)
    
    
    def post(self, request):
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            
            serializer = ModeLeadSerializer(data=mutable_data)

            # Check if the data passed is valid
            print()
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Return Response to User

            response = Response()

            response.data = {
                'message': 'Mode Lead Created Successfully',
                'data': serializer.data
            }
            return response
    
    def patch(self, request, pk=None, format=None):
                # Get the todo to update
            ModeLead_to_update = ModeLead.objects.get(pk=pk)
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            # request.data['user'] = request.user.id

            serializer = ModeLeadSerializer(instance=ModeLead_to_update,data=mutable_data, partial=True)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = Response()

            response.data = {
                'message': 'Mode Lead upated Successfully',
                'data': serializer.data
            }

            return response
    def delete(self, request, pk, format=None):
        ModeLead_to_delete =  ModeLead.objects.get(pk=pk)

            # delete the todo
        ModeLead_to_delete.delete()

        return Response({
            'message': 'Mode Lead upated Successfully',
        })
    

class LeadEditAPIView(APIView):
    permission_classes = [IsAuthenticated,]
    def get_object(self, pk):
        try:
            return LeadEdit.objects.get(pk=pk)
        except LeadEdit.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
        
        if pk:
            data = self.get_object(pk)
            serializer = LeadEditSerializer(data)
            return Response(serializer.data)

        else:
            data = LeadEdit.objects.all().order_by('-created_at')
            serializer = LeadEditSerializer(data, many=True)
            return Response(serializer.data)
    
    
    # def post(self, request):
    #         current_user = request.user
    #         mutable_data = request.data.copy()
    #         mutable_data['user'] = current_user.id 
            
    #         serializer = LeadEditSerializer(data=mutable_data)
    #         token_query = FCMTokens.objects.filter(user=current_user.id)
    #         fcm_tokens = [i.device_token for i in token_query if i.device_token!=""]
    #         if 'next_schedule_date' in mutable_data:
    #             noti_instance = NotificationStore.objects.filter(head=FbLeads.objects.get(id=mutable_data['fb_leads']).full_name, sent_to=current_user,message__icontains=f"Lead ID:{mutable_data['fb_leads']}")
    #             noti_instance.update(seen=True)
    #             notification_data = {"sent_to":current_user.id, "head":FbLeads.objects.get(id=mutable_data['fb_leads']).full_name, "message":f"Next scheduled at {mutable_data['next_schedule_date']} for {mutable_data['next_schedule_mode']}, Lead ID:{mutable_data['fb_leads']}"}
    #             notiserializer = NotificationStoreSerializer(data=notification_data)
    #             if notiserializer.is_valid():
    #                 notiserializer.save()
    #             try:
    #                 sendPush(mutable_data['fb_leads'].full_name, f"Next scheduled at {mutable_data['next_schedule_date']} for {mutable_data['next_schedule_mode']}, Lead ID:{mutable_data['fb_leads']}", fcm_tokens)
    #             except Exception as e:
    #                 print("Error while sending push notification",e)
    #         # else:
    #         #     notification_data = {"sent_to":current_user.id, "head":FbLeads.objects.get(id=mutable_data['fb_leads']).full_name, "message":f"Next scheduled at {mutable_data['next_schedule_date']} for {mutable_data['next_schedule_mode']}, Lead ID:{mutable_data['fb_leads']}"}
    #         #     notiserializer = NotificationStoreSerializer(data=notification_data)
    #         #     if notiserializer.is_valid():
    #         #         notiserializer.save()
    #         #     try:
    #         #         sendPush(mutable_data['fb_leads'].full_name, f"Next scheduled at {mutable_data['next_schedule_date']} for {mutable_data['next_schedule_mode']}, Lead ID:{mutable_data['fb_leads']}", fcm_tokens)
    #         #     except Exception as e:
    #         #         print("Error while sending push notification",e)
    #         # Check if the data passed is valid
    #         lead = FbLeads.objects.get(id=mutable_data['fb_leads'])
    #         if 'site_visit_to' in mutable_data:
    #             lead.site_visit_to = User.objects.get(id=mutable_data['site_visit_to'])
    #             lead.site_visit = True
    #             lead.save()
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save()
    #         # Return Response to User
    #         data = serializer.data.copy()
    #         data['site_visit_to'] = User.objects.get(id=mutable_data['site_visit_to']).name
    #         response = Response()

    #         response.data = {
    #             'message': 'Lead Edit Created Successfully',
    #             'data': data
    #         }
    #         return response

    def post(self, request):
        current_user = request.user
        mutable_data = request.data.copy()
        mutable_data['user'] = current_user.id 
        
        serializer = LeadEditSerializer(data=mutable_data)
        token_query = FCMTokens.objects.filter(user=current_user.id)
        fcm_tokens = [i.device_token for i in token_query if i.device_token!=""]
        if 'next_schedule_date' in mutable_data:
            noti_instance = NotificationStore.objects.filter(message__icontains=f"Lead ID:{mutable_data['fb_leads']}")
            noti_instance.update(seen=True)
            inst = ModeLead.objects.get(id=mutable_data['mode'])
            # if inst.status_lead in ['Booked','Dump']:
            # if inst.status_lead not in ['Booked','Dump']:
            #     mode = ModeLead.objects.get(id=mutable_data['next_schedule_mode'])
                # notification_data = {"sent_to":current_user.id, "head":FbLeads.objects.get(id=mutable_data['fb_leads']).full_name, "message":f"Next scheduled at {mutable_data['next_schedule_date']} for {mode.mode_lead}, Lead ID:{mutable_data['fb_leads']}"}
                # notiserializer = NotificationStoreSerializer(data=notification_data)
                # if notiserializer.is_valid():
                #     notiserializer.save()
                # try:
                #     sendPush(mutable_data['fb_leads'].full_name, f"Next scheduled at {mutable_data['next_schedule_date']} for {mode.mode_lead}, Lead ID:{mutable_data['fb_leads']}", fcm_tokens)
                # except Exception as e:
                #     print("Error while sending push notification",e)

        lead = FbLeads.objects.get(id=mutable_data['fb_leads'])
        save_extra = False
        # Check if 'site_visit_to' key is present in mutable_data
        if 'site_visit_to' in mutable_data:
            if mutable_data['site_visit_to']!="" and mutable_data['site_visit_to']:
                lead.site_visit_to = User.objects.get(id=mutable_data['site_visit_to'])
                lead.site_visit = True
                lead.save()

       
        mode_id = mutable_data['mode']
        site_visit_count = 0
         # Count site visits based on mode
        if mode_id:
            mode_instance = ModeLead.objects.get(pk=mode_id)
            if mode_instance.mode_lead == 'Site Visit':
                leadedit = LeadEdit.objects.filter(mode=mode_instance.id, fb_leads=lead)
                if leadedit.exists():
                    site_visit_count = leadedit.count()
                lead.site_visit = True
                lead.updated_at = timezone.now()
                lead.save()

        elif mode_id:
            mode_instance = ModeLead.objects.get(pk=mode_id)
            if mode_instance.mode_lead == 'Re-Visit':
                leadedit = LeadEdit.objects.filter(mode=mode_instance.id, fb_leads=lead)
                if leadedit.exists():
                    site_visit_count = leadedit.count()
                lead.site_visit = True
                lead.updated_at = timezone.now()
                lead.save()
        if mode_id:
            mode_instance = ModeLead.objects.get(pk=mode_id)
            if mode_instance.mode_lead == 'Site Visit':
                # Update the related FbLeads instance to mark it as 'Site Visit'
                leadedit = LeadEdit.objects.filter(mode=mode_instance.id, fb_leads=lead)
                if leadedit.exists():
                    site_visit_count = leadedit.count()

                if lead.dump_lead:
                    lead.dump_lead = False
                    lead.permanent_dump_lead = False
                    mutable_data = {
                        "user": request.user.id,
                        "fb_leads": lead.id,
                        "description": f"As this lead was dumped and site visited by {request.user.name}, it is transferred from {lead.assigned_to.name} to {request.user.name}."
                    }
                    lead.assigned_to = request.user

                    serializer_edit = LeadEditSerializer(data=mutable_data)
                    if serializer_edit.is_valid():
                        save_extra = True

                lead.site_visit = True
                lead.updated_at = timezone.now()
                lead.save()
        status_lead_id = mutable_data.get('status_of_lead')
        if status_lead_id:
            status_lead_instance = StatusLead.objects.get(pk=status_lead_id)
            if status_lead_instance.status_lead == 'Dump':
                # Update the related FbLeads instance to mark it as 'Dump'
                # lead = lead_edit_instance.fb_leads
                lead.dump_lead = True
                lead.updated_at = timezone.now()
                lead.save()

            # elif status_lead_instance.status_lead == 'Site Visit':
            #     # Update the related FbLeads instance to mark it as 'Site Visit'
            #     leadedit = LeadEdit.objects.filter(mode=status_lead_instance.id, fb_leads=lead)
            #     if leadedit.exists():
            #         site_visit_count = leadedit.count()

            #     # lead = lead_edit_instance.fb_leads
            #     if lead.dump_lead:
            #         lead.dump_lead = False
            #         lead.permanent_dump_lead = False
            #         mutable_data = {
            #             "user":request.user.id,
            #             "fb_leads":lead.id,
            #             "description":f"As this lead was dump and site visited by {request.user.name}, so it is transferred from {lead.assigned_to.name} to {request.user.name}."
            #         }
            #         lead.assigned_to = request.user

            #         serializer_edit = LeadEditSerializer(data=mutable_data)
            #         if serializer_edit.is_valid():
            #             save_extra = True

            #     lead.site_visit = True
            #     lead.updated_at = timezone.now()
            #     lead.save()

            elif status_lead_instance.status_lead == 'Booked':
                # Update the related FbLeads instance to mark it as 'Site Visit'
                # lead = lead_edit_instance.fb_leads
                lead.booked = True
                lead.updated_at = timezone.now()
                lead.save()

            elif status_lead_instance.status_lead == 'Corporate Visit':
                # Update the related FbLeads instance to mark it as 'Site Visit'
                # lead = lead_edit_instance.fb_leads
                lead.corporate_visit = True
                lead.updated_at = timezone.now()
                lead.save()

            elif status_lead_instance.status_lead == 'Intersted':
                # Update the related FbLeads instance to mark it as 'Site Visit'
                # lead = lead_edit_instance.fb_leads
                lead.intersted = True
                lead.updated_at = timezone.now()
                lead.save()

        # Check if the data passed is valid
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        if save_extra:
            serializer_edit.save()

        # Update feedback
        lead.feedback = serializer.data['description']
        lead.save()
        
        leadedit = LeadEdit.objects.get(pk=serializer.data['id'])
        leadedit.site_visits = site_visit_count
        leadedit.save()
        
        # Return Response to User
        data = serializer.data.copy()
        # Access 'site_visit_to' only if it exists in mutable_data
        if 'site_visit_to' in mutable_data:
            if mutable_data['site_visit_to']!="" and mutable_data['site_visit_to']:
                data['site_visit_to'] = User.objects.get(id=mutable_data['site_visit_to']).name
        
        response = Response()
        response.data = {
            'message': 'Discussion added Successfully',
            'data': data
        }
        return response

    
    def patch(self, request, pk=None, format=None):
        current_user = request.user
        try:
            # Get the LeadEdit instance to update
            lead_edit_instance = LeadEdit.objects.get(pk=pk)
            
            # Check if the status_of_lead is 'Dump' in the request data
            status_lead_id = request.data.get('status_of_lead', None)
            if status_lead_id:
                status_lead_instance = StatusLead.objects.get(pk=status_lead_id)
                if status_lead_instance.status_lead.lower() == 'dump':
                # Update the LeadEdit instance
                    serializer = LeadEditSerializer(instance=lead_edit_instance, data=request.data, partial=True)
                    token_query = FCMTokens.objects.filter(user=request.data.user)
                    fcm_tokens = [i.device_token for i in token_query if i.device_token!=""]
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    
                    # Update the related FbLeads instance to mark it as 'Dump'
                    fb_lead_instance = lead_edit_instance.fb_leads
                    fb_lead_instance.dump_lead = True
                    fb_lead_instance.save()

                    return Response({
                        'message': 'Lead Edit with dump lead updated successfully',
                        'data': serializer.data
                    })
            
                elif status_lead_instance.status_lead.lower() == 'site visit':
                        # Update the LeadEdit instance
                        mutable_data = request.data.copy()
                        mutable_data['site_visits'] = lead_edit_instance.site_visits + 1
                        serializer = LeadEditSerializer(instance=lead_edit_instance, data=mutable_data, partial=True)
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                        
                        # Update the related FbLeads instance to mark it as 'Site Visit'
                        fb_lead_instance = lead_edit_instance.fb_leads
                        fb_lead_instance.site_visit = True
                        fb_lead_instance.save()

                elif status_lead_instance.status_lead.lower() == 'booked':
                        # Update the LeadEdit instance
                        serializer = LeadEditSerializer(instance=lead_edit_instance, data=request.data, partial=True)
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                        
                        # Update the related FbLeads instance to mark it as 'Site Visit'
                        fb_lead_instance = lead_edit_instance.fb_leads
                        fb_lead_instance.booked = True
                        fb_lead_instance.save()

                        return Response({
                            'message': 'Lead Edit with site visit updated successfully',
                            'data': serializer.data
                        })
                elif status_lead_instance.status_lead.lower() == 'corporate visit':
                        # Update the LeadEdit instance
                        serializer = LeadEditSerializer(instance=lead_edit_instance, data=request.data, partial=True)
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                        
                        # Update the related FbLeads instance to mark it as 'Site Visit'
                        fb_lead_instance = lead_edit_instance.fb_leads
                        fb_lead_instance.corporate_visit = True
                        fb_lead_instance.save()

                        return Response({
                            'message': 'Lead Edit with site visit updated successfully',
                            'data': serializer.data
                        })

                elif status_lead_instance.status_lead.lower() == 'intersted':
                        # Update the LeadEdit instance
                        serializer = LeadEditSerializer(instance=lead_edit_instance, data=request.data, partial=True)
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                        
                        # Update the related FbLeads instance to mark it as 'Site Visit'
                        fb_lead_instance = lead_edit_instance.fb_leads
                        fb_lead_instance.intersted = True
                        fb_lead_instance.save()

                        return Response({
                            'message': 'Lead Edit with intersted updated successfully',
                            'data': serializer.data
                        })
                notification_data = {"sent_to":current_user.id, "head":request.data['fb_leads'].full_name, "message":f"Next scheduled at {request.data['next_schedule_date']} for {request.data['next_schedule_mode']}, Lead ID:{mutable_data['fb_leads']}"}
                notiserializer = NotificationStoreSerializer(data=notification_data)
                if notiserializer.is_valid():
                    notiserializer.save()
                try:
                    sendPush(request.data['fb_leads'].full_name, f"Next scheduled at {request.data['next_schedule_date']} for {request.data['next_schedule_mode']}, Lead ID:{mutable_data['fb_leads']}", fcm_tokens)
                except Exception as e:
                    print("Error while sending push notification",e)
            else:
                serializer = LeadEditSerializer(instance=lead_edit_instance, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                
                return Response({
                    'message': 'Lead Edit updated successfully',
                    'data': serializer.data
                })

        except LeadEdit.DoesNotExist:
            return Response({'message': 'Lead Edit not found'}, status=status.HTTP_404_NOT_FOUND)
    def delete(self, request, pk, format=None):
        LeadEdit_to_delete =  LeadEdit.objects.get(pk=pk)

            # delete the todo
        LeadEdit_to_delete.delete()

        return Response({
            'message': 'Lead Edit upated Successfully',
        })


# ALl dump lead
class FbDumpViewAPIView(APIView):
    permission_classes = [IsAuthenticated,]
    def get_object(self, pk):
        try:
            return FbLeads.objects.get(pk=pk)
        except FbLeads.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
        
        if pk:
            data = self.get_object(pk)
            serializer = FbLeadSerializer(data)
            return Response(serializer.data)

        else:
            data = FbLeads.objects.filter(dump_lead=True, assigned_to=request.user).order_by('-created_at')
            serializer = FbLeadSerializer(data, many=True)

            return Response(serializer.data)

class FbSiteVisitViewAPIView(APIView):
    permission_classes = [IsAuthenticated,]
    def get_object(self, pk):
        try:
            return FbLeads.objects.get(pk=pk)
        except FbLeads.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
        paginator = CommonPagination()
        
        if pk:
            data = self.get_object(pk)
            serializer = FbLeadSerializer(data)
            return Response(serializer.data)

        else:
            data = FbLeads.objects.filter(
                Q(site_visit=True),
                Q(leadedit__visited_by=request.user) | Q(assigned_to=request.user)
            ).order_by('-created_at')
            if  'page' in request.query_params:

                result_page = paginator.paginate_queryset(data, request)
                serializer = FbLeadSerializer(result_page, many=True)
                return paginator.get_paginated_response(serializer.data)
            else:
                serializer = FbLeadSerializer(data, many=True)
                return Response(serializer.data)
        


# Reason for site update
        
class ReasonSiteUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated,]
    def get_object(self, pk):
        try:
            return ReasonSiteVisit.objects.get(pk=pk)
        except ReasonSiteVisit.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
        # dump = self.request.query_params.get('Dump')
        # site_visit = self.request.query_params.get('site_visit')
        # booked = self.request.query_params.get('Booked')

        if pk:
            data = self.get_object(pk)
            serializer = ReasonSiteVisitSerializer(data)
            return Response(serializer.data)

        else:
            data = ReasonSiteVisit.objects.all().order_by('-created_at')
            # if dump == 'True':
            #         queryset = queryset.filter(dump=True)
            # if site_visit == 'True':
            #     queryset = queryset.filter(site_visit=True)

            # if booked == 'True':
            #     queryset = queryset.filter(booked=True)
            serializer = ReasonSiteVisitSerializer(data, many=True)

            return Response(serializer.data)
    
    
    def post(self, request):
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            
            serializer = ReasonSiteVisitSerializer(data=mutable_data)

            # Check if the data passed is valid
            print()
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Return Response to User

            response = Response()

            response.data = {
                'message': 'Reason Site Visit Created Successfully',
                'data': serializer.data
            }
            return response
    
    def patch(self, request, pk=None, format=None):
                # Get the todo to update
            ReasonSiteVisit_to_update = ReasonSiteVisit.objects.get(pk=pk)
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            # request.data['user'] = request.user.id

            serializer = ReasonSiteVisitSerializer(instance=ReasonSiteVisit_to_update,data=mutable_data, partial=True)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = Response()

            response.data = {
                'message': 'Feed Back upated Successfully',
                'data': serializer.data
            }

            return response
    def delete(self, request, pk, format=None):
        ReasonSiteVisit_to_delete =  ReasonSiteVisit.objects.get(pk=pk)

            # delete the todo
        ReasonSiteVisit_to_delete.delete()

        return Response({
            'message': 'Reason Site Visit upated Successfully',
        })
    
# Don't change this api until you have a change in data from Zapier
class FBleadsZap(APIView):
    permission_classes = [AllowAny]

    def get_last(self):
        query = FbLeads.objects.all().last()
        users = User.objects.filter(sales_employee=True, assign=True)
        users_on_leave = UserHoliday.objects.filter(Q(from_date__lte=datetime.now()),Q(to_date__gte=datetime.now())).values('user')
        user_holiday_user_ids = {user_holiday['user'] for user_holiday in users_on_leave}
        if query:
            query = query.assigned_to
            if query:
                rearrange_idx = 0
                for idx in range(len(users)):
                    if users[idx].pk==query.pk:
                        if len(users)-1>idx:
                            rearrange_idx = idx
                        else:
                            rearrange_idx = 0
                        break
                users = users[rearrange_idx+1:] + users[:rearrange_idx+1]
        users_list = []
        for idx in range(len(users)):
            if users[idx].pk not in user_holiday_user_ids:
                users_list.append(users[idx])

        return users_list

    def post(self, request):
        users = self.get_last()
        new_leads = request.data.copy()
        count = 0
        assigned_users = []
        notification_data = []
        medium = MediumOfLead.objects.get(medium='Digital Marketing')
        lead_source = LeadSource.objects.get(lead_source='Facebook')
        if type(new_leads)!=list:
            new_leads = [new_leads]
        for i in new_leads:
            i['lead_source'] = lead_source.pk
            i['by_medium'] = medium.pk
            i['fb_from'] = 'Park'
            old_leads = FbLeads.objects.filter(phone_number=i['phone_number'])
            if len(old_leads) > 0:
                assigned_user = old_leads.last().assigned_to
                old_leads.update(dump_lead=False)
                i['assigned_to'] = assigned_user
                if assigned_user in users:
                    users.remove(assigned_user)
                users.append(assigned_user)
            else:
                i['assigned_to'] = users[count].pk
                count+=1

            if i['assigned_to'] not in assigned_users  and i['assigned_to']:
                assigned_users.append(i['assigned_to'])
                # send notifications to the assignee and manager of the assignee
                notification_data.append({"sent_to":i['assigned_to'], "head":"New Lead: Park", "message":"New lead has been assigned to you."})
            if count==len(users):
                count=0

        token_query = FCMTokens.objects.filter(user__in=assigned_users)
        fcm_tokens = [i.device_token for i in token_query if i.device_token!=""]

        notiserializer = NotificationStoreSerializer(data=notification_data, many=True)
        if notiserializer.is_valid():
            notiserializer.save()
        try:
            sendPush("New Lead: Park", "New lead has been assigned to you.", fcm_tokens)
        except Exception as e:
            print("Error while sending push notification",e)

        if type(new_leads)==list:
            serializer = FbLeadPostSerializer(data=new_leads, many=True)
        else:
            serializer = FbLeadPostSerializer(data=new_leads)
        if serializer.is_valid():
            serializer.save()
        else:
            print(serializer.errors)        
        return Response({'data':"Uploaded successfully", "status":200})

class FBleadsZap2(APIView):
    permission_classes = [AllowAny]

    def get_last(self):
        query = FbLeads.objects.all().last()
        users = User.objects.filter(sales_employee=True, assign=True)
        users_on_leave = UserHoliday.objects.filter(Q(from_date__lte=datetime.now()),Q(to_date__gte=datetime.now())).values('user')
        user_holiday_user_ids = {user_holiday['user'] for user_holiday in users_on_leave}
        if query:
            query = query.assigned_to
            if query:
                rearrange_idx = 0
                for idx in range(len(users)):
                    if users[idx].pk==query.pk:
                        if len(users)-1>idx:
                            rearrange_idx = idx
                        else:
                            rearrange_idx = 0
                        break
                users = users[rearrange_idx+1:] + users[:rearrange_idx+1]
        users_list = []
        for idx in range(len(users)):
            if users[idx].pk not in user_holiday_user_ids:
                users_list.append(users[idx])

        return users_list

    def post(self, request):
        users = self.get_last()
        new_leads = request.data.copy()
        count = 0
        assigned_users = []
        notification_data = []
        medium = MediumOfLead.objects.get(medium='Digital Marketing')
        lead_source = LeadSource.objects.get(lead_source='Facebook')
        if type(new_leads)!=list:
            new_leads = [new_leads]
        for i in new_leads:
            i['lead_source'] = lead_source.pk
            i['by_medium'] = medium.pk
            i['fb_from'] = 'CI Grand'
            old_leads = FbLeads.objects.filter(phone_number=i['phone_number'])
            if len(old_leads) > 0:
                assigned_user = old_leads.last().assigned_to
                old_leads.update(dump_lead=False)
                i['assigned_to'] = assigned_user
                if assigned_user in users:
                    users.remove(assigned_user)
                users.append(assigned_user)
            else:
                i['assigned_to'] = users[count].pk
                count+=1

            if i['assigned_to'] not in assigned_users and i['assigned_to']:
                assigned_users.append(i['assigned_to'])
                # send notifications to the assignee and manager of the assignee
                notification_data.append({"sent_to":i['assigned_to'], "head":"New Lead: CI Grand", "message":"New lead has been assigned to you."})
            if count==len(users):
                count=0

        token_query = FCMTokens.objects.filter(user__in=assigned_users)
        fcm_tokens = [i.device_token for i in token_query if i.device_token!=""]

        notiserializer = NotificationStoreSerializer(data=notification_data, many=True)
        if notiserializer.is_valid():
            notiserializer.save()
        try:
            sendPush("New Lead: CI Grand", "New lead has been assigned to you.", fcm_tokens)
        except Exception as e:
            print("Error while sending push notification",e)

        if type(new_leads)==list:
            serializer = FbLeadPostSerializer(data=new_leads, many=True)
        else:
            serializer = FbLeadPostSerializer(data=new_leads)
        if serializer.is_valid():
            serializer.save()
        else:
            print(serializer.errors) 
        
        return Response({'data':"Uploaded successfully", "status":200})    

class ShowNotificationAPIview(APIView):
    permission_classes = [IsAuthenticated,]
    def get(self, request, pk=None, format=None):
        if pk:
            data = self.get_object(pk)
            serializer = NotificationStoreSerializer(data)
            return Response(serializer.data)

        else:
            data = NotificationStore.objects.filter(sent_to=request.user, seen=False).order_by('-created_at')
            serializer = NotificationStoreSerializer(data, many=True)

            return Response(serializer.data)
        
class ReassignDumpleads(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.admin:
            leads = FbLeads.objects.filter(pk__in=request.data['lead_id'])
            responses = []
            for lead in leads:
                old_assign = lead.assigned_to
                if not (lead.dump_lead and lead.permanent_dump_lead):
                    lead.dump_lead = False
                    lead.permanent_dump_lead = True
                    lead.assigned_to = User.objects.get(id=request.data['assign_to'])
                    lead.updated_at = timezone.now()
                    lead.save()
                    responses.append({"message":"Successfully reassigned dumped lead "+str(lead.pk)+" to "+str(lead.assigned_to)})
                    mutable_data = {
                        "user":request.user.id,
                        "fb_leads":lead.id,
                        "description":f"This dump lead has been transferred from {old_assign.name} to {lead.assigned_to.name}."
                    }
                    serializer = LeadEditSerializer(data=mutable_data)
                    if serializer.is_valid():
                        serializer.save()
                    
                    notification_data = {"sent_to":request.data['assign_to'], "head":f"Dump Lead: {lead.full_name}", "message":f"Dump lead has been assigned to you. Lead ID:{lead.id}"}
                    notiserializer = NotificationStoreSerializer(data=notification_data)
                    if notiserializer.is_valid():
                        notiserializer.save()
                    token_query = FCMTokens.objects.filter(user__in=lead.assigned_to)
                    fcm_tokens = [i.device_token for i in token_query if i.device_token!=""]
                    try:
                        sendPush(f"Dump Lead: {lead.full_name}", "Dump lead has been assigned to you.", fcm_tokens)
                    except Exception as e:
                        print("Error while sending push notification",e)
                # return Response({'data':'Reassigned successfully', 'status':200})
                else:
                    responses.append({"message":"Failed to reassigned dumped lead "+str(lead.pk)})
            return Response(responses, status=200)
             
        else:
            return Response({"data":"You don't have permission to edit it."}, status=403)

# class AgentSiteVisits(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         # Aggregate the leads by site_visits and count them
#         sitevisit_counts = LeadEdit.objects.values('site_visits').annotate(count=Count('id'))

#         # Prepare the response data
#         sitevisit_list = {}
#         for item in sitevisit_counts:
#             site_visits = item['site_visits']
#             count = item['count']
#             lead_objs = LeadEdit.objects.filter(site_visits=site_visits)
#             serialized_leads = LeadEditSerializer(lead_objs, many=True).data

#             sitevisit_list[site_visits] = {
#                 "leads": serialized_leads,
#                 "count": count
#             }

#         return Response(sitevisit_list, status=200)


# class AgentSiteVisits(APIView):
#     permission_classes = [IsAuthenticated]
#     pagination_class = CommonPagination

#     def get(self, request):
#         # Check if a specific site_visits number and user_id are provided in the query parameters
#         site_visits_number = request.query_params.get('site_visits')
#         user_id = request.query_params.get('user_id')

#         if site_visits_number:
#             # Filter leads data for the specified site_visits number
#             leads_data = LeadEdit.objects.filter(status_of_lead__site_visits=site_visits_number)
#             if user_id:
#                 # Further filter by user_id if provided
#                 leads_data = leads_data.filter(user_id=user_id)

#             paginator = self.pagination_class()
#             paginated_leads = paginator.paginate_queryset(leads_data, request)
#             serialized_leads = LeadEditSerializer(paginated_leads, many=True).data

#             return paginator.get_paginated_response(serialized_leads)
#         else:
#             # Annotate each lead with the number of site visits
#             annotated_leads = LeadEdit.objects.filter(user_id=user_id).values('fb_leads').annotate(site_visits_count=Count('id')) if user_id else LeadEdit.objects.values('fb_leads').annotate(site_visits_count=Count('id'))

#             # Aggregate the annotated leads by the number of site visits
#             visit_counts = {}
#             for lead in annotated_leads:
#                 count = lead['site_visits_count']
#                 if count in visit_counts:
#                     visit_counts[count] += 1
#                 else:
#                     visit_counts[count] = 1

#             # Prepare the response data
#             sitevisit_list = []
#             for count, num_leads in visit_counts.items():
#                 sitevisit_list.append({
#                     "site_visits": count,
#                     "count": num_leads
#                 })

#             return Response(sitevisit_list, status=200)
        

class AgentSiteVisits(APIView):
    permission_classes = [IsAuthenticated]

    # def get(self, request):
    #     # Get query parameters
    #     user_id = request.query_params.get('user_id')

    #     # Define base queryset with a date filter
    #     date_cutoff = datetime(2024, 6, 1)
    #     base_queryset = LeadEdit.objects.filter(
    #         status_of_lead__status_lead='Site Visit',
    #         created_at__gte=date_cutoff
    #     )

    #     # Filter by user_id if provided
    #     if user_id:
    #         base_queryset = base_queryset.filter(user=user_id)

    #     # Aggregate the leads by site_visits and count them
    #     sitevisit_counts = base_queryset.values('site_visits').annotate(count=Count('id')).order_by('site_visits')

    #     # Prepare the response data
    #     sitevisit_list = []
    #     for item in sitevisit_counts:
    #         site_visits = item['site_visits']
    #         count = item['count']

    #         sitevisit_list.append({
    #             "site_visits": site_visits,
    #             "count": count
    #         })

    #     return Response(sitevisit_list, status=200)

    def get(self, request):
            # Get query parameters
        assigned_to__id = request.query_params.get('user_id')

        base_queryset = FbLeads.objects.filter(site_visit=True)
        if assigned_to__id:
            base_queryset = base_queryset.filter(assigned_to__id=assigned_to__id)

        # Aggregate the leads by site_visits and count them
        sitevisit_counts = base_queryset.values('site_visit').annotate(count=Count('id')).order_by('site_visit')

        # If no data is available, return 0
        if not sitevisit_counts:
            return Response([{"site_visits": 0, "count": 0}], status=200)

        # Prepare the response data
        sitevisit_list = {}
        for item in sitevisit_counts:
            site_visits = item['site_visit']
            count = item['count']
            if count in sitevisit_list:
                sitevisit_list[count]+=1
            else:
                sitevisit_list[count]=1
        sitevisit_list = [{"count": k, "site_visits": v} for k,v in sitevisit_list.items()]
        return Response(sitevisit_list, status=200)



class AgentSiteVisitsForFbLead(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CommonPagination

    def get(self, request):
        # Get query parameters
        user_id = request.query_params.get('user_id')
        site_visit = request.query_params.get('site_visits')

        # Define base queryset
        # date_cutoff = datetime(2024, 6, 1)
        base_queryset = LeadEdit.objects.all().order_by("-created_at")

        # Filter by user_id if provided
        if user_id:
            base_queryset = base_queryset.filter(user=user_id)

        # Filter for 'Site Visit' status
        site_visit_queryset = base_queryset.filter(status_of_lead__status_lead='Site Visit')

        # Aggregate the leads by site_visits and count them
        sitevisit_counts = site_visit_queryset.values('fb_leads').annotate(count=Count('id')).order_by('status_of_lead__status_lead')

        # Prepare the response data
        sitevisit_list = []
        for item in sitevisit_counts:
            lead = FbLeads.objects.get(pk=item['fb_leads'])
            count = item['count']
            if count==int(site_visit):
                ser = FbLeadSerializer(lead)
                sitevisit_list.append(ser.data)
        
        paginator = self.pagination_class()
        paginated_fb_leads = paginator.paginate_queryset(sitevisit_list, request)
        return paginator.get_paginated_response(paginated_fb_leads)


class CheckScheduled(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        today = timezone.now().date()
        # Subquery to get the latest updated_at for each fb_leads
        latest_updated_at_subquery = LeadEdit.objects.filter(fb_leads=OuterRef('fb_leads')).values('fb_leads').annotate(latest_updated_at=Max('updated_at')).values('latest_updated_at')

        # Filter LeadEdit entries scheduled for today and are the latest for their fb_leads
        leads = LeadEdit.objects.annotate(
            latest_update=Subquery(latest_updated_at_subquery)
        ).filter(
            Q(next_schedule_date=today) & Q(updated_at=F('latest_update'))
        )
        # print(leads)
        # leads = LeadEdit.objects.filter(next_schedule_date=today)
        # count = 0
        # count2 = 0
        for lead in leads:
            mode = lead.next_schedule_mode
            # Ensure the mode exists and that mode_lead is not None
            if mode and mode.mode_lead is not None:
                existing_noti = NotificationStore.objects.filter(
                    created_at__date=today, 
                    message__icontains=lead.fb_leads.id
                )
            # existing_noti = NotificationStore.objects.filter(created_at__date=today, message__icontains=lead.fb_leads.id)
            if existing_noti.exists():
                # count += 1
                continue
            # count2 += 1
            token_query = FCMTokens.objects.filter(user=lead.fb_leads.assigned_to)
            fcm_tokens = [i.device_token for i in token_query if i.device_token!=""]

            if lead and lead.fb_leads and mode:
            # Also check if mode_lead attribute exists and is not None
                notification_data = {"sent_to":lead.fb_leads.assigned_to.id, "head":lead.fb_leads.full_name, "message":f"Lead is scheduled for today for {mode.mode_lead}, with Lead ID:{lead.fb_leads.id}"}
                notiserializer = NotificationStoreSerializer(data=notification_data)
                if notiserializer.is_valid():
                    notiserializer.save()
                try:
                    sendPush(lead.fb_leads.full_name, f"Lead is scheduled for today for {mode.mode_lead}, with Lead ID:{lead.fb_leads.id}", fcm_tokens)
                except Exception as e:
                    print("Error while sending push notification",e)
            # return Response("Notified Users", status=200)
        return Response({"data":LeadEditSerializer(leads, many=True).data,"count":len(leads)})

class AgentLeadSouce(APIView):
    permission_classes = [IsAuthenticated]

    # def get(self, request):
    #     user = request.query_params.get('user')
    #     if user is None or user == '':
    #         query = FbLeads.objects.all()
    #     else:
    #         query = FbLeads.objects.filter(assigned_to=user)
    #     leads_count = {}
    #     for i in query:
    #         if i.assigned_to:
    #             if  i.assigned_to.name not in leads_count:
    #                 if i.by_medium:
    #                     leads_count[i.assigned_to.name] = {i.by_medium.medium :1}
    #                 else:
    #                     leads_count[i.assigned_to.name] = {"N/A" :1}

    #             else:
    #                 if i.by_medium:
    #                     if  i.by_medium.medium not in leads_count[i.assigned_to.name]:
    #                         leads_count[i.assigned_to.name][i.by_medium.medium]=1
    #                     else:
    #                         leads_count[i.assigned_to.name][i.by_medium.medium]+=1
    #                 else:
    #                     if 'N/A' not in leads_count[i.assigned_to.name]:
    #                         leads_count[i.assigned_to.name]["N/A"] =1
    #                     else:
    #                         leads_count[i.assigned_to.name]["N/A"]+=1
            
    #     return Response(leads_count, status=200)

    def get(self, request):
        try:
            # Get query parameters
            user_id = request.query_params.get('user')

            # Define date cutoff
            date_cutoff = datetime(2024, 6, 1)

            # Get all users
            all_users = User.objects.all()

            # Initialize leads_count dictionary with default value as 0
            leads_count = {}

            # Populate the dictionary with 0 counts for all users
            for user in all_users:
                leads_count[user.name] = {}

            # Define base queryset with a date filter
            if user_id is None or user_id == '':
                query = FbLeads.objects.filter(created_at__gte=date_cutoff)
            else:
                query = FbLeads.objects.filter(assigned_to=user_id, created_at__gte=date_cutoff)

            # Annotate the query with counts grouped by assigned user and medium
            annotated_query = query.values('assigned_to__name', 'by_medium__medium').annotate(count=Count('id')).order_by('assigned_to__name')

            # Update counts based on available data
            for lead in annotated_query:
                user_name = lead['assigned_to__name']
                medium = lead['by_medium__medium'] if lead['by_medium__medium'] else "N/A"
                count = lead['count']

                if medium not in leads_count[user_name]:
                    leads_count[user_name][medium] = count
                else:
                    leads_count[user_name][medium] += count

            return Response(leads_count, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class acers99Leads(APIView):
    permission_classes = [AllowAny]

    def get_last(self):
        query = FbLeads.objects.all().last()
        users = User.objects.filter(sales_employee=True, assign=True)
        users_on_leave = UserHoliday.objects.filter(Q(from_date__lte=datetime.now()),Q(to_date__gte=datetime.now())).values('user')
        user_holiday_user_ids = {user_holiday['user'] for user_holiday in users_on_leave}
        if query:
            query = query.assigned_to
            rearrange_idx = 0
            for idx in range(len(users)):
                if users[idx].pk==query.pk:
                    if len(users)-1>idx:
                        rearrange_idx = idx
                    else:
                        rearrange_idx = 0
                    break
            users = users[rearrange_idx+1:] + users[:rearrange_idx+1]
        users_list = []
        for idx in range(len(users)):
            if users[idx].pk not in user_holiday_user_ids:
                users_list.append(users[idx])

        return users_list

    def post(self, request):
        users = self.get_last()
        new_leads = request.data.copy()
        count = 0
        assigned_users = []
        notification_data = []
        medium = MediumOfLead.objects.get(medium='Digital Marketing')
        lead_source = LeadSource.objects.get(lead_source='99acers')
        for i in new_leads:
            old_leads = FbLeads.objects.filter(phone_number=i['phone_number'])
            i['lead_source'] = lead_source.pk
            i['by_medium'] = medium.pk
            if len(old_leads) > 0:
                assigned_user = old_leads.last().assigned_to
                old_leads.update(dump_lead=False)
                i['assigned_to'] = assigned_user
                users.remove(assigned_user)
                users.append(assigned_user)
            else:
                i['assigned_to'] = users[count]
                count+=1

            if i['assigned_to'] not in assigned_users:
                assigned_users.append(i['assigned_to'].pk)
                # send notifications to the assignee and manager of the assignee
                notification_data.append({"sent_to":i['assigned_to'], "head":"New Lead: 99acers", "message":"New lead has been assigned to you."})
            if count==len(users):
                count=0

        token_query = FCMTokens.objects.filter(user__in=assigned_users)
        fcm_tokens = [i.device_token for i in token_query if i.device_token!=""]

        notiserializer = NotificationStoreSerializer(data=notification_data, many=True)
        if notiserializer.is_valid():
            notiserializer.save()
        try:
            sendPush("New Lead: 99acers", "New lead has been assigned to you.", fcm_tokens)
        except Exception as e:
            print("Error while sending push notification",e)

        if type(request.data)==list:
            serializer = FBleads99(data=request.data, many=True)
        else:
            serializer = FBleads99(data=request.data)
        if serializer.is_valid():
            serializer.save()
        
        return Response({'data':serializer.data, "status":200})

class HomeOnlineLeads(APIView):
    permission_classes = [AllowAny]

    def get_last(self):
        query = FbLeads.objects.all().last()
        users = User.objects.filter(sales_employee=True, assign=True)
        users_on_leave = UserHoliday.objects.filter(Q(from_date__lte=datetime.now()),Q(to_date__gte=datetime.now())).values('user')
        user_holiday_user_ids = {user_holiday['user'] for user_holiday in users_on_leave}
        if query:
            query = query.assigned_to
            rearrange_idx = 0
            for idx in range(len(users)):
                if users[idx].pk==query.pk:
                    if len(users)-1>idx:
                        rearrange_idx = idx
                    else:
                        rearrange_idx = 0
                    break
            users = users[rearrange_idx+1:] + users[:rearrange_idx+1]
        users_list = []
        for idx in range(len(users)):
            if users[idx].pk not in user_holiday_user_ids:
                users_list.append(users[idx])

        return users_list

    def post(self, request):
        users = self.get_last()
        new_leads = request.data.copy()
        count = 0
        assigned_users = []
        notification_data = []
        medium = MediumOfLead.objects.get(medium='Digital Marketing')
        lead_source = LeadSource.objects.get(lead_source='Home Online')
        for i in new_leads:
            i['lead_source'] = lead_source.pk
            i['by_medium'] = medium.pk
            old_leads = FbLeads.objects.filter(phone_number=i['phone_number'])
            if len(old_leads) > 0:
                assigned_user = old_leads.last().assigned_to
                old_leads.update(dump_lead=False)
                i['assigned_to'] = assigned_user
                users.remove(assigned_user)
                users.append(assigned_user)
            else:
                i['assigned_to'] = users[count]
                count+=1

            if i['assigned_to'] not in assigned_users:
                assigned_users.append(i['assigned_to'].pk)
                # send notifications to the assignee and manager of the assignee
                notification_data.append({"sent_to":i['assigned_to'], "head":"New Lead: Home", "message":"New lead has been assigned to you."})
            if count==len(users):
                count=0

        token_query = FCMTokens.objects.filter(user__in=assigned_users)
        fcm_tokens = [i.device_token for i in token_query if i.device_token!=""]

        notiserializer = NotificationStoreSerializer(data=notification_data, many=True)
        if notiserializer.is_valid():
            notiserializer.save()
        try:
            sendPush("New Lead: Home", "New lead has been assigned to you.", fcm_tokens)
        except Exception as e:
            print("Error while sending push notification",e)

        if type(request.data)==list:
            serializer = FBleadsHomeonline(data=request.data, many=True)
        else:
            serializer = FBleadsHomeonline(data=request.data)
        if serializer.is_valid():
            serializer.save()
        
        return Response({'data':serializer.data, "status":200})

class HousingLeads(APIView):
    permission_classes = [AllowAny]

    def get_last(self):
        query = FbLeads.objects.all().last()
        users = User.objects.filter(sales_employee=True, assign=True)
        users_on_leave = UserHoliday.objects.filter(Q(from_date__lte=datetime.now()),Q(to_date__gte=datetime.now())).values('user')
        user_holiday_user_ids = {user_holiday['user'] for user_holiday in users_on_leave}
        if query:
            query = query.assigned_to
            rearrange_idx = 0
            for idx in range(len(users)):
                if users[idx].pk==query.pk:
                    if len(users)-1>idx:
                        rearrange_idx = idx
                    else:
                        rearrange_idx = 0
                    break
            users = users[rearrange_idx+1:] + users[:rearrange_idx+1]
        users_list = []
        for idx in range(len(users)):
            if users[idx].pk not in user_holiday_user_ids:
                users_list.append(users[idx])

        return users_list

    def post(self, request):
        users = self.get_last()
        new_leads = request.data.copy()
        count = 0
        assigned_users = []
        notification_data = []
        medium = MediumOfLead.objects.get(medium='Digital Marketing')
        lead_source = LeadSource.objects.get(lead_source='Housing')
        for i in new_leads:
            old_leads = FbLeads.objects.filter(phone_number=i['phone_number'])
            i['lead_source'] = lead_source.pk
            i['by_medium'] = medium.pk
            if len(old_leads) > 0:
                assigned_user = old_leads.last().assigned_to
                old_leads.update(dump_lead=False)
                i['assigned_to'] = assigned_user
                users.remove(assigned_user)
                users.append(assigned_user)
            else:
                i['assigned_to'] = users[count]
                count+=1

            if i['assigned_to'] not in assigned_users:
                assigned_users.append(i['assigned_to'].pk)
                # send notifications to the assignee and manager of the assignee
                notification_data.append({"sent_to":i['assigned_to'], "head":"New Lead: Hosuing", "message":"New lead has been assigned to you."})
            if count==len(users):
                count=0

        token_query = FCMTokens.objects.filter(user__in=assigned_users)
        fcm_tokens = [i.device_token for i in token_query if i.device_token!=""]

        notiserializer = NotificationStoreSerializer(data=notification_data, many=True)
        if notiserializer.is_valid():
            notiserializer.save()
        try:
            sendPush("New Lead: Hosuing", "New lead has been assigned to you.", fcm_tokens)
        except Exception as e:
            print("Error while sending push notification",e)

        if type(request.data)==list:
            serializer = FBleadsHousing(data=request.data, many=True)
        else:
            serializer = FBleadsHousing(data=request.data)
        if serializer.is_valid():
            serializer.save()
        
        return Response({'data':serializer.data, "status":200})
    

class FbLeadAPIviewDelete(APIView):
    permission_classes = [AllowAny]
    def delete(self, request, pk, format=None):
        ReasonSiteVisit_to_delete =  FbLeads.objects.all()

            # delete the todo
        ReasonSiteVisit_to_delete.delete()

        return Response({
            'message': 'Lead delete Successfully',
        })
    


class SiteVisitCountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        fb_lead_id = request.query_params.get('fb_lead_id')

        if not fb_lead_id:
            return Response({'detail': 'fb_lead_id is required.'}, status=400)

        # Filter LeadEdit objects by the given fb_lead_id
        lead_edits = LeadEdit.objects.filter(fb_leads=fb_lead_id, mode__mode_lead__in=['Site visit', 'Re-Visit'])
       

        if not lead_edits.exists():
            return Response({'detail': 'No site visits found for the given fb_lead_id.'}, status=404)

        # Count the total number of site visits
        site_visit_count = lead_edits.count()

        # Calculate the next site visit count
        next_site_visit_count = site_visit_count + 1

        # Prepare the response data
        response_data = {
            'current_site_visit_count': site_visit_count,
            'next_site_visit_count': next_site_visit_count
        }

        return Response(response_data, status=200)



class DumpLeadsCount(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get all users
        users = User.objects.filter(sales_employee=True)

        # List to store user details and corresponding dump leads count
        dump_leads_counts = []

        # Count dump leads for each user
        for user in users:
            dump_leads_count = FbLeads.objects.filter(assigned_to=user, dump_lead=True,).count()
            dump_leads_counts.append({
                'user_id': user.id,
                'user_name': user.name,
                'dump_leads_count': dump_leads_count
            })

        # Sort the dump leads counts list by the count
        sorted_dump_leads_counts = sorted(dump_leads_counts, key=itemgetter('dump_leads_count'))

        return Response(sorted_dump_leads_counts, status=200)

class PendingTasks(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get all users
        leads = FbLeads.objects.filter(assigned_to=request.user)
        data = []
        for lead in leads:
            lead_edit = LeadEdit.objects.filter(fb_leads=lead)
            if len(lead_edit)>0:
                lead_edit = lead_edit.last()
                if lead_edit.status_of_lead.status_lead.lower() not in ['booked','dump']:
                    data.append(LeadEditSerializer(lead_edit).data)
        
        return Response({"data":data,"count":len(data)}, status=200)
    
class ModifyStatus(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get the lead id from the request

        status_lead_instance = StatusLead.objects.get(pk=request.data['status'])
        data = []
        if type(request.data['id'])==list:
            lead_ids = request.data['id']
            leads = FbLeads.objects.filter(id__in=lead_ids)

        elif type(request.data['id'])==str:
            leads = FbLeads.objects.filter(dump_lead=False, booked=False)
            full_name = request.data.get('full_name')
            assigned_user = request.data.get('assigned_to_name')
            created_at_gte = request.data.get('created_at_gte')
            created_at_lte = request.data.get('created_at_lte')
            phone_number = request.data.get('phone_number')
            project_name = request.data.get('project_name')
            agent_name = request.data.get('agent_name')
            project_type_name = request.data.get('project_type_name')
            lead_source = request.data.get('lead_source')
            description = request.data.get('description')
            status_of_lead_warm_hot_cold = request.data.get('status_of_lead_warm_hot_cold')
            status_of_lead = request.data.get('status_of_lead')
            expected_booking = request.data.get('expected_booking')
            feedback = request.data.get('feedback')
            re_assigned = request.data.get('re_assigned')
            lead_edits = LeadEdit.objects.all()

            if description:
                lead_edits = lead_edits.filter(description__icontains=description)
            # if status_of_lead:
            #     lead_edits = lead_edits.filter(status_of_lead__status_lead__exact=status_of_lead)

            if status_of_lead:
                latest_lead_edit_subquery = LeadEdit.objects.filter(
                    fb_leads=OuterRef('fb_leads')
                ).order_by('-created_at').values('pk')[:1]

                lead_edits = lead_edits.filter(
                    pk__in=Subquery(latest_lead_edit_subquery),
                    status_of_lead__status_lead__exact=status_of_lead
                )
            if status_of_lead_warm_hot_cold:
                latest_lead_edit_subquery = LeadEdit.objects.filter(
                    fb_leads=OuterRef('fb_leads')
                ).order_by('-created_at').values('pk')[:1]

                lead_edits = lead_edits.filter(
                    pk__in=Subquery(latest_lead_edit_subquery),
                    status_of_lead_warm_hot_cold__exact=status_of_lead_warm_hot_cold
                )
            if status_of_lead or status_of_lead_warm_hot_cold or description:
                fb_leads_ids = lead_edits.values_list('fb_leads_id', flat=True).distinct()

                leads = FbLeads.objects.filter(id__in=fb_leads_ids).exclude(Q(dump_lead=True)).order_by('-created_at')
            else:
                leads = FbLeads.objects.all().exclude(Q(dump_lead=True)).order_by('-created_at')
            if full_name:
                leads = leads.filter(full_name__icontains=full_name)
            if created_at_gte:
                try:
                    created_at_gte_parsed = parse(created_at_gte).date()
                    leads = leads.filter(created_at__gte=created_at_gte_parsed)
                except ValueError:
                    pass  # Handle invalid date format if needed
            if created_at_lte:
                try:
                    created_at_lte_parsed = parse(created_at_lte).date()
                    leads = leads.filter(created_at__lte=created_at_lte_parsed)
                except ValueError:
                    pass  # Handle invalid date format if needed
            if phone_number:
                leads = leads.filter(phone_number__icontains=phone_number)
            if assigned_user:
                leads = leads.filter(assigned_to__name__icontains=assigned_user)
            if project_name:
                leads = leads.filter(project_name__project_name__icontains=project_name)
            if agent_name:
                leads = leads.filter(user__name__exact=agent_name)
            if project_type_name:
                leads = leads.filter(project_type_name__property_type__exact=project_type_name)
            if lead_source:
                leads = leads.filter(lead_source__lead_source__exact=lead_source)
            if feedback:
                leads = leads.filter(feedback__icontains=feedback)
            if expected_booking:
                leads = leads.filter(expected_booking=expected_booking)
            if re_assigned:
                leads = leads.filter(dump_lead=False, permanent_dump_lead=True)

        else:
            return Response({"message":"Invalid lead ids."}, status=status.HTTP_400_BAD_REQUEST)
        
        for lead in leads:
            data1 = {"fb_leads":lead.id, "status_of_lead":request.data['status']}
            dicussion = LeadEdit.objects.filter(fb_leads=lead).last()
            try:
                try:
                    data1['description'] = f"The status for this lead has been changed from {dicussion.status_of_lead.status_lead} to {status_lead_instance.status_lead}" 
                except:
                    data1['description'] = f"The status for this lead has been changed to {status_lead_instance.status_lead}" 
                data1['user'] = request.user.id
                data.append(data1)

                if status_lead_instance.status_lead.lower() == 'dump':
                    lead.dump_lead = True
                    lead.updated_at = timezone.now()
                    lead.save()

                elif status_lead_instance.status_lead.lower() == 'call not received':
                    lead.call_not_recevied = True
                    lead.updated_at = timezone.now()
                    lead.save()

                elif status_lead_instance.status_lead.lower() == 'in process':
                    lead.intersted = True
                    lead.updated_at = timezone.now()
                    lead.save()

                elif status_lead_instance.status_lead.lower() == 'good lead':
                    lead.good_lead = True
                    lead.updated_at = timezone.now()
                    lead.save()

                elif status_lead_instance.status_lead.lower() == 'poor lead':
                    lead.poor_lead = True
                    lead.updated_at = timezone.now()
                    lead.save()

                else:
                    pass

                noti_instance = NotificationStore.objects.filter(head=lead.full_name,message__icontains=f"Lead ID:{lead.id}")
                noti_instance.update(seen=True)
                if status_lead_instance.status_lead.lower() != 'dump':
                    token_query = FCMTokens.objects.filter(user=lead.assigned_to)
                    fcm_tokens = [i.device_token for i in token_query if i.device_token!=""]

                    notification_data = {"sent_to":lead.assigned_to.id, "head":lead.full_name, "message":f"The status for this lead has been changed from {dicussion.status_of_lead.status_lead} to {status_lead_instance.status_lead}, with Lead ID:{lead.id}"}
                    notiserializer = NotificationStoreSerializer(data=notification_data)
                    if notiserializer.is_valid():
                        notiserializer.save()
                    try:
                        sendPush(lead.full_name, f"The status for this lead has been changed from {dicussion.status_of_lead.status_lead} to {status_lead_instance.status_lead}, with Lead ID:{lead.id}", fcm_tokens)
                    except Exception as e:
                        print("Error while sending push notification",e)
            except Exception as e:
                print(lead)
                print(e)
        serializer = LeadEditSerializer(data=data, many=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        return Response({"message":"Status updated successfully.", "data":serializer.data}, status=status.HTTP_200_OK)
