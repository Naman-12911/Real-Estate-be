from django.shortcuts import render
from rest_framework.views import APIView
from bookingForm.models import PersonalDeatils
from bookingForm.serializers import BookingPersonalDeatils
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http.response import Http404
from rest_framework.response import Response
from .filters import ProfileSearchFilters
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter
from rest_framework import status
from django_filters import rest_framework as filters
from .models import *
from collections import defaultdict
from .serializer import *
from account.models import User
from bookingForm.models import Booking, PersonalDeatils
from documentation.models import Receipt
from realEstate.pagination import CommonPagination
from openpyxl import Workbook
from io import BytesIO
from datetime import datetime
from django.http import HttpResponse
# Create your views here.

class ProfileSearchData(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = PersonalDeatils.objects.filter(deleted=False, cancelled=False)
    serializer_class = BookingPersonalDeatils
    filter_backends = [filters.DjangoFilterBackend,SearchFilter]
    filterset_class = ProfileSearchFilters
    search_fields = ['applicant_name', 'unit_no', 'project']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        if not queryset.exists():
            return Response({'detail': 'No data found'}, status=status.HTTP_204_NO_CONTENT)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

# class PaymentStagesAPIview(APIView):
#     permission_classes = [IsAuthenticated]
#     def get_object(self, pk):
#         try:
#             return PaymentStages.objects.get(pk=pk)
#         except PaymentStages.DoesNotExist:
#             raise Http404
        
#     def get(self, request, pk=None, format=None):
#             if pk:
#                 data = self.get_object(pk)
#                 serializer = PaymentStages(data)
#                 return Response(serializer.data)

#             else:
#                 data = PaymentStages.objects.all()
#                 serializer = PaymentStagesSerializer(data, many=True)

#                 return Response(serializer.data)
#     def post(self, request, format=None):
#             current_user = request.user
#             mutable_data = request.data.copy()
#             mutable_data['user'] = current_user.id 
            
#             serializer = PaymentStagesSerializer(data=mutable_data)

#             # Check if the data passed is valid
#             serializer.is_valid(raise_exception=True)
#             serializer.save()
#             # Return Response to User

#             response = Response()

#             response.data = {
#                 'message': 'payment stage Created Successfully',
#                 'data': serializer.data
#             }
#             return response
    
#     def patch(self, request, pk=None, format=None):
#                 # Get the todo to update
#             Payment_stages_deatils_to_update = PaymentStages.objects.get(pk=pk)

#             serializer = PaymentStages(instance=Payment_stages_deatils_to_update,data=request.data, partial=True)

#             serializer.is_valid(raise_exception=True)
#             serializer.save()
#             response = Response()

#             response.data = {
#                 'message': 'Payment stages upated Successfully',
#                 'data': serializer.data
#             }

#             return response
#     def delete(self, request, pk, format=None):
#         co_applicant_form_to_delete =  PaymentStages.objects.get(pk=pk)

#             # delete the todo
#         co_applicant_form_to_delete.delete()

#         return Response({
#             'message': 'Payment stages Deleted Successfully'
#         })





class PaymentStageDetailAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return PaymentStageDetail.objects.get(pk=pk)
        except PaymentStageDetail.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
        personal_id = request.query_params.get('personal_id')  # Get personal_id from query parameters
        if personal_id:
            data = PaymentStageDetail.objects.filter(personal_deatils=personal_id, deleted=False, cancelled=False).order_by("-created_at")
        else:
            data = PaymentStageDetail.objects.filter(deleted=False, cancelled=False).order_by("-created_at")

        grouped_data = defaultdict(list)

        for obj in data:
            grouped_data[int(obj.personal_deatils.pk)].append(obj)

        serialized_data = {}
        for key, value in grouped_data.items():
            serialized_data = PaymentStageDetailSerializer(value, many=True).data

        # Remove the key "1" and use a hardcoded value instead
        final_serialized_data = {"personal_deatils": serialized_data}
        
        return Response(final_serialized_data)
    def post(self, request, format=None):
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            
            serializer = PaymentStageDetailSerializer(data=mutable_data)

            # Check if the data passed is valid
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Return Response to User

            response = Response()

            response.data = {
                'message': 'payment stage deatils Created Successfully',
                'data': serializer.data
            }
            return response
    
    def patch(self, request, pk=None, format=None):
        # Get the todo to update
        Payment_stages_details_deatils_to_update = PaymentStageDetail.objects.get(pk=pk)

        serializer = PaymentStageDetailSerializer(instance=Payment_stages_details_deatils_to_update, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = Response()
        response.data = {
            'message': 'Payment stages deatils updated Successfully',
            'data': serializer.data
        }

        return response

    def delete(self, request, pk, format=None):
        co_applicant_form_to_delete =  PaymentStageDetail.objects.get(pk=pk)

            # delete the todo
        co_applicant_form_to_delete.delete()

        return Response({
            'message': 'Payment stages deatils Deleted Successfully'
        })
    
class PaymentReceiptsAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return PaymentReceipts.objects.get(pk=pk)
        except PaymentReceipts.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = self.get_object(pk)
                serializer = PaymentReceipts(data)
                return Response(serializer.data)

            else:
                data = PaymentReceipts.objects.filter(deleted=False).order_by("-created_at")
                serializer = PaymentReceiptsSerializer(data, many=True)

                return Response(serializer.data)
    def post(self, request, format=None):
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            
            serializer = PaymentReceiptsSerializer(data=mutable_data)

            # Check if the data passed is valid
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Return Response to User

            response = Response()

            response.data = {
                'message': 'payment recepts Created Successfully',
                'data': serializer.data
            }
            return response
    
    def patch(self, request, pk=None, format=None):
                # Get the todo to update
            Payment_receipts_details_deatils_to_update = PaymentReceipts.objects.get(pk=pk)

            serializer = PaymentReceipts(instance=Payment_receipts_details_deatils_to_update,data=request.data, partial=True)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = Response()

            response.data = {
                'message': 'Payment receipts deatils upated Successfully',
                'data': serializer.data
            }

            return response
    def delete(self, request, pk, format=None):
        co_applicant_form_to_delete =  PaymentReceipts.objects.get(pk=pk)

            # delete the todo
        co_applicant_form_to_delete.delete()

        return Response({
            'message': 'Payment receipts deatils Deleted Successfully'
        })
    

class RemiderDemandInformationAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return RemiderDemandInformation.objects.get(pk=pk)
        except RemiderDemandInformation.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = self.get_object(pk)
                serializer = RemiderDemandInformation(data)
                return Response(serializer.data)

            else:
                data = RemiderDemandInformation.objects.filter(deleted=False).order_by("-created_at")
                serializer = RemiderDemandInformationSerializer(data, many=True)

                return Response(serializer.data)
    def post(self, request, format=None):
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            
            serializer = RemiderDemandInformationSerializer(data=mutable_data)

            # Check if the data passed is valid
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Return Response to User

            response = Response()

            response.data = {
                'message': 'payment demand Information Created Successfully',
                'data': serializer.data
            }
            return response
    
    def patch(self, request, pk=None, format=None):
                # Get the todo to update
            Payment_demand_details_deatils_to_update = RemiderDemandInformation.objects.get(pk=pk)

            serializer = RemiderDemandInformation(instance=Payment_demand_details_deatils_to_update,data=request.data, partial=True)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = Response()

            response.data = {
                'message': 'Payment demand Information upated Successfully',
                'data': serializer.data
            }

            return response
    def delete(self, request, pk, format=None):
        co_applicant_form_to_delete =  RemiderDemandInformation.objects.get(pk=pk)

            # delete the todo
        co_applicant_form_to_delete.delete()

        return Response({
            'message': 'Payment demand Information upated Successfully',
        })

class UserBalance(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        # users = User.objects.filter(accounts_employee=True)
        paginator = CommonPagination()
        data=[]
        # for user in users:
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        # applicant_name = request.query_params.get('end_date')
        unit_no_param = request.query_params.get('unit_no')
        customer_name = request.query_params.get('customer_name')
        if start_date is None or end_date is None:
            bookings = Booking.objects.filter(deleted=False, cancelled=False).order_by("-created_at")
        else:
            bookings = Booking.objects.filter(deleted=False,created_at__range=[start_date, end_date], cancelled=False).order_by("-created_at")

        if unit_no_param:
            bookings = bookings.filter(unit_no__unit_no=unit_no_param)
        if customer_name:
            bookings = bookings.filter(personaldeatils__applicant_name__icontains=customer_name)

        total_amt = 0
        if len(bookings)>0:
            for booking in bookings:
                # if booking.unit_cost=="":
                total_amount = booking.cost_payable_to_company
                # else:
                #     total_amount = booking.cost_payable_to_company + float(booking.unit_cost)
                if booking.booking_amount == "":
                    booking_amount = 0
                else:
                    booking_amount = float(booking.booking_amount)
                paid = 0

                profile = PersonalDeatils.objects.filter(booking=booking, deleted=False, cancelled=False)
                if len(profile)>0:
                    profile = profile.last()
                    payment_stages = PaymentStageDetail.objects.filter(personal_deatils=profile, deleted=False, cancelled=False)
                    if len(payment_stages)>0:
                        for payment_stage in payment_stages:
                            try:
                                payment = Receipt.objects.get(payment_stage=payment_stage, unit_number=booking.unit_no, cancel=False, delete=False, deleted=False, cancelled=False)
                                # if len(payment)>0:
                                    # for pay in payment:
                                    # payment = payment.last()
                                if payment_stage.paybale_amount == "":
                                    amount_recived = 0
                                else:
                                    amount_recived = float(payment_stage.paybale_amount)
                                paid += amount_recived
                            except Exception as e:
                                print(e)
                                
                    other_charges = 0
                    balance = total_amount - paid
                    # if booking.unit_cost == "":
                    #     other_charges = booking.cost_payable_to_company
                    # else:
                    #     other_charges = booking.cost_payable_to_company - float(booking.unit_cost)
                    other_charges = booking.maintainance_charges_2_year + booking.external_electrical_charges + booking.water_connection_charges + booking.mutation_charges + booking.socity_maintaince_charges
                    additional_charges = booking.corner_plot_charges + booking.park_face_charges + booking.registry_extra_charges + booking.other_charges + booking.wide_road_facing_charges
                    cost_without_gst = total_amount - booking.govt_extra_charges
                    
                    user_data = {'customer_name':profile.applicant_name, 'unit_no':booking.unit_no.unit_no, "sqft":booking.unit_no.square_fit, 'booking_date':booking.application_date, 
                        'basic_charge':booking.unit_cost, 'other_charges':other_charges, 'total_cost':total_amount, 'total_received':paid, 'cost_without_gst':cost_without_gst,
                        'balance':balance, "registry_date":booking.registry_date, "posession_date":booking.posession_date, "additional_charges":additional_charges, 'gst':booking.govt_extra_charges}
                    data.append(user_data)
                    total_amt += paid

        result_page = paginator.paginate_queryset(data, request)
        response = {'data': result_page, 'count': len(data), 'total':total_amt}
        return paginator.get_paginated_response(response)

class UserBalanceExcel(APIView):
    permission_classes = [AllowAny]

    def get(self,request):
        # users = User.objects.filter(accounts_employee=True)
        # paginator = CommonPagination()
        data=[]
        # for user in users:
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        data_filter = request.query_params.get('data_filter')
        if start_date is None or end_date is None:
            bookings = Booking.objects.filter(deleted=False, cancelled=False).order_by("-created_at")
        else:
            bookings = Booking.objects.filter(created_at__range=[start_date, end_date], deleted=False, cancelled=False)
        
        # Create Excel workbook and sheet
        wb = Workbook()
        ws = wb.active
        if data_filter.lower()=='all':
            ws.append([
                'Customer Name', 
                'Unit No', 
                'SQFT', 
                'Booking Date', 
                'Basic Charge', 
                'Other Charges', 
                'Additional Charges',
                'Total Cost', 
                'GST',
                'Grand Total'
                'Total Received', 
                'Balance', 
                'Registry Date', 
                'Possession Date'
            ])
        elif data_filter.lower()=='registry':
            ws.append([
                'Customer Name', 
                'Unit No', 
                # 'SQFT', 
                'Booking Date', 
                # 'Basic Charge', 
                # 'Other Charges', 
                # 'Total Cost', 
                # 'Total Received', permanent_address mobile_number
                # 'Balance', 
                'Registry Date', 
                'Possession Date',
            ])
        elif  data_filter.lower()=='customer':
            ws.append([
                'Customer Name', 
                'Unit No', 
                'SQFT', 
                'Booking Date', 
                # 'Basic Charge', 
                # 'Other Charges', 
                'Total Cost', 
                # 'Total Received', 
                # 'Balance', 
                'Address',
                'Mobile No.'
                # 'Registry Date', 
                # 'Possession Date',
            ])

        registry_count = 0
        posession_count = 0
        if len(bookings)>0:
            for booking in bookings:
                # if booking.unit_cost=="":
                total_amount = booking.cost_payable_to_company
                # else:
                #     total_amount = booking.cost_payable_to_company + float(booking.unit_cost)
                if booking.booking_amount == "":
                    booking_amount = 0
                else:
                    booking_amount = float(booking.booking_amount)
                paid = 0

                profile = PersonalDeatils.objects.filter(booking=booking, deleted=False, cancelled=False)
                if len(profile)>0:
                    profile = profile.last()
                    payment_stages = PaymentStageDetail.objects.filter(personal_deatils=profile, deleted=False, cancelled=False)
                    if len(payment_stages)>0:
                        for payment_stage in payment_stages:
                            try:
                                payment = Receipt.objects.get(payment_stage=payment_stage, unit_number=booking.unit_no, cancel=False, delete=False, deleted=False, cancelled=False)
                                # if len(payment)>0:
                                    # for pay in payment:
                                    # payment = payment.last()
                                if payment_stage.paybale_amount == "":
                                    amount_recived = 0
                                else:
                                    amount_recived = float(payment_stage.paybale_amount)
                                paid += amount_recived
                            except Exception as e:
                                print(e)
                                
                    other_charges = 0
                    balance = total_amount - paid
                    # if booking.unit_cost == "":
                    #     other_charges = booking.cost_payable_to_company
                    # else:
                    #     other_charges = booking.cost_payable_to_company - float(booking.unit_cost)
                    other_charges = booking.maintainance_charges_2_year + booking.external_electrical_charges + booking.water_connection_charges + booking.mutation_charges + booking.socity_maintaince_charges
                    additional_charges = booking.corner_plot_charges + booking.park_face_charges + booking.registry_extra_charges + booking.other_charges + booking.wide_road_facing_charges
                    cost_without_gst = total_amount - booking.govt_extra_charges
                    user_data = {'customer_name':profile.applicant_name, 'unit_no':booking.unit_no.unit_no, "sqft":booking.unit_no.square_fit, 'booking_date':booking.application_date, 
                        'basic_charge':booking.unit_cost, 'other_charges':other_charges, 'total_cost':total_amount, 'total_received':paid, 'cost_without_gst':cost_without_gst,
                        'balance':balance, "registry_date":booking.registry_date, "posession_date":booking.posession_date, "additional_charges":additional_charges, "gst":booking.govt_extra_charges}
                    data.append(user_data)
                    if user_data['registry_date']:
                        user_data['registry_date'] = user_data['registry_date'].strftime("%d-%m-%Y")
                        registry_count += 1

                    if user_data['posession_date']:
                        user_data['posession_date'] = user_data['posession_date'].strftime("%d-%m-%Y")
                        posession_count += 1

                    if data_filter.lower()=='all':
                        ws.append([
                            user_data['customer_name'],
                            user_data['unit_no'],
                            user_data['sqft'],
                            user_data['booking_date'].strftime("%d-%m-%Y"),
                            user_data['basic_charge'],
                            user_data['other_charges'],
                            user_data['additional_charges'],
                            user_data['cost_without_gst'],
                            user_data['gst'],
                            user_data['total_cost'],
                            user_data['total_received'],
                            user_data['balance'],
                            user_data['registry_date'],
                            user_data['posession_date']
                        ])
                    elif data_filter.lower()=='registry':
                        ws.append([
                            user_data['customer_name'],
                            user_data['unit_no'],
                            # user_data['sqft'],
                            user_data['booking_date'].strftime("%d-%m-%Y"),
                            # user_data['basic_charge'],
                            # user_data['other_charges'],
                            # user_data['total_cost'],
                            # user_data['total_received'],
                            # user_data['balance'],
                            user_data['registry_date'],
                            user_data['posession_date']
                        ])
                    elif  data_filter.lower()=='customer':
                        ws.append([
                            user_data['customer_name'],
                            user_data['unit_no'],
                            user_data['sqft'],
                            user_data['booking_date'].strftime("%d-%m-%Y"),
                            # user_data['basic_charge'],
                            # user_data['other_charges'],
                            user_data['total_cost'],
                            profile.persent_address,
                            profile.mobile_number
                            # user_data['total_received'],
                            # user_data['balance'],
                            # user_data['registry_date'],
                            # user_data['posession_date']
                        ])
        # result_page = paginator.paginate_queryset(data, request)
        response = {'data': data, 'count': len(data)}
        if data_filter.lower()=='registry':
            ws.append([
                "Total registery",
                registry_count,
                "Total posession",
                posession_count,
                "   "
            ])
       
        
        # Save workbook to BytesIO buffer
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        
        # Prepare HTTP response with Excel file
        response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=Account_report_{datetime.now()}.xlsx'

        return response


class PaymentStageDetailCancelAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return PaymentStageDetail.objects.get(pk=pk)
        except PaymentStageDetail.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
        personal_id = request.query_params.get('personal_id')  # Get personal_id from query parameters
        if personal_id:
            data = PaymentStageDetail.objects.filter(personal_deatils=personal_id, deleted=False, cancelled=True).order_by("-created_at")
        else:
            data = PaymentStageDetail.objects.filter(deleted=False, cancelled=True).order_by("-created_at")

        grouped_data = defaultdict(list)

        for obj in data:
            grouped_data[int(obj.personal_deatils.pk)].append(obj)

        serialized_data = {}
        for key, value in grouped_data.items():
            serialized_data = PaymentStageDetailSerializer(value, many=True).data

        # Remove the key "1" and use a hardcoded value instead
        final_serialized_data = {"personal_deatils": serialized_data}
        
        return Response(final_serialized_data)