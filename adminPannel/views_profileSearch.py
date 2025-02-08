from django.shortcuts import render
from rest_framework.views import APIView
from bookingForm.models import PersonalDeatils
from bookingForm.serializers import BookingPersonalDeatils
from rest_framework.permissions import IsAuthenticated
from django.http.response import Http404
from rest_framework.response import Response

from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter
from rest_framework import status
from django_filters import rest_framework as filters
from profileSearch.models import *
from collections import defaultdict
from profileSearch.serializer import *
from account.models import User
from bookingForm.models import Booking, PersonalDeatils
from realEstate.pagination import CommonPagination
# Create your views here.








class PaymentStageDetailAPIview(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CommonPagination
    def get_object(self, pk):
        try:
            return PaymentStageDetail.objects.get(pk=pk)
        except PaymentStageDetail.DoesNotExist:
            raise Http404
        
    def get(self, request, format=None):
        personal_id = request.query_params.get('personal_id')  # Get personal_id from query parameters
        if personal_id:
            data = PaymentStageDetail.objects.filter(personal_deatils=personal_id,deleted=False, cancelled=False).order_by("-created_at")
        else:
            data = PaymentStageDetail.objects.filter(deleted=False, cancelled=False).order_by("-created_at")
        
        grouped_data = defaultdict(list)

        for obj in data:
            grouped_data[int(obj.personal_deatils.pk)].append(obj)

        paginated_data = []
        for key, value in grouped_data.items():
            paginator = self.pagination_class()  # Use the custom pagination class
            paginated_value = paginator.paginate_queryset(value, request)
            paginated_data.extend(paginated_value)

        serializer = PaymentStageDetailSerializer(paginated_data, many=True)
        return paginator.get_paginated_response(serializer.data)
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
    pagination_class = CommonPagination
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
                data = PaymentReceipts.objects.filter(deleted=False, cancelled=False).order_by('-created_at')
                paginator = self.pagination_class()
                result_page = paginator.paginate_queryset(data, request)
                serializer = PaymentReceiptsSerializer(result_page, many=True)
                return paginator.get_paginated_response(serializer.data)
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
                data = RemiderDemandInformation.objects.filter(deleted=False)
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
        data=[]
        # for user in users:
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date is None or end_date is None:
            bookings = Booking.objects.filter(deleted=False, cancelled=False)
        else:
            bookings = Booking.objects.filter(created_at__range=[start_date, end_date], deleted=False, cancelled=False)

        if len(bookings)>0:
            for booking in bookings:
                total_amount = booking.cost_payable_to_company
                if booking.booking_amount == "":
                    booking_amount = 0
                else:
                    booking_amount = float(booking.booking_amount)
                paid = booking_amount

                profile = PersonalDeatils.objects.filter(booking=booking, deleted=False, cancelled=False)
                if len(profile)>0:
                    profile = profile.last()
                    payment_stages = PaymentStageDetail.objects.filter(personal_deatils=profile, deleted=False, cancelled=False)
                    if len(payment_stages)>0:
                        for payment_stage in payment_stages:
                            payment = PaymentReceipts.objects.filter(stage_deatils=payment_stage, deleted=False)
                            if len(payment)>0:
                                payment = payment.last()
                                if payment.amount_recived == "":
                                    amount_recived = 0
                                else:
                                    amount_recived = float(payment.amount_recived)
                                paid += amount_recived

                    other_charges = 0
                    balance = total_amount - paid
                    if booking.unit_cost == "":
                        other_charges = booking.cost_payable_to_company
                    else:
                        other_charges = booking.cost_payable_to_company - float(booking.unit_cost)

                    user_data = {'customer_name':profile.applicant_name, 'unit_no':booking.unit_no.unit_no, "sqft":booking.unit_no.square_fit, 'booking_date':booking.created_at, 
                        'basic_charge':booking.unit_cost, 'other_charges':other_charges, 'total_cost':total_amount, 'total_received':paid,
                        'balance':balance, "registry_date":booking.registry_date, "posession_date":booking.posession_date}
                    data.append(user_data)

        response = {'data':data, 'count':len(data)}

        return Response(response, status=200)
