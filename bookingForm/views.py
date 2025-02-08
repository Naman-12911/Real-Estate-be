from django.shortcuts import render
from rest_framework.views import APIView
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http.response import Http404
from rest_framework.response import Response
from .filters import PersonalDeatilsFilters
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter
from rest_framework import status
from django_filters import rest_framework as filters
from workers.serializer import SiteWorkersSerializer
from realEstate.pagination import CommonPagination
from propertyStatus.models import UnitNo, Project
# Create your views here.
from documentation.models import Receipt, DemandLetter
from profileSearch.models import PaymentReceipts, PaymentStageDetail, RemiderDemandInformation
from workers.models import SiteWorkers, MonthlyExpense
from django.http import HttpResponse
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.shared import Pt
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class BookingApiview(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CommonPagination
    def get_object(self, pk):
        try:
            return Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = self.get_object(pk)
                serializer = BookingSerializers(data)
                return Response(serializer.data)

            else:
                data = Booking.objects.filter(deleted=False, cancelled=False).order_by('-created_at')
                paginator = self.pagination_class()
                result_page = paginator.paginate_queryset(data, request)
                serializer = BookingSerializers(result_page, many=True)
                return paginator.get_paginated_response(serializer.data)

    # def post(self, request, format=None):
    #     current_user = request.user
    #     mutable_data = request.data.copy()
    #     mutable_data['user'] = current_user.id
        
    #     if "cost_payable_to_company" not in mutable_data:
    #         mutable_data["cost_payable_to_company"] = 0
    #     costs = ["unit_cost","maintainance_charges_2_year","external_electrical_charges","water_connection_charges","corner_plot_charges","park_face_charges","registry_extra_charges","mutation_charges","socity_maintaince_charges","govt_extra_charges","other_charges","wide_road_facing_charges"]
    #     for i in costs:
    #         if (i=="govt_extra_charges") or (i=="unit_cost"):
    #             if mutable_data[i] == "":
    #                 mutable_data[i] = "0"
            
    #         mutable_data["cost_payable_to_company"] +=  float(mutable_data[i])

    #     serializer = BookingSerializers(data=mutable_data)

    #     # Check if the data passed is valid
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     # Return Response to User

    #     response = Response()

    #     response.data = {
    #         'message': 'Booking Created Successfully',
    #         'data': serializer.data
    #     }
    #     return response

    def post(self, request, format=None):
        current_user = request.user
        mutable_data = request.data.copy()
        mutable_data['user'] = current_user.id
        
        # Set default value for cost_payable_to_company if not present
        if "cost_payable_to_company" not in mutable_data:
            mutable_data["cost_payable_to_company"] = 0.0
        
        if mutable_data["cost_payable_to_company"] == "":
            mutable_data["cost_payable_to_company"] = 0
        
        if not mutable_data["cost_payable_to_company"]:
            mutable_data["cost_payable_to_company"] = 0
            
        # Define costs to consider for calculating cost_payable_to_company
        costs = ["unit_cost", "maintainance_charges_2_year", "external_electrical_charges",
                "water_connection_charges", "corner_plot_charges", "park_face_charges",
                "registry_extra_charges", "mutation_charges", "socity_maintaince_charges",
                "govt_extra_charges", "other_charges", "wide_road_facing_charges"]

        # Calculate cost_payable_to_company
        # mutable_data["cost_payable_to_company"] = float(mutable_data["cost_payable_to_company"])
        cost_payable_to_company = 0
        # if mutable_data["cost_payable_to_company"]>0:
        for i in costs:
            # Handle empty strings and convert them to 0
            if mutable_data.get(i, '') == '':
                mutable_data[i] = 0
            
            cost_payable_to_company += float(mutable_data[i])
            
        mutable_data["cost_payable_to_company"] = cost_payable_to_company

            
            #mutable_data["cost_payable_to_company"] += float(mutable_data[i])

        # Initialize serializer with modified data
        serializer = BookingSerializers(data=mutable_data)

        # Check if the data passed is valid
        serializer.is_valid(raise_exception=True)
        
        # Save the serializer
        serializer.save()

        unit_no = UnitNo.objects.get(pk=serializer.data['unit_no'])
        unit_no.available = False
        unit_no.booked = True
        unit_no.save()

        workerSerializer = SiteWorkersSerializer(data=mutable_data)
        workerSerializer.is_valid(raise_exception=True)
        workerSerializer.save()

        # Return Response to User
        response = Response()
        response.data = {
            'message': 'Booking Created Successfully',
            'data': serializer.data
        }
        return response

    
    def patch(self, request, pk=None, format=None):
        # Get the booking to update
        booking_to_update = Booking.objects.get(pk=pk)

        mutable_data = request.data.copy()

        # Set default value for cost_payable_to_company if not present
        if "cost_payable_to_company" not in mutable_data:
            mutable_data["cost_payable_to_company"] = 0

        if mutable_data["cost_payable_to_company"] == "":
            mutable_data["cost_payable_to_company"] = 0

        if not mutable_data["cost_payable_to_company"]:
            mutable_data["cost_payable_to_company"] = 0

        # Define costs to consider for calculating cost_payable_to_company
        costs = ["unit_cost", "maintainance_charges_2_year", "external_electrical_charges",
                "water_connection_charges", "corner_plot_charges", "park_face_charges",
                "registry_extra_charges", "mutation_charges", "socity_maintaince_charges",
                "govt_extra_charges", "other_charges", "wide_road_facing_charges"]

        # Convert cost_payable_to_company to an integer
        cost_payable_to_company = int(mutable_data["cost_payable_to_company"])

        # Check if cost_payable_to_company is greater than 0
        if not cost_payable_to_company > 0:
            for i in costs:
                # Handle empty strings and convert them to 0
                if mutable_data.get(i, '') == '':
                    mutable_data[i] = 0
                
                cost_payable_to_company += float(mutable_data[i])

        # Update mutable_data["cost_payable_to_company"] with the calculated value
        mutable_data["cost_payable_to_company"] = cost_payable_to_company

        # Initialize serializer with instance to update and data
        new_lst = ['booking_amount'] + costs
        for i in new_lst:
            if mutable_data[i]=="":
                mutable_data[i] = 0
        serializer = BookingSerializers(booking_to_update, data=mutable_data, partial=True)

        # Validate and save the serializer
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Prepare the response
        response_data = {
            'message': 'Booking updated Successfully',
            'data': serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)


        
    def delete(self, request, pk, format=None):
        Carrer_to_delete =  Booking.objects.get(pk=pk)

            # delete the todo
        Carrer_to_delete.delete()

        return Response({
            'message': 'Booking Deleted Successfully'
        })




class PersonalDeatilsApiview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return PersonalDeatils.objects.get(pk=pk)
        except PersonalDeatils.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = self.get_object(pk)
                serializer = BookingPersonalDeatils(data)
                return Response(serializer.data)

            else:
                data = PersonalDeatils.objects.filter(deleted=False, cancelled=False).order_by("-created_at")
                serializer = BookingPersonalDeatils(data, many=True)

                return Response(serializer.data)
    def post(self, request, format=None):
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            
            serializer = BookingPersonalDeatils(data=mutable_data)

            # Check if the data passed is valid
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Return Response to User

            response = Response()

            response.data = {
                'message': 'Personal deatils Created Successfully',
                'data': serializer.data
            }
            return response
    
    def patch(self, request, pk=None, format=None):
                # Get the todo to update
            Personal_deatils_to_update = PersonalDeatils.objects.get(pk=pk)

            serializer = BookingPersonalDeatils(instance=Personal_deatils_to_update,data=request.data, partial=True)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = Response()

            response.data = {
                'message': 'Persoanl deatils upated Successfully',
                'data': serializer.data
            }

            return response
    def delete(self, request, pk, format=None):
        personal_to_delete =  PersonalDeatils.objects.get(pk=pk)

            # delete the todo
        personal_to_delete.delete()

        return Response({
            'message': 'Personl deatils Deleted Successfully'
        })



class CoApplicantDeatilsApiview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return CoApplicantForm.objects.get(pk=pk)
        except CoApplicantForm.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = self.get_object(pk)
                serializer = CoApplicantForm(data)
                return Response(serializer.data)

            else:
                data = CoApplicantForm.objects.filter(deleted=False, cancelled=False).order_by("-created_at")
                serializer = CoApplicantFormSerializers(data, many=True)

                return Response(serializer.data)
    def post(self, request, format=None):
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            
            serializer = CoApplicantFormSerializers(data=mutable_data)

            # Check if the data passed is valid
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Return Response to User

            response = Response()

            response.data = {
                'message': 'co applicant form Created Successfully',
                'data': serializer.data
            }
            return response
    
    def patch(self, request, pk=None, format=None):
                # Get the todo to update
            Personal_deatils_to_update = CoApplicantForm.objects.get(pk=pk)

            serializer = CoApplicantFormSerializers(instance=Personal_deatils_to_update,data=request.data, partial=True)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = Response()

            response.data = {
                'message': 'co applicant upated Successfully',
                'data': serializer.data
            }

            return response
    def delete(self, request, pk, format=None):
        co_applicant_form_to_delete =  CoApplicantForm.objects.get(pk=pk)

            # delete the todo
        co_applicant_form_to_delete.delete()

        return Response({
            'message': 'co applicant Deleted Successfully'
        })
    


class BookingFiltersData(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = PersonalDeatils.objects.filter(deleted=False, cancelled=False)
    serializer_class = BookingPersonalDeatils
    filter_backends = [filters.DjangoFilterBackend,SearchFilter]
    filterset_class = PersonalDeatilsFilters
    search_fields = ['applicant_name']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).order_by("-created_at")
        
        if not queryset.exists():
            return Response({'detail': 'No data found'}, status=status.HTTP_204_NO_CONTENT)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

class CoApplicantFormByUnitNo(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, unit_id):
        co_applicants = CoApplicantForm.objects.filter(personal_deatils__booking__unit_no_id=unit_id, deleted=False, cancelled=False).order_by("-created_at")
        serializer = CoApplicantFormSerializers(co_applicants, many=True)
        return Response(serializer.data)



class AllDocumentApiview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return AllDocument.objects.get(pk=pk)
        except AllDocument.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = self.get_object(pk)
                serializer = AllDocument(data)
                return Response(serializer.data)

            else:
                data = AllDocument.objects.filter(deleted=False).order_by("-created_at")
                serializer = AllDocumentserializers(data, many=True)

                return Response(serializer.data)
    def post(self, request, format=None):
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            
            serializer = AllDocumentserializers(data=mutable_data)

            # Check if the data passed is valid
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Return Response to User

            response = Response()

            response.data = {
                'message': 'All Document form Created Successfully',
                'data': serializer.data
            }
            return response
    
    def patch(self, request, pk=None, format=None):
                # Get the todo to update
            AllDocument_to_update = AllDocument.objects.get(pk=pk)

            serializer = AllDocumentserializers(instance=AllDocument_to_update,data=request.data, partial=True)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = Response()

            response.data = {
                'message': 'All Document upated Successfully',
                'data': serializer.data
            }

            return response
    def delete(self, request, pk, format=None):
        co_applicant_form_to_delete =  AllDocument.objects.get(pk=pk)

            # delete the todo
        co_applicant_form_to_delete.delete()

        return Response({
            'message': 'All Document Deleted Successfully'
        })

# class GetUserBalance(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):

class DelBookingApiview(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk=None,):
        if not pk:
            booking_id = request.GET.get('booking_id')
        else:
            booking_id = pk
        booking = Booking.objects.get(id=booking_id)
        booking.deleted = True
        booking.save()

        presonal_details = PersonalDeatils.objects.filter(booking=booking)
        presonal_details.update(deleted = True)
        # presonal_details.save()

        coapplicant = CoApplicantForm.objects.filter(personal_deatils__in=presonal_details)
        coapplicant.update(deleted=True)

        paymentstage = PaymentStageDetail.objects.filter(personal_deatils__in=presonal_details)
        paymentstage.update(deleted = True)
        # paymentstage.save()

        paymentreceipts = PaymentReceipts.objects.filter(stage_deatils__in=paymentstage)
        paymentreceipts.update(deleted = True)
        # paymentreceipts.save()

        receipt = Receipt.objects.filter(payment_stage__in=paymentstage)
        receipt.update(deleted=True)

        demandletter = DemandLetter.objects.filter(payment_stage__in=paymentstage)
        demandletter.update(deleted=True)

        remainder_demand = RemiderDemandInformation.objects.filter(payment_receipts_stage__in=paymentreceipts)
        remainder_demand.update(deleted=True)

        unit_no = booking.unit_no

        site_workers = SiteWorkers.objects.filter(unit_no=unit_no)
        site_workers.update(deleted=True)

        monthly_expense = MonthlyExpense.objects.filter(siteworker__in=site_workers)
        monthly_expense.update(deleted=True)

        unit_no.available=True
        unit_no.booked=False
        unit_no.save()

        return Response({"message":"Your booking has been cancelled successfully."}, status=status.HTTP_200_OK)
    
class CancelBookingAPI(APIView):
    permssion_class = [IsAuthenticated]

    def post(self, request):
        unit_no = request.data.get('unit_no')
        project = Project.objects.get(pk=request.data['project_name'])
        unit_no = UnitNo.objects.get(unit_no=unit_no, projects=project)
        booking = Booking.objects.filter(unit_no=unit_no)
        
        mutable_data = request.data.copy()
        check_flag = False
        
        try:
            if float(mutable_data['total_refund_amt']) < float(mutable_data['refunded_amt']):
                return Response({"message":"Refund amount is more than it should be."}, status=status.HTTP_400_BAD_REQUEST)
        except:
            pass
            
        if booking.exists():
            if len(booking)>0:
                booking = booking.filter(cancelled=False)
            booking = booking.last()
            if booking.cancelled:
                check_flag = True
            else:
                booking.cancelled=True
                booking.save()
        else:
             return Response({"message":"Booking not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if not check_flag:
            personal_details = PersonalDeatils.objects.get(booking=booking)
            personal_details.cancelled=True
            personal_details.save()

            coapplicant = CoApplicantForm.objects.filter(personal_deatils=personal_details)
            coapplicant.update(cancelled=True)

            payment_stages = PaymentStageDetail.objects.filter(personal_deatils=personal_details)
            payment_stages.update(cancelled=True)

            receipt = Receipt.objects.filter(payment_stage__in=payment_stages)
            receipt.update(cancelled=True)

            demand_letter = DemandLetter.objects.filter(unit_number=unit_no)
            demand_letter.update(cancelled=True)
            
            unit_no.available = True        
            unit_no.booked = False
            unit_no.save()

            mutable_data['unit_no'] = unit_no.id
            mutable_data['booking'] = booking.id
            mutable_data['remaining_bal'] = float(mutable_data['total_refund_amt']) - float(mutable_data['refunded_amt'])
            serializer = CancelBookingSerializers(data=mutable_data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save()
            cancel_booking = CancelBooking.objects.get(pk=serializer.data['id'])
            cancel_booking.unit_no = unit_no
            cancel_booking.save()
            mutable_data['cancelbooking'] = serializer.data['id']

        else:
            cancel_booking = CancelBooking.objects.filter(unit_no=unit_no, booking=booking).last()
            remaining_bal = cancel_booking.remaining_bal - float(mutable_data['refunded_amt'])
            if remaining_bal<0:
                return Response({"message":"Refund amount is more than it should be."}, status=status.HTTP_400_BAD_REQUEST)

            cancel_booking.remaining_bal = remaining_bal
            cancel_booking.save()
            mutable_data['cancelbooking'] = cancel_booking.id

        try:
            last_receipt = CancelRefund.objects.all().last()
            new_receipt_no = int(last_receipt.reciept_no) + 1 if last_receipt else 1
        except Exception:
            new_receipt_no = 1

        formatted_receipt_no = f"{new_receipt_no:04d}"
        mutable_data['reciept_no'] = formatted_receipt_no

        refund_serializer = CancelRefundSerializers(data=mutable_data)
        if not refund_serializer.is_valid():
            return Response(refund_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        refund_serializer.save()
        
        if check_flag:
            return Response({"message":"Booking already cancelled. Refund amount updated successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"message":"Your booking has been cancelled successfully."}, status=status.HTTP_200_OK)
        
    def get(self, request):
        try:
            unit_no = request.GET.get('unit_no')
            unit_no = UnitNo.objects.get(unit_no=unit_no)
            booking = Booking.objects.filter(unit_no=unit_no)
        
            if booking.exists():
                booking = booking.last()
            else:
                return Response({"message":"Booking not found."}, status=status.HTTP_404_NOT_FOUND)
            
            cancel_booking = CancelBooking.objects.filter(unit_no=unit_no, booking=booking)
        except:
            cancel_booking = CancelBooking.objects.filter(deleted=False)

        serializer = CancelBookingSerializers(cancel_booking, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request):
        pk = request.data['id']
        if pk:
            cancel_booking = CancelBooking.objects.get(pk=pk)
        else:
            return Response({"message":"Invalid id."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = CancelBookingSerializers(cancel_booking, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request):
        pk = request.GET['id']
        refund = request.GET['refund_id']
        
        if pk:
            cancel_booking = CancelBooking.objects.get(pk=pk)
        else:
            return Response({"message":"Invalid cancellation id."}, status=status.HTTP_400_BAD_REQUEST)
        
        refund = CancelRefund.objects.get(pk=refund)
        refund.deleted = True
        refund.save()

        cancel_booking.remaining_bal += refund.refunded_amt
        cancel_booking.save()

        return Response({'meesage':'Refund entry removed successfully.'}, status=status.HTTP_200_OK)
    
class GenerateCancellationReport(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print(request.GET['doc_type'])
        try:
            cancel_booking = CancelBooking.objects.get(pk=request.GET.get('id'))
        except:
            return Response({"message": "Please check the cancellation ID."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CancelBookingSerializers(cancel_booking)
        data = serializer.data
        
        # Check the requested format
        export_format = request.GET.get("doc_type","word").lower()  # Default is Word
        
        if export_format == "pdf":
            return self.generate_pdf(data)
        elif export_format == "word":
            return self.generate_word(data)
        else:
            return Response({"message": "Invalid format. Use 'word' or 'pdf'."}, status=status.HTTP_400_BAD_REQUEST)

    def generate_word(self, data):
        document = Document()

        title = document.add_heading("CANCELLATION REPORT", level=1)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        current_date = f'Date: {datetime.now().strftime("%d-%m-%Y")}'
        date_paragraph = document.add_paragraph(current_date)
        date_paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        date_paragraph.runs[0].font.size = Pt(10)

        def add_section_in_box(doc, title, content):
            """
            Add a section with a heading and boxed content
            """
            table = doc.add_table(rows=1, cols=1)

            cell = table.cell(0, 0)
            heading = cell.add_paragraph(title)
            heading.runs[0].bold = True
            heading.runs[0].font.size = Pt(13)
            heading.alignment = WD_ALIGN_PARAGRAPH.LEFT

            for line in content:
                content_paragraph = cell.add_paragraph(line)
                content_paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                content_paragraph.runs[0].font.size = Pt(11)

            cell.vertical_alignment = WD_TABLE_ALIGNMENT.CENTER

        layout_table = document.add_table(rows=2, cols=2)
        layout_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        layout_table.style = "Table Grid"

        left_cell = layout_table.cell(0, 0)
        left_cell2 = layout_table.cell(1, 0)
        right_cell = layout_table.cell(0, 1)

        add_section_in_box(
            left_cell,
            "Customer Details",
            [
                f"Customer Name: {data['customer_name']}",
                f"Cancellation Date: {data['cancellation_date']}",
                f"Total Refund Amount: ₹{data['total_refund_amt']:,}",
                # f"Remaining Balance: ₹{data['remaining_bal']:,}",
            ],
        )

        add_section_in_box(
            left_cell2,
            "Applicant Details",
            [
                f"Applicant Name: {data['personal_details']['applicant_name']}",
                f"Present Address: {data['personal_details']['persent_address']}",
                f"Permanent Address: {data['personal_details']['permanent_address']}",
                f"Mobile Number: {data['personal_details']['mobile_number']}",
                f"Aadhar No.: {data['personal_details']['adhar_no']}",
            ],
        )

        add_section_in_box(
            right_cell,
            "Booking Details",
            [
                f"Project Name: {data['personal_details']['booking']['project_names']}",
                f"Type: {data['personal_details']['booking']['type_names']}",
                f"Unit Number: {data['personal_details']['booking']['unit_nos']}",
                # f"Cost Payable to Company: ₹{data['personal_details']['booking']['cost_payable_to_company']:,}",
            ],
        )

        document.add_paragraph("\n")
        refund_heading = document.add_heading("Refund Details", level=2)
        refund_heading.alignment = WD_ALIGN_PARAGRAPH.LEFT

        refund_table = document.add_table(rows=1, cols=7, style="Table Grid")
        headers = ["S.No.", "Receipt No.", "Refunded Amount", "Mode of Refund", "Cheque No.", "Date", "Bank Name"]
        hdr_cells = refund_table.rows[0].cells
        for i, header in enumerate(headers):
            hdr_cells[i].text = header
            hdr_cells[i].paragraphs[0].runs[0].bold = True

        for count, refund in enumerate(data["refund"], start=1):
            row_cells = refund_table.add_row().cells
            row_cells[0].text = str(count)
            row_cells[1].text = str(refund["reciept_no"])
            row_cells[2].text = f"₹{refund['refunded_amt']:,}"
            row_cells[3].text = refund["mode_of_refund"]
            row_cells[4].text = refund["cheque_no"] or "N/A"
            row_cells[5].text = refund["date"].split('T')[0]
            row_cells[6].text = refund["bank_name"]

        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        response["Content-Disposition"] = 'attachment; filename="refund_cancellation_report.docx"'
        document.save(response)

        return response

    def generate_pdf(self, data):
        # Set up PDF styles
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="refund_cancellation_report.pdf"'

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Title'],
            fontSize=16,
            alignment=1,
            spaceAfter=10,
            wordWrap='CJK'
        )
        normal_style = ParagraphStyle(
            'Normal',
            parent=styles['BodyText'],
            fontSize=10,
            spaceAfter=5,
        )
        section_heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=8,
        )
        table_style = TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("WORDWRAP", (0, 0), (-1, -1), "CJK"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )

        # Create PDF
        pdf = SimpleDocTemplate(response, pagesize=letter)
        elements = []

        # Add title
        elements.append(Paragraph("CANCELLATION REPORT", title_style))
        elements.append(Spacer(1, 20))

        # Add current date
        current_date = f"Date: {datetime.now().strftime('%d-%m-%Y')}"
        elements.append(Paragraph(current_date, normal_style))
        elements.append(Spacer(1, 20))

        # Define Customer and Booking Details as a side-by-side table (without border)
        customer_booking_table = [
            [
                Paragraph(
                    "<b>Customer Details</b><br/>"
                    f"Customer Name: {data['customer_name']}<br/>"
                    f"Cancellation Date: {data['cancellation_date']}<br/>"
                    f"Total Refund Amount: Rs. {data['total_refund_amt']:,}",
                    normal_style,
                ),
                Paragraph(
                    "<b>Booking Details</b><br/>"
                    f"Project Name: {data['personal_details']['booking']['project_names']}<br/>"
                    f"Type: {data['personal_details']['booking']['type_names']}<br/>"
                    f"Unit Number: {data['personal_details']['booking']['unit_nos']}",
                    normal_style,
                ),
            ]
        ]

        table = Table(customer_booking_table, colWidths=[250, 250])
        table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black), 
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        elements.append(table)
        # elements.append(Spacer(1, 20))

        # Add Applicant Details
        applicant_details_data = [
            [
                Paragraph(
                    "<b>Applicant Details</b><br/>"
                    f"Applicant Name: {data['personal_details']['applicant_name']}<br/>"
                    f"Present Address: {data['personal_details']['persent_address']}<br/>"
                    f"Permanent Address: {data['personal_details']['permanent_address']}<br/>"
                    f"Mobile Number: {data['personal_details']['mobile_number']}<br/>"
                    f"Aadhar No.: {data['personal_details']['adhar_no']}",
                    normal_style,
                )
            ]
        ]

        applicant_details_table = Table(applicant_details_data, colWidths=[500])
        applicant_details_table.setStyle(
            TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),  # Add grid/border
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ])
        )
        elements.append(applicant_details_table)
        elements.append(Spacer(1, 20))

        # Add Refund Details Table
        elements.append(Paragraph("<b>Refund Details</b>", section_heading_style))
        refund_data = [["S.No.", "Receipt No.", "Refunded Amount", "Mode of Refund", "Cheque No.", "Date", "Bank Name"]]
        for count, refund in enumerate(data["refund"], start=1):
            refund_data.append(
                [
                    str(count),
                    refund["reciept_no"],
                    f"Rs. {refund['refunded_amt']:,}",
                    refund["mode_of_refund"],
                    refund["cheque_no"] or "N/A",
                    refund["date"].split("T")[0],
                    refund["bank_name"],
                ]
            )

        refund_table = Table(refund_data, colWidths=[40, 80, 100, 80, 80, 80, 100])
        refund_table.setStyle(table_style)
        elements.append(refund_table)

        # Build PDF
        pdf.build(elements)
        return response
