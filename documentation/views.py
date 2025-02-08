from django.shortcuts import render
from rest_framework.views import APIView
from bookingForm.models import PersonalDeatils
from bookingForm.serializers import BookingPersonalDeatils
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http.response import Http404
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter
from rest_framework import status
from django_filters import rest_framework as filters
from .models import *
from collections import defaultdict
from .serializer import *
from .filters import ReceiptFilters, ReceiptCancelFilters
from realEstate.pagination import CommonPagination
from profileSearch.models import *
from .helper import *
from django.core.management.base import BaseCommand
from django.conf import settings
from openpyxl import Workbook
from io import BytesIO
from datetime import datetime
from django.http import HttpResponse
import random

class DemandLetterAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return DemandLetter.objects.get(pk=pk)
        except DemandLetter.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            unit_no = request.query_params.get('unit_no')
            paginator = CommonPagination()
            if pk:
                data = self.get_object(pk)
                serializer = DemandLetter(data)
                return Response(serializer.data)

            else:
                if unit_no:
                    data = DemandLetter.objects.filter(unit_number__unit_no=unit_no, cancelled=False).order_by('-created_at')
                else:
                    data = DemandLetter.objects.filter(cancelled=False).order_by('-created_at')

                result_page = paginator.paginate_queryset(data, request)
                serializer = DemandLetterSerializer(result_page, many=True)
                return paginator.get_paginated_response(serializer.data)
            
    def post(self, request, format=None):
        current_user = request.user
        mutable_data = request.data.copy() if request.data else {}

        mutable_data['user'] = current_user.id 
                
        serializer = DemandLetterSerializer(data=mutable_data)

        # Check if the data passed is valid
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Return Response to User
        response = Response({
            'message': 'Demand Letter Created Successfully',
            'data': serializer.data
        })
        return response

    
    def patch(self, request, pk=None, format=None):
        # Get the todo to update
        DemandLetter_deatils_to_update = DemandLetter.objects.get(pk=pk)

        serializer = DemandLetterSerializer(instance=DemandLetter_deatils_to_update, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = Response()
        response.data = {
            'message': 'Demand Letter updated Successfully',
            'data': serializer.data
        }

        return response

    def delete(self, request, pk, format=None):
        DemandLetter_to_delete =  DemandLetter.objects.get(pk=pk)

            # delete the todo
        DemandLetter_to_delete.delete()

        return Response({
            'message': 'Demand Letter Deleted Successfully'
        })
    

class ModeOfPaymentAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return ModeOfPayment.objects.get(pk=pk)
        except ModeOfPayment.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = self.get_object(pk)
                serializer = ModeOfPayment(data)
                return Response(serializer.data)

            else:
                data = ModeOfPayment.objects.all()
                serializer = ModeOfPaymentSerializer(data, many=True)

                return Response(serializer.data)
            
    def post(self, request, format=None):
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            
            serializer = ModeOfPaymentSerializer(data=mutable_data)

            # Check if the data passed is valid
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Return Response to User

            response = Response()

            response.data = {
                'message': 'Mode Of Payment Created Successfully',
                'data': serializer.data
            }
            return response
    
    def patch(self, request, pk=None, format=None):
        # Get the todo to update
        DemandLetter_deatils_to_update = ModeOfPayment.objects.get(pk=pk)

        serializer = ModeOfPaymentSerializer(instance=DemandLetter_deatils_to_update, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = Response()
        response.data = {
            'message': 'Mode Of Payment updated Successfully',
            'data': serializer.data
        }

        return response

    def delete(self, request, pk, format=None):
        ModeOfPayment_to_delete =  ModeOfPayment.objects.get(pk=pk)

            # delete the todo
        ModeOfPayment_to_delete.delete()

        return Response({
            'message': 'Mode Of Payment Deleted Successfully'
        })
    

class BankNameBranchNameAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return BankName.objects.get(pk=pk)
        except BankName.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = self.get_object(pk)
                serializer = BankName(data)
                return Response(serializer.data)

            else:
                data = BankName.objects.all()
                serializer = BankNameSerializer(data, many=True)

                return Response(serializer.data)
            
    def post(self, request, format=None):
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            
            serializer = BankNameSerializer(data=mutable_data)

            # Check if the data passed is valid
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Return Response to User

            response = Response()

            response.data = {
                'message': 'Bank Name Created Successfully',
                'data': serializer.data
            }
            return response
    
    def patch(self, request, pk=None, format=None):
        # Get the todo to update
        BankName_to_update = BankName.objects.get(pk=pk)

        serializer = BankNameSerializer(instance=BankName_to_update, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = Response()
        response.data = {
            'message': 'Bank Name  updated Successfully',
            'data': serializer.data
        }

        return response

    def delete(self, request, pk, format=None):
        BankName_to_delete =  BankName.objects.get(pk=pk)

            # delete the todo
        BankName_to_delete.delete()

        return Response({
            'message': 'Bank Name Deleted Successfully'
        })
    
class ReceiptAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return Receipt.objects.get(pk=pk)
        except Receipt.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = self.get_object(pk)
                serializer = Receipt(data)
                return Response(serializer.data)

            else:
                paginator = CommonPagination()
                start_date = request.query_params.get('start_date')
                end_date = request.query_params.get('end_date')
                if start_date and end_date:
                    data = Receipt.objects.filter(delete=False, deleted=False, cancelled=False, transation_date__range=[start_date, end_date]).order_by("-transation_date")
                else:
                    data = Receipt.objects.filter(delete=False, cancelled=False).order_by("-transation_date")
                #serializer = ReceiptSerializer(data, many=True)

                result_page = paginator.paginate_queryset(data, request)
                serializer = ReceiptSerializer(result_page, many=True)
                return paginator.get_paginated_response(serializer.data)
            
    def post(self, request, format=None):
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            
            serializer = ReceiptSerializer(data=mutable_data)

            # Check if the data passed is valid
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Return Response to User

            response = Response()

            response.data = {
                'message': 'Receipt Created Successfully',
                'data': serializer.data
            }
            return response
    
    def patch(self, request, pk=None, format=None):
        # Get the todo to update
        Receipt_to_update = Receipt.objects.get(pk=pk)

        serializer = ReceiptSerializer(instance=Receipt_to_update, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = Response()
        response.data = {
            'message': 'Receipt updated Successfully',
            'data': serializer.data
        }

        return response

    def delete(self, request, pk, format=None):
        Receipt_to_delete =  Receipt.objects.get(pk=pk)

            # delete the todo
        Receipt_to_delete.deleted = True
        Receipt_to_delete.save()

        return Response({
            'message': 'Receipt Deleted Successfully'
        })
    

class BookingFiltersData(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Receipt.objects.filter(deleted=False, delete=False, cancelled=False)
    serializer_class = ReceiptSerializer
    filter_backends = [filters.DjangoFilterBackend,SearchFilter]
    filterset_class = ReceiptFilters
    search_fields = ['unit_number']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        if not queryset.exists():
            return Response({'detail': 'No data found'}, status=status.HTTP_204_NO_CONTENT)

        serializer = self.get_serializer(queryset, many=True)
        total_amt = 0
        data = {'data':serializer.data}
        for i in serializer.data:
            total_amt += float(i['payment_stage']['paybale_amount'])
        
        data['total'] = round(total_amt,2)
        return Response(data)
    

class DemandLetterPersonalDeatilsAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return DemandLetter.objects.get(pk=pk)
        except DemandLetter.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            personal_details = request.query_params.get('personal_details')
            paginator = CommonPagination()
            if pk:
                data = self.get_object(pk)
                serializer = DemandLetter(data)
                return Response(serializer.data)

            else:
                if personal_details:
                    data = DemandLetter.objects.filter(payment_stage__personal_deatils=personal_details, deleted=False).order_by('-created_at')
                else:
                    data = DemandLetter.objects.filter(deleted=False).order_by('-created_at')

                result_page = paginator.paginate_queryset(data, request)
                serializer = DemandLetterSerializer(result_page, many=True)
                return Response(serializer.data)

class PaymentDetails(APIView):
    permission_classes = [AllowAny]

    def get(self, request, receipt_id):
        try:
            receipts = Receipt.objects.all()
            send_email_with_attachment(settings.DATABASES['default']['NAME'])
            for receipt in receipts:
                # Get all PaymentStageDetail objects
                payment_stages = PaymentStageDetail.objects.all()
                if not payment_stages.exists():
                    return Response({'error': 'No payment stages found.'}, status=status.HTTP_404_NOT_FOUND)
                
                # Randomly select a payment stage
                new_payment_stage = random.choice(payment_stages)
                
                # Update the receipt
                receipt.payment_stage = new_payment_stage
                receipt.save()

                serializer = ReceiptSerializer(receipt)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except Receipt.DoesNotExist:
            return Response({'error': 'Receipt not found.'}, status=status.HTTP_404_NOT_FOUND)

class ReceiptExportAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return Receipt.objects.get(pk=pk)
        except Receipt.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
        if pk:
            data = self.get_object(pk)
            serializer = Receipt(data)
            return Response(serializer.data)

        else:
            paginator = CommonPagination()
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            if start_date and end_date:
                data = Receipt.objects.filter(transation_date__range=[start_date, end_date]).order_by("-transation_date")
            else:
                data = Receipt.objects.filter(delete=False, deleted=False, cancelled=False).order_by("-transation_date")
            serializer = ReceiptSerializer(data, many=True)

            # Create Excel workbook and sheet
            wb = Workbook()
            ws = wb.active
            ws.append([
                'Name',
                'Project Name',
                'Unit Number',
                'Receipt Number',
                'Amount Received',
                'Bank Details',
                'Date',
                'By',
            ])

            if len(data)>0:
                for dta in serializer.data:
                    by = ""
                    if dta['by_bank']:
                        by = "Bank"
                    elif dta['by_customer']:
                        by = "Customer"
                    try:
                        bank_name = dta['bank_name']['bank_name']
                    except:
                        bank_name = ""
                    
                    ws.append([
                        dta['applicant_name'],
                        dta['project_name']['project_name'],
                        dta['unit_number']['unit_no'],
                        dta['receipt_unique_id'],
                        dta['payment_stage']['paybale_amount'],
                        bank_name,
                        dta['receipt_date'],
                        by
                    ])
            # Save workbook to BytesIO buffer
            buffer = BytesIO()
            wb.save(buffer)
            buffer.seek(0)
            
            # Prepare HTTP response with Excel file
            response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename=Receipt_report_{datetime.now()}.xlsx'

            return response
            # result_page = paginator.paginate_queryset(data, request)
            # serializer = ReceiptSerializer(result_page, many=True)
            # return paginator.get_paginated_response(serializer.data)
class BookingFiltersCancelData(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Receipt.objects.filter(deleted=False, delete=False, cancelled=True)
    serializer_class = ReceiptSerializer

    def get(self, request):
        queryset = self.queryset.filter(payment_stage__personal_deatils=request.GET['presonal_details'])

        if not queryset.exists():
            return Response({'detail': 'No data found'}, status=status.HTTP_204_NO_CONTENT)

        serializer = self.get_serializer(queryset, many=True)
        total_amt = 0
        data = {'data':serializer.data}
        for i in serializer.data:
            total_amt += float(i['payment_stage']['paybale_amount'])
        
        data['total'] = round(total_amt,2)
        return Response(data)

# class BookingFiltersCancelData(ListAPIView):
#     permission_classes = [IsAuthenticated]
#     queryset = Receipt.objects.filter(deleted=False, delete=False, cancelled=True)
#     serializer_class = ReceiptSerializer
#     filter_backends = [filters.DjangoFilterBackend,SearchFilter]
#     filterset_class = ReceiptCancelFilters
#     search_fields = ['presonal_details']

#     def list(self, request, *args, **kwargs):
#         queryset = self.filter_queryset(self.get_queryset())
        
#         if not queryset.exists():
#             return Response({'detail': 'No data found'}, status=status.HTTP_204_NO_CONTENT)

#         serializer = self.get_serializer(queryset, many=True)
#         total_amt = 0
#         data = {'data':serializer.data}
#         for i in serializer.data:
#             total_amt += float(i['payment_stage']['paybale_amount'])
        
#         data['total'] = round(total_amt,2)
#         return Response(data)