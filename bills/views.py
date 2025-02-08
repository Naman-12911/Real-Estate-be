from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http.response import Http404
from rest_framework.response import Response
from .models import *
from .serializer import *
from social.fcm_manager import sendPush
from account.models import *
from rest_framework import status
from django.db.models import Count,Sum,Q,Func, IntegerField
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from openpyxl import Workbook
import openpyxl
from django.http import HttpResponse
from civilWorker.models import *
from datetime import datetime, date
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.cell.cell import MergedCell
import tempfile, os
from django.core.files.base import ContentFile
import inflect

# Create your views here.
class ProjectsApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pk = request.GET.get('pk')
        constructor_id = request.GET.get('constructor')
        if pk:
            query = ConstProject.objects.filter(id=pk)
        else:
            query = ConstProject.objects.filter(constructor__id=constructor_id)

        serializer = ConstProjectSerializer(query, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    
    def post(self, request):
        serializer = ConstProjectSerializer(data=request.data)
    
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        pk = request.GET.get('pk')
        try:
            const_project = ConstProject.objects.get(pk=pk)
        except ConstProject.DoesNotExist:
            return Response({'error': 'ConstProject not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ConstProjectSerializer(const_project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


        
class ConstBillAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def calculate_total_amount(self, project_id):
        # Sum the 'amount' of all previous bills for this project using project__id
        previous_bills = ConstBill.objects.filter(project__id=project_id)
        total_amount = previous_bills.aggregate(total=Sum('amount'))['total'] or 0
        prev_amount = previous_bills.filter(billed=True).aggregate(total=Sum('amount'))['total'] or 0
        return total_amount, prev_amount


    def get(self, request):
        pk =  request.GET.get('pk')
        project = request.GET.get('project')
        if pk:
            try:
                const_bill = ConstBill.objects.get(pk=pk)
                serializer = ConstBillSerializer(const_bill)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except ConstBill.DoesNotExist:
                return Response({'error': 'ConstBill not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            const_bills = ConstBill.objects.filter(project__id=project)
            serializer = ConstBillSerializer(const_bills, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    # POST request to create a new ConstBill
    def post(self, request):
        mutable_data = request.data.copy()
        # bills = ConstBill.objects.filter(project__id=mutable_data['project'])
        bills = ConstBill.objects.filter(project__constructor__id=mutable_data['constructor'])
        mutable_data['bill_no'] = "RA - "+str(len(bills)+1) 
        serializer = ConstBillSerializer(data=mutable_data)
        if serializer.is_valid():
            # Calculate the total_amount for the associated project
            project_id = serializer.validated_data['project'].id
            current_amount = serializer.validated_data['amount']
            
            # Sum of all previous bills + current bill's amount
            total_amount, prev_amount = self.calculate_total_amount(project_id)
            total_amount += current_amount
            # Set total_amount in serializer before saving
            serializer.save(total_amount=total_amount, prev_total_amount=prev_amount)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PUT request to update an existing ConstBill
    def put(self, request):
        pk =  request.GET.get('pk')

        try:
            const_bill = ConstBill.objects.get(pk=pk)
        except ConstBill.DoesNotExist:
            return Response({'error': 'ConstBill not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ConstBillSerializer(const_bill, data=request.data, partial=True)
        if serializer.is_valid():
            # Calculate the total_amount for the associated project
            project_id = const_bill.project.id
            current_amount = serializer.validated_data.get('amount', const_bill.amount)
            
            # Sum of all previous bills (excluding the current bill being updated) + current bill's new amount
            total_amount = (self.calculate_total_amount(project_id)[0] - const_bill.amount) + current_amount
            
            # Set total_amount in serializer before saving
            serializer.save(total_amount=total_amount, billed=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExcelBillsAPI(APIView):
    permission_classes = [IsAuthenticated]

    # Define a function to apply alignment to a range of cells
    def apply_alignment(self, ws, cell_range, alignment):
        for row in ws[cell_range]:
            for cell in row:
                cell.alignment = alignment

    def convert_number_to_words(self, amount):
        p = inflect.engine()

        # Split amount into integer and decimal parts
        integer_part = int(amount)
        
        # Convert the integer part to words
        words = p.number_to_words(integer_part, andword='').replace(',', '')
        
        # Convert to the Indian numbering format
        words = words.replace('thousand', 'Thousand').replace('lakh', 'Lakh').replace('crore', 'Crore')

        # Capitalize first letter
        words = words.capitalize()

        # Append "Rupees Only" to the end
        return words + " Rupees Only"

    def get(self, request):
        constructor_id = request.GET.get('constructor')
        preview = request.GET.get('preview')
        try:
            constructor = ConstructorProfile.objects.get(id=constructor_id)
            projects = ConstProject.objects.filter(constructor__id=constructor_id)
        except:
            return Response({"error":"No project found"}, status=status.HTTP_400_BAD_REQUEST)
        works = ConstBill.objects.filter(project__in=projects)
        exported_bills = BillsExported.objects.filter(constructor_profile=constructor)
        bill_no = len(exported_bills)+1
        # Create a new Excel workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = f"Bill {bill_no}"

        # Set column widths
        ws.column_dimensions['A'].width = 7
        ws.column_dimensions['B'].width = 20
        ws.column_dimensions['C'].width = 5
        ws.column_dimensions['D'].width = 15
        ws.column_dimensions['E'].width = 15
        ws.column_dimensions['F'].width = 15

        # Add bill header
        ws.merge_cells('A1:F1')
        ws['A1'] = "CI REAL ESTATE"
        ws['A1'].font = Font(bold=True, size=14)
        ws['A1'].alignment = Alignment(horizontal='center')

        ws.merge_cells('A2:E2')
        ws.merge_cells('A3:E3')
        ws.merge_cells('A4:F4')
        ws.merge_cells('A5:F5')
        ws.merge_cells('A6:F6')
        ws['A2'] = f"PAN No.: "
        ws['F2'] = f"Date: {datetime.today().date()}"

        ws['A3'] = f"Bill No.: RA-{bill_no}"
        ws['A4'] = f"Name of Contractor: {constructor.name}"

        ws['A5'] = f"Name of Site: CI GRAND"
        ws['A6'] = f"Name of Work: DEVELOPMENT WORK"
        green_fill = PatternFill(start_color="00FF00", end_color="00FF00", fill_type="solid")
        yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
        # Add table header'Quantity', 'Unit', 'Rate',
        headers = ['Sr. No', 'Work', "", 'Total Work Done Amount', 'Pre Bill Amount', 'This Bill Amount']
        ws.append(headers)
        ws.merge_cells('B7:C7')

        thick_border = Border(left=Side(style='thick'), right=Side(style='thick'), top=Side(style='thick'), bottom=Side(style='thick'))
        for col in range(1, 7):
            ws.cell(row=7, column=col).border = thick_border
        # Add table data
        thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        total_amount_all = 0
        total_amount_this = 0
        pre_bill_amount_all = 0
        count = 8
        to_save = False
        works_found = False
        for index, proj in enumerate(projects, start=1):
            work = ConstBill.objects.filter(project=proj).last()
            if work:
                works_found=True
                if work.billed:
                    pre_bill_amount = float(work.total_amount)
                    amount = 0
                else:
                    old_works = ConstBill.objects.filter(project=proj)
                    to_save = True
                    pre_bill_amount = old_works.filter(billed=True).aggregate(total=Sum('amount'))['total'] or 0
                    amount = old_works.filter(billed=False).aggregate(total=Sum('amount'))['total'] or 0
                    # proj.quantity,
                    # proj.unit,
                    # proj.rate,
                ws.append([
                    index,
                    proj.name,
                    "",
                    work.total_amount,
                    pre_bill_amount,
                    amount
                ])
                ws.merge_cells(f'B{index + 7}:C{index + 7}')
                
                ws.cell(row=index + 7, column=2).fill = yellow_fill
                for col in range(1, 7):
                    ws.cell(row=index + 7, column=col).border = thin_border

                # work.billed = True
                # work.save()
                # if not preview:
                #     ConstBill.objects.filter(project=proj).update(billed=True)
                total_amount_all+=work.total_amount
                total_amount_this+=amount
                pre_bill_amount_all+=pre_bill_amount


        if not works_found:
            return Response({"error":"Please add an amount to generate bill."}, status=status.HTTP_400_BAD_REQUEST)
        # Calculate totals and discounts
        discount = total_amount_all*((5.08)/100)
        discount_this = total_amount_this*((5.08)/100)
        discounted_total = total_amount_all - discount
        discounted_total_this = total_amount_this - discount_this

        ws.append([ '', 'Amount Rs.:',"",  total_amount_all, pre_bill_amount_all, total_amount_this])
        ws.append([ '', 'Less Discount 5.08%:', "", discount, "", discount_this])
        ws.append([ '', 'Total Amount Rs.:',"", discounted_total,"", discounted_total_this])
        cell_no = 8+len(projects)
        ws.merge_cells(f'B{cell_no}:C{cell_no}')
        ws.merge_cells(f'B{cell_no+1}:C{cell_no+1}')
        ws.merge_cells(f'B{cell_no+2}:C{cell_no+2}')
        ws.cell(row=ws.max_row, column=6).fill = green_fill

        cell_no = 11+len(projects)
        ws.merge_cells(f'A{cell_no}:C{cell_no}')
        ws.merge_cells(f'D{cell_no}:E{cell_no}')
        ws[f'A{cell_no}'] = f"Billing Engineer"
        ws[f'D{cell_no}'] = f"Site Engineer"
        ws[f'F{cell_no}'] = f"Contractor"

        ws_invoice = wb.create_sheet(title="Invoice")

        # Define thin and thick borders
        thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        thick_border = Border(left=Side(style='medium'), right=Side(style='medium'), top=Side(style='medium'), bottom=Side(style='medium'))

        # Merge cells for structured layout
        ws_invoice.merge_cells('B11:C11')  # Company Name
        ws_invoice.merge_cells('B12:C12')  # Company Address
        ws_invoice.merge_cells('B13:C13')  # Company GST

        # Content for cells
        ws_invoice['B10'] = f'Bill no. : RA-{bill_no}'
        ws_invoice['C10'] = f'Date:- {datetime.today().date().strftime("%d-%m-%Y")}'
        ws_invoice['B11'] = 'To,'
        ws_invoice['B12'] = 'C I Real Estate'
        ws_invoice['B13'] = 'Bhopal'
        ws_invoice['B14'] = 'GST:- 23AAMFC8562F1ZD'

        # Style for bold fonts
        bold_font = Font(bold=True)
        ws_invoice['B10'].font = bold_font
        ws_invoice['C10'].font = bold_font
        ws_invoice['B11'].font = bold_font
        ws_invoice['B14'].font = bold_font

        # total_amount = 0

        # Adjusting project details
        for index, proj in enumerate(projects, start=1):
            old_works = ConstBill.objects.filter(project=proj)
            ws_invoice[f'A{14+index}'] = index
            ws_invoice[f'B{14+index}'] = proj.name
            ws_invoice[f'C{14+index}'] = old_works.filter(billed=False).aggregate(total=Sum('amount'))['total'] or 0
            ws_invoice[f'A{14+index}'].font = bold_font
            ws_invoice[f'B{14+index}'].font = bold_font
            # total_amount += work.total_amount
            if not preview:
                ConstBill.objects.filter(project=proj).update(billed=True)
        
        # Tax Calculations and Total
        ws_invoice[f'B{15+index}'] = "Total Amount"
        ws_invoice[f'C{15+index}'] = total_amount_this
        disc = total_amount_this*0.0508
        total_amount_this = total_amount_this - disc
        cgst = total_amount_this * 0.09
        sgst = total_amount_this * 0.09
        tds = total_amount_this * 0.01
        final_total = total_amount_this + cgst + sgst - tds

        # Add CGST, SGST, and total
        
        ws_invoice[f'C{15+index}'].font = bold_font
        ws_invoice[f'B{15+index}'].font = bold_font
        ws_invoice[f'B{17+index}'] = "Less Discount 5.08%"
        ws_invoice[f'C{17+index}'] = disc
        ws_invoice[f'B{18+index}'] = 'Add CGST 9 %'
        ws_invoice[f'C{18+index}'] = cgst
        ws_invoice[f'B{19+index}'] = 'Add SGST 9 %'
        ws_invoice[f'C{19+index}'] = sgst
        ws_invoice[f'B{20+index}'] = 'TDS 1%'
        ws_invoice[f'C{20+index}'] = tds
        ws_invoice[f'B{21+index}'] = 'Total Amount'
        ws_invoice[f'C{21+index}'] = final_total

        # Merge for final amount in words
        ws_invoice.merge_cells(f'A{23+index}:C{23+index}')
        ws_invoice[f'A{23+index}'] = 'Amount Including all taxes.'
        ws_invoice.merge_cells(f'A{24+index}:C{24+index}')
        ws_invoice[f'A{24+index}'] = f'Amount: {self.convert_number_to_words(final_total)}'

        # Apply borders to cells
        for row in ws_invoice[f'B10:C{24+index}']:
            for cell in row:
                cell.border = thin_border

        # Apply thick border for total amount
        for row in ws_invoice[f'B17:C17']:
            for cell in row:
                cell.border = thick_border

        # Align text properly
        left_alignment = Alignment(horizontal='left')
        right_alignment = Alignment(horizontal='right')
        center_alignment = Alignment(horizontal='center')

        # Apply alignments
        for row in ws_invoice[f'B10:B{24+index}']:
            for cell in row:
                cell.alignment = left_alignment

        for row in ws_invoice[f'C10:C{24+index}']:
            for cell in row:
                cell.alignment = right_alignment
        # ws_invoice[f'B17'].alignment = center_alignment  # Center align total amount heading

        # Set bold font for important values
        # ws_invoice[f'B17'].font = bold_font
        # ws_invoice[f'C17'].font = bold_font

        # Set column widths for better presentation
        ws_invoice.column_dimensions['B'].width = 40
        ws_invoice.column_dimensions['C'].width = 20

        # Optional: Add thicker borders around the main body (for a cleaner look)
        for row in ws_invoice[f'A14:C{17+index}']:
            for cell in row:
                cell.border = thick_border
       

        # Save the workbook to the response
        if to_save and not preview:
             # Set the response to return the Excel file
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename=bill_{bill_no}.xlsx'
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
            wb.save(temp_file.name)
            with open(temp_file.name, 'rb') as f:
                file_content = ContentFile(f.read(), name=f'RA_{constructor.name}_Bill_{constructor_id}.xlsx')

                # Create an instance of InvoiceCivilStages
                invoice_instance = BillsExported(
                    constructor_profile=constructor,
                    bill=file_content,
                    bill_no=f"RA-{bill_no}"
                )
                invoice_instance.save()

            # Add the units to the instance
            os.remove(temp_file.name)
            wb.save(response)
        
        if preview:
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename=bill_RA-{bill_no}.xlsx'
            
            wb.save(response)
        
        if to_save or preview:
            return response
        
        return Response({"error":"This bill has already been genrated."}, status=status.HTTP_400_BAD_REQUEST)

class BillsExportedListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Get constructor ID from query parameters
        constructor_id = request.query_params.get('constructor')
        
        if not constructor_id:
            bills = BillsExported.objects.all()
        else:
            bills = BillsExported.objects.filter(constructor_profile__id=constructor_id)
        
        # If no bills found for the given constructor ID
        if not bills.exists():
            return Response({"message": "No bills found for this constructor"}, status=status.HTTP_404_NOT_FOUND)
        
        # Serialize the data
        serializer = BillsExportedSerializer(bills, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)