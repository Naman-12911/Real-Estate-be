from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from social.models import FbLeads,LeadEdit, NotificationStore, StatusLead
from social.serializer import LeadEditSerializer, FbLeadPostSerializer, NotificationStoreSerializer, FbLeadSerializer
from .serializer import FileUploadSerializer
import pandas as pd
import numpy as np
from account.models import User
# from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
import time
from datetime import datetime, date

class FileUploadView(APIView):
    permission_classes = [AllowAny]
    serializer_class = FileUploadSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            if file.name.endswith(('.xlsx', '.xls', '.csv')):
                try:
                    if file.name.endswith(('.xlsx', '.xls')):
                        df = pd.read_excel(file)
                    else:
                        df = pd.read_csv(file)
                    
                    # Replace NaN values with None
                    df.replace({np.nan: None}, inplace=True)
                    
                    # Process the DataFrame and create or update LeadEdit objects
                    row_count = 0  # Counter for tracking row processed
                    for index, row in df.iterrows():
                        lead_data = {}
                        for field in LeadEdit._meta.fields:
                            field_name = field.name
                            if field_name == 'user':
                                user_id = row.get('user_id')
                                lead_data[field_name] = get_object_or_404(User, id=user_id) if user_id else None
                            elif field_name == 'fb_leads':
                                fb_leads_id = row.get('fb_leads_id')
                                lead_data[field_name] = get_object_or_404(FbLeads, id=fb_leads_id) if fb_leads_id else None
                            elif field_name in row:
                                lead_data[field_name] = row[field_name]
                            else:
                                lead_data[field_name] = None

                        # Ensure uniqueness by adding additional criteria if needed
                        fb_leads_instance = lead_data.get('fb_leads')
                        user_instance = lead_data.get('user')
                        
                        # Attempt to find existing record
                        if fb_leads_instance and user_instance:
                            lead_edit_qs = LeadEdit.objects.filter(fb_leads=fb_leads_instance, user=user_instance)
                        else:
                            lead_edit_qs = LeadEdit.objects.filter(fb_leads=fb_leads_instance)

                        if lead_edit_qs.exists():
                            if lead_edit_qs.count() == 1:
                                lead_edit = lead_edit_qs.first()
                                for key, value in lead_data.items():
                                    setattr(lead_edit, key, value)
                                lead_edit.save()
                            else:
                                # If multiple records are found, you can choose to update them all or handle as per your logic
                                for lead_edit in lead_edit_qs:
                                    for key, value in lead_data.items():
                                        setattr(lead_edit, key, value)
                                    lead_edit.save()
                        else:
                            LeadEdit.objects.create(**lead_data)
                        
                        row_count += 1
                        # If 100 rows processed, sleep for 50 seconds
                        if row_count % 100 == 0:
                            time.sleep(50)
                    
                    return Response({'message': 'Data uploaded successfully'}, status=200)
                except Exception as e:
                    return Response({'error': str(e)}, status=400)
            else:
                return Response({'error': 'Invalid file format. Please upload a valid Excel file (xlsx/xls) or CSV file.'}, status=400)
        else:
            return Response(serializer.errors, status=400)

class LeadEditUploadViewNew(APIView):
    serializer_class = FileUploadSerializer
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            if file.name.endswith(('.xlsx', '.xls', '.csv')):
                try:
                    if file.name.endswith(('.xlsx', '.xls')):
                        df = pd.read_excel(file, sheet_name="prospect_discussions_tbl")
                    else:
                        df = pd.read_csv(file)
                    df.dropna(how='all', inplace=True)
                    # Replace NaN values with None
                    df.replace({np.nan: None}, inplace=True)
                    print(df.shape)
                    df.rename(columns={"discription":"description"}, inplace=True)
                    print(df['created_at'])
                    LeadEdit.objects.all().delete()
                    data = df.to_dict('records')
                    saved_data = []
                    error_data = []
                    for row in data:
                        ser = LeadEditSerializer(LeadEdit.objects.all().first())
                        print(ser.data)
                        print(row)
                        serializer_new = LeadEditSerializer(data=row)
                        if serializer_new.is_valid():
                            print("new row")
                            serializer_new.save()
                            saved_data.append(row)
                        else:
                            print("error", serializer_new.errors)
                            error_data.append({"row": row, "errors": serializer_new.errors})
                        # break
                    # today_date = date.today()
                    # query = LeadEdit.objects.all().delete()
                    # print(len(query))
                    # serializer_new = LeadEditSerializer(query, many=True)
                    return Response({"saved_data": saved_data, "error_data": error_data})
                    # return Response({"data": "serializer_new.data"})
                except:
                    return Response({"error":"Invalid file format. Please upload a valid Excel file (xlsx/xls) or CSV file."})
        
        return Response({"error":"Invalid file format. Please upload a valid Excel file (xlsx/xls) or CSV file."})
        
class FBLeadUploadViewNew(APIView):
    serializer_class = FileUploadSerializer
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            if file.name.endswith(('.xlsx', '.xls', '.csv')):
                # try:
                if file.name.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(file, sheet_name="prospect_discussions_tbl")
                else:
                    df = pd.read_csv(file)
                df.dropna(how='all', inplace=True)
                # Replace NaN values with None
                df.replace({np.nan: None}, inplace=True)
                print(df.shape)
                # df['project_name'] = df['project_name'].apply(lambda x: x.split(','))
                # df['project_type_name'] = df['project_type_name'].apply(lambda x: x.split(','))
                # print(df.head)

                df.rename(columns={"discription":"description"}, inplace=True)
                query = FbLeads.objects.filter(created_at__lte="2024-06-02").delete()
                data = df.to_dict('records')
                saved_data = []
                error_data = []
                for row in data:
                    # row['project_name'] = row['project_name'].replace("2","2108")
                    # row['project_name'] = row['project_name'].replace("1","2")
                    if ',' in row['project_name']:
                        row['project_name'] = row['project_name'].split(",")
                    else:
                        row['project_name'] = [row['project_name']]
                    if ',' in row['project_type_name']:
                        row['project_type_name'] = row['project_type_name'].split(",")
                    else:
                        row['project_type_name'] = [row['project_type_name']]
                    if not row['dump_lead']:
                        row['dump_lead'] = 0

                    if row['dump_lead']:
                        if row['dump_lead']==1:
                            row['dump_lead'] = True
                        else:
                            row['dump_lead'] = False
                    # ser = FbLeadSerializer(LeadEdit.objects.all().first())
                    print("here")
                    # try:
                    #     lead = FbLeads.objects.get(id=row['id'])
                    #     lead.dump_lead = row['dump_lead']
                    #     lead.save()
                    # except Exception as e:
                    #     print("skiped because",e)
                    row['created_at'] = datetime.strptime(row['created_at'] + " " + row['created_time'], "%d-%m-%Y %H:%M:%S")
                    serializer_new = FbLeadPostSerializer(data=row)
                    if serializer_new.is_valid():
                        print("new row")
                        serializer_new.save()
                        lead = FbLeads.objects.get(pk=serializer_new.data['id'])
                        lead.id = row['id']
                        lead.save()
                        FbLeads.objects.filter(pk=serializer_new.data['id']).delete()
                        saved_data.append(row)
                    else:
                        print("error", serializer_new.errors)
                        error_data.append({"row": row, "errors": serializer_new.errors})
                    # break
                # today_date = date.today()
                # query = LeadEdit.objects.all().delete()
                # print(len(query))
                # serializer_new = LeadEditSerializer(query, many=True)
                return Response({"error_data": error_data})
                    # return Response({"data": "serializer_new.data"})
                # except Exception as e:
                #     print(e)
                #     return Response({"error":"Invalid file format. Please upload a valid Excel file (xlsx/xls) or CSV file."})
        
        return Response({"error":"Invalid file format. Please upload a valid Excel file (xlsx/xls) or CSV file."})

class UploadDiscussion(APIView):
    permission_classes = [AllowAny]
    serializer_class = FileUploadSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            if file.name.endswith(('.xlsx', '.xls', '.csv')):
                # try:
                if file.name.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(file, sheet_name="prospect_discussions_tbl")
                else:
                    df = pd.read_csv(file, low_memory=False)
                df.dropna(how='all', inplace=True)
                # Replace NaN values with None
                df.replace({np.nan: None}, inplace=True)
                print(df.shape)
                # df['project_name'] = df['project_name'].apply(lambda x: x.split(','))
                # df['project_type_name'] = df['project_type_name'].apply(lambda x: x.split(','))
                # print(df.head)

                df.rename(columns={"discription":"description"}, inplace=True)
                df['created_at'] = pd.to_datetime(df['created_at'], dayfirst=True)
                # lead = FbLeads.objects.get(pk=5602)
                # lead.id = 5062
                # lead.save()
                # FbLeads.objects.filter(pk=5602).delete()
                data = df.to_dict("records")
                query = LeadEdit.objects.filter(created_at__lte="2024-06-02").delete()

                serializer = LeadEditSerializer(data=data, many=True)
                if not serializer.is_valid():
                    return Response({"error": serializer.errors})
                
                serializer.save()
                return Response(serializer.data)
            
        return Response({"error":"Invalid file format. Please upload a valid Excel file (xlsx/xls) or CSV file."})
        
# class DescripApi(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#         if serializer.is_valid():
#             file = serializer.validated_data['file']
#             if file.name.endswith(('.xlsx', '.xls', '.csv')):
#                 try:
#                     if file.name.endswith(('.xlsx', '.xls')):
#                         df = pd.read_excel(file, sheet_name="prospect_discussions_tbl")
#                     else:
#                         df = pd.read_csv(file)
#                     df.dropna(how='all', inplace=True)
#                     # Replace NaN values with None
#                     df.replace({np.nan: None}, inplace=True)

class OldNotificationAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        leads = FbLeads.objects.all()
        count = 0
        for lead in leads:
            lead_edit = LeadEdit.objects.filter(fb_leads=lead)
            if lead_edit.exists():
                lead_edit = lead_edit.last()
                if '1970' in str(lead_edit.created_at):
                    lead.updated_at = None
                else:
                    lead.updated_at = lead_edit.created_at
                lead.save()
                # if lead_edit.mode:
                #     if lead_edit.mode.mode_lead not in ['Booked', 'Dump']:
                #         print(lead_edit.next_schedule_date)
                #         notification_data = {"sent_to":lead_edit.user.id, "head":lead.full_name, "message":f"Next scheduled at {lead_edit.next_schedule_date} for {lead_edit.mode.mode_lead}, Lead ID:{lead.id}"}
                #         print(notification_data)
                #         notiserializer = NotificationStoreSerializer(data=notification_data)
                #         if notiserializer.is_valid():
                #             # notiserializer.save()
                #             print("save")
                #         else:
                #             print("There should be notification but failed to add")
                #             print("lead",lead)
                #             print("lead_edit",lead_edit)
                # else:
                #     print("This is done")
            else:
                if '1970' in str(lead.created_at):
                    lead.updated_at = None
                else:
                    lead.updated_at = lead.created_at
                lead.save()
                print("This has not yet discussed", count)
            count += 1
        return Response({'Notifications':"Done"})

class LeadEditUpdate(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        status_of_lead = ['Re-Visit',"Do Not Call","Block Enquiry","Very Strong Lead","Non Convertable Lead","May Be"]
        convert = ['Site Visit','Poor Lead','Poor Lead','Good Lead','Poor Lead','Poor Lead']
        for stat, conv in zip(status_of_lead,convert):
            stl = StatusLead.objects.get(status_lead=stat)
            new_stl = StatusLead.objects.get(status_lead=conv)
            print("old",stl,"new",new_stl)
            lead_edits = LeadEdit.objects.filter(status_of_lead=stl)
            # print([i.status_of_lead for i in lead_edits])
            lead_edits.update(status_of_lead=new_stl)
            # lead_edits.save()
            # lead_edits = LeadEdit.objects.filter(status_of_lead=stl).update(status_of_lead=new_stl)
            # print(lead_edits)
            # print(LeadEditSerializer(lead_edits, many=True).data)
            # break
        return Response({'Update':"Done"})

class UpdateLeadFeedback(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        leads = FbLeads.objects.all()
        for lead in leads:
            disc = LeadEdit.objects.filter(fb_leads=lead)
            if disc.exists():
                lead.feedback = disc.last().description
            else:
                lead.feedback = ""

            lead.save()
        
        return Response({"data":"Feedback updated."})

class UpdateNoti(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        notification = NotificationStore.objects.filter(sent_to=User.objects.get(pk=28))
        notification.update(seen=True)
        return Response({"update":"done"})

class DataCheck(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        leads = FbLeads.objects.all()
        lead_num = {}
        for i in leads:
            if i.phone_number not in lead_num:
                lead_num[i.phone_number] = 1
            else:
                lead_num[i.phone_number] += 1

        return Response(lead_num)