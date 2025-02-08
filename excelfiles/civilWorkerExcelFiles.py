from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.http import HttpResponse
from django.utils.dateparse import parse_date
from io import BytesIO
import pandas as pd
from civilWorker.models import *
from .serializer import *
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Alignment
from .serializer import *
from rest_framework.response import Response
from rest_framework import status
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Alignment, Font, Border, Side
from django.core.files.base import ContentFile
import os
from reportlab.lib.units import inch
from django.http.response import Http404
from civilWorker.serializer import *
from civilWorker.filters import ExcelFilesDownloadFilter,InvoiceCivilStagesFilter
from num2words import num2words
from openpyxl.utils import get_column_letter
from datetime import datetime, date
from openpyxl.styles import PatternFill
import tempfile
from .helper import filter_rows_with_fewest_missing, sort_key
from django.db.models import Q

class ContractorBillsAPIview(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        contractor_id = request.query_params.get('contractor_id')
        unit_nos = request.query_params.getlist('unit_no')

        if not contractor_id:
            return Response({"error": "Contractor ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            contractor_id = int(contractor_id)
        except ValueError:
            return Response({"error": "Invalid Contractor ID."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            contractor_profile = ConstructorProfile.objects.get(id=contractor_id)
        except ConstructorProfile.DoesNotExist:
            return Response({"error": "Contractor Profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Filter CivilStages by contractor_id and optionally by unit_nos
        if unit_nos:
            civil_stages = CivilStatges.objects.filter(
                constructor_profile_id=contractor_id,
                unit__unit_no__in=unit_nos
            ).order_by('-created_at')
        else:
            civil_stages = CivilStatges.objects.filter(
                constructor_profile_id=contractor_id
            ).order_by('-created_at')

        civil_stages_check = civil_stages.filter(
            Q(completed_stage_1=1) | 
            Q(completed_stage_2=1) | 
            Q(completed_stage_3=1) | 
            Q(completed_stage_4=1) | 
            Q(completed_stage_5=1) | 
            Q(completed_stage_6=1) | 
            Q(completed_stage_7=1) | 
            Q(completed_stage_8=1) | 
            Q(completed_stage_9=1) | 
            Q(completed_stage_10=1) | 
            Q(completed_stage_11=1)
            )
        if not civil_stages_check.exists():
            return Response({"message":"There's no bill to generate."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            constructor_profile = ConstructorProfile.objects.get(id=contractor_id)
        except ConstructorProfile.DoesNotExist:
            # return Response({"error": "Contractor Profile not found."}, status=status.HTTP_404_NOT_FOUND)
            constructor_profile = ConstructorProfile.objects.all().last()
            contractor_id = constructor_profile.id


        if unit_nos:
            query = CivilStatges.objects.filter(constructor_profile__id=contractor_id, unit__unit_no__in=unit_nos)
        else:
            query = CivilStatges.objects.filter(constructor_profile__id=contractor_id)

        rows = []
        # stages_set = set()
        stages_set = []

        total_amount_sum = 0
        prev_bill_sum = 0
        this_bill_sum = 0
        prev_bill_dict = {}
        
        green_fill = PatternFill(start_color="00FF00", end_color="00FF00", fill_type="solid")

        # Fetch the last entry for the same contractor
        last_excel_record = ExcelFilesCivilStages.objects.filter(constructor_profile=contractor_profile)
        file_same = False # to identify if the file has been saved before
        prev_bill_values = {}
        df_misc = pd.DataFrame()
        if len(last_excel_record)>0:
            # prev_bill_values = last_excel_record.prev_bill
            df_old = pd.DataFrame()
            for bills in last_excel_record:
                excel_path = bills.file.path
                df1 = pd.read_excel(excel_path, skiprows=4)
                df_old = pd.concat([df_old,df1], ignore_index=False)
            df_old.drop_duplicates(inplace=True)
            
            df_misc = df1[(df1['Sr No'].isnull()) & (~df1['Rate'].isnull()) & (~df1['This Bill'].isnull())]
            
            df_old = df_old[~((df_old['Sr No'].isnull()) & (df_old['Total Percentage'].isnull()))]
            df_check = df_old[~(df_old['Sr No'].isnull())]
            df_check['Sr No'] = df_check['Sr No'].astype(int).astype(str)
            df_check['Rate'] = df_check['Rate'].astype(int)
            df_check = df_check[df_check.columns[:-1]]

            df_check.drop_duplicates(inplace=True)
            units_no = [str(int(i)) for i in unit_nos]
            if unit_nos:
                df_check = df_check[df_check['Sr No'].isin(units_no)]

            df_check = df_check.groupby('Sr No').apply(filter_rows_with_fewest_missing).reset_index(drop=True)
            df_check.drop_duplicates(subset=df_check.columns[:-2], keep='last', inplace=True)
            
            if len(df_check)>0:
                count = 1
                for sr in df_check['Sr No'].unique():
                    df_sub = df_check[df_check['Sr No']==sr]
                    # prev_bill_values[f'row_{count}'] = df_sub['This Bill'].to_list()[-1]
                    prev_bill_values[sr] = df_sub['This Bill'].to_list()[-1]


        # Track newly added completed stages
        newly_completed_stages = set()
        stage_dict = {}
        for idx, stage in enumerate(civil_stages, start=1):
            area = float(stage.unit.square_fit if stage.unit.square_fit else 0.0)
            rate = float(stage.unit.rate if stage.unit.rate else 0.0)
            total_percentage = 0
            sr_1 = stage.unit.unit_no if stage.unit else ''
            try:
                # prev_bill_value = prev_bill_values[str(int(sr_1))]
                prev_row_amt = df_check[df_check['Sr No']==str(int(sr_1))]['Total Amount'].to_list()[0]
            except Exception as e:
                # prev_bill_value = 0
                prev_row_amt = 0
            row = {
                'Sr No': stage.unit.unit_no if stage.unit else '',
                'Area': area,
                'Rate': rate,
                'Total Percentage': 0,
                'Total Amount': 0,
                'Prv Bill Amount': prev_row_amt,
                'This Bill': 0,
                'Remarks': stage.remark.title if stage.remark else ''
            }

            current_stage_set = set()
            for i in range(1, 12):
                stage_name = getattr(stage, f'stage{i}', '')
                try:
                    percentage = float(getattr(stage, f'percentage_stage_{i}', 0))
                except:
                    percentage = 0
                completed = getattr(stage, f'completed_stage_{i}', False)
                if stage_name:
                    row[stage_name] = f"{percentage}%" if completed else ''
                    # stages_set.add(stage_name)
                    stage_dict[i] = stage_name
                    # if stage_name not in stages_set:
                    #     print(stage_name)
                    #     stages_set.append(stage_name)
                    if completed:
                        current_stage_set.add(stage_name)
                        total_percentage += percentage

            # Identify newly completed stages
            for stage_name in current_stage_set:
                if stage_name not in prev_bill_values or not prev_bill_values[stage_name]:
                    newly_completed_stages.add(stage_name)
            row['Total Percentage'] = f"{total_percentage}%"
            row['Total Amount'] = int(area * rate * (total_percentage / 100))
            if prev_row_amt==0:
                row['This Bill'] = row['Total Amount'] - row['Prv Bill Amount']
            else:
                row['This Bill'] = row['Total Amount'] - prev_row_amt
            prev_bill_dict[f'row_{idx}'] = row['Total Amount']

            total_amount_sum += row['Total Amount']
            prev_bill_sum += row['Prv Bill Amount']
            this_bill_sum += row['This Bill']

            rows.append(row)
        sorted_dict = {k: stage_dict[k] for k in sorted(stage_dict)}
        stages_set = sorted_dict.values()
        # Fetch miscellaneous data
        miscellaneous_records = Miscellaneous.objects.filter(unit__in=[stage.unit for stage in civil_stages], delete=False)

        for misc in miscellaneous_records:
            if misc.prev_bill:
                row = {
                    'Sr No': '',
                    'Area': '',
                    'Rate': misc.title,
                    'Total Percentage': '',
                    'Total Amount': misc.amount,
                    'Prv Bill Amount': misc.amount,
                    'This Bill': 0,
                    'Remarks': ''
                }
            else:
                row = {
                    'Sr No': '',
                    'Area': '',
                    'Rate': misc.title,
                    'Total Percentage': '',
                    'Total Amount': misc.amount,
                    'Prv Bill Amount': 0,
                    'This Bill': misc.amount,
                    'Remarks': ''
                }
                # misc.prev_bill = True
                # misc.save()
            rows.append(row)
        df = pd.DataFrame(rows)
        try : 
            df_check_new = df_check.copy()
            df_check_new['Rate'] = df_check_new['Rate'].astype(float)
            df_check_new.fillna("", inplace=True)
            df_new_check = df.copy()
            df_new_check = df_new_check[(~df_new_check['Sr No'].isnull()) & (df_new_check['Sr No']!='')]
            df_new_check.drop(columns=['Total Percentage', 'Total Amount', 'Prv Bill Amount', 'This Bill', 'Remarks'], inplace=True)
            df_new_check['Sr No'] = df_new_check['Sr No'].astype(int).astype(str)
            df_check_new.drop(columns=['Total Percentage', 'Total Amount', 'Prv Bill Amount', 'This Bill'], inplace=True)
            df_check_new.fillna('', inplace=True)
            df_new_check.fillna('', inplace=True)
            merged_df = df_new_check.merge(df_check_new, how='left', indicator=True)
            all_rows_in_df1 = merged_df['_merge'].eq('both').all()
            if all_rows_in_df1:
                file_same = True
            
        except Exception as e:
            print(e)
        df = df.sort_values(
                by='Sr No',
                key=lambda x: x.map(lambda val: float('inf') if pd.isna(val) or val == '' else int(val)),
                na_position='last'
            ).reset_index(drop=True)
        try:
            # df_check['Sr No'] = sorted(df_check['Sr No'], key=sort_key)
            df_check = df_check.sort_values(
                by='Sr No',
                key=lambda x: x.map(lambda val: float('inf') if pd.isna(val) or val == '' else int(val)),
                na_position='last'
            ).reset_index(drop=True)
        except:
            pass
        if not file_same:
            for misc in miscellaneous_records:
                if not misc.prev_bill:
                    misc.prev_bill = True
                    misc.save()
        for stage_name in stages_set:
            if stage_name not in df.columns:
                df[stage_name] = "0%"

        ordered_columns = ['Sr No', 'Area', 'Rate'] + list(stages_set) + [
            'Total Percentage', 'Total Amount', 'Prv Bill Amount', 'This Bill', 'Remarks'
        ]
        df = df[ordered_columns]
        # Values from the image for the stages
        stage_values = ['10%', '10%', '10%', '10%', '5%', '10%', '15%', '10%', '5%', '10%', '5%']

        # Create a dictionary for the new row with values for the stages and empty strings for the rest
        new_row = {col: "" for col in ordered_columns}
        for stage, value in zip(stages_set, stage_values):
            new_row[stage] = value

        new_row["Total Percentage"] = "100%"

        # Convert the new row to a DataFrame
        new_row_df = pd.DataFrame([new_row])
        df_totals = {
            'Total Amount': df['Total Amount'].sum(),
            'Prv Bill Amount': df['Prv Bill Amount'].sum(),
            'This Bill': df['This Bill'].sum(),
        }

        df = pd.concat([new_row_df,df]).reset_index(drop=True)
        # df = df.sort_values('Sr No')
        total_sum_of_total_amount = df_totals['Total Amount']
        total_sum_of_pre_bill_amount = df_totals['Prv Bill Amount']
        total_sum_of_this_bill = df_totals['This Bill']

        discount = contractor_profile.discount
        total_this_bill = total_sum_of_total_amount - total_sum_of_pre_bill_amount
        discounted_amount = total_this_bill * (discount / 100)
        total_sum = total_this_bill - discounted_amount
        gst = total_sum * 0.18
        total_with_gst = total_sum + gst
        #total_with_gst = total_sum 
        # less_1_percenatge_gst = total_with_gst * (1 / 100)
        less_1_percenatge_gst = total_sum * (1 / 100)
        final_total_amount = total_with_gst - less_1_percenatge_gst


        output = BytesIO()
        wb = Workbook()
        ws = wb.active
        ws.title = contractor_profile.name

        header_font = Font(bold=True, size=16)
        header_contactor_profile = Font(bold=True, size=24)
        bill_count = ExcelFilesCivilStages.objects.filter(constructor_profile=contractor_profile).count()
        bill_number = f"{bill_count + 1:02d}"

        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(ordered_columns))
        ws.cell(row=1, column=1).value = f"{contractor_profile.name}"
        ws.cell(row=1, column=1).font = header_contactor_profile
        ws.cell(row=1, column=1).alignment = Alignment(horizontal='center')

        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(ordered_columns))
        ws.cell(row=2, column=1).value = f"Date: {datetime.now().strftime('%d/%m/%y')}"
        ws.cell(row=2, column=1).font = header_font
        ws.cell(row=2, column=1).alignment = Alignment(horizontal='left')

        ws.merge_cells(start_row=3, start_column=1, end_row=3, end_column=len(ordered_columns))
        ws.cell(row=3, column=1).value = f"RA Bill No: {bill_number}"
        ws.cell(row=3, column=1).font = header_font
        ws.cell(row=3, column=1).alignment = Alignment(horizontal='right')

        thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        bold_border = Border(left=Side(style='medium'), right=Side(style='medium'), top=Side(style='medium'), bottom=Side(style='medium'))
        # print(df)
        # print(df_old)
        for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), 5):
            for c_idx, value in enumerate(row, 1):
                cell = ws.cell(row=r_idx, column=c_idx, value=value)
                if r_idx == 5:
                    cell.font = Font(bold=True, size=14)
                    ws.column_dimensions[cell.column_letter].width = 15
                    cell.border = bold_border
                else:
                    if any(misc.title == cell.value for misc in miscellaneous_records):
                        cell.border = None
                    else:
                        cell.border = thin_border
                cell.alignment = Alignment(horizontal='center', vertical='center')
                if r_idx > 5:
                    cell.font = Font(size=12)
                if r_idx == 6:
                    cell.font = Font(size=12, color="0000FF")
               # Apply green fill for newly completed stages
                column_name = ordered_columns[c_idx - 1]
                # if column_name in newly_completed_stages:
                #     cell.fill = green_fill
                try:
                    if r_idx>6:
                        if pd.isna(df_check.loc[df_check['Sr No']==str(int(df.loc[r_idx-6,'Sr No'])), column_name].to_list()[0]) and df_check.loc[df_check['Sr No']==str(int(df.loc[r_idx-6,'Sr No'])), column_name]=="" and not pd.isna(value) and value!="" and value not in ordered_columns and column_name in stages_set:
                            cell.fill = green_fill
                        elif len(df_check[df_check['Sr No']==str(int(df.loc[r_idx-6,'Sr No']))])==0 and not pd.isna(value) and value!="" and value not in ordered_columns and column_name in stages_set:
                            cell.fill = green_fill
                except Exception as e:
                    print(e)
                    try:
                        if column_name in stages_set and not pd.isna(value) and value!="" and value not in ordered_columns:
                            cell.fill = green_fill
                    except:
                        pass
        last_row = len(df) + 6
        total_font = Font(bold=True, size=14)

        row_offset = last_row
        for col_name in ['Total Amount', 'Prv Bill Amount', 'This Bill']:
            col_idx = ordered_columns.index(col_name) + 1
            ws.cell(row=row_offset, column=col_idx, value=df_totals[col_name]).font = total_font
            ws.cell(row=row_offset, column=col_idx).border = bold_border
            ws.cell(row=row_offset, column=col_idx).alignment = Alignment(horizontal='center', vertical='center')

        # total_amt = total_sum - discounted_amount
        additional_totals = [
            ("This Bill Amount", total_this_bill),
            (f"Below ({discount}%)", discounted_amount),
            (f"Total Amount", total_sum),
            ("Add 18% GST", gst),
            ("Total Amount with GST", total_with_gst),
            ("Less TDS 1%", less_1_percenatge_gst),
            ("Total Amount", final_total_amount)
        ]

        for i, (label, value) in enumerate(additional_totals):
            row_offset = last_row + 2 + i
            ws.cell(row=row_offset, column=len(ordered_columns) - 3, value=label).font = total_font
            ws.cell(row=row_offset, column=len(ordered_columns) - 2, value=value).font = total_font
            ws.cell(row=row_offset, column=len(ordered_columns) - 3).border = bold_border
            ws.cell(row=row_offset, column=len(ordered_columns) - 2).border = bold_border
            ws.cell(row=row_offset, column=len(ordered_columns) - 3).alignment = Alignment(horizontal='center', vertical='center')
            ws.cell(row=row_offset, column=len(ordered_columns) - 2).alignment = Alignment(horizontal='center', vertical='center')
            if label == "Total Amount":
                ws.cell(row=row_offset, column=len(ordered_columns) - 2).fill = green_fill
                ws.cell(row=row_offset, column=len(ordered_columns) - 3).fill = green_fill

        ws_invoice = wb.create_sheet(title="Invoice")

        # Set up the worksheet content
        ws_invoice['A1'] = constructor_profile.name
        ws_invoice['A1'].font = Font(bold=True,size=24)
        ws_invoice.merge_cells('A1:F1')

        ws_invoice['A2'] = 'Tax Invoice'
        ws_invoice['A2'].font = Font(bold=True)
        ws_invoice['E4'] = f'Date: {date.today()}'
        ws_invoice.merge_cells('A2:F2')

        ws_invoice['A4'] = 'TO,'
        ws_invoice['A4'].font = Font(bold=True)

        ws_invoice['A5'] = 'C.I. REAL ESTATE'
        ws_invoice['A5'].font = Font(bold=True)

        ws_invoice['A6'] = f'GST: {constructor_profile.gst}'

        ws_invoice['A7'] = 'M.P. NAGAR, BHOPAL'

        ws_invoice['A8'] = 'From,'
        ws_invoice['A8'].font = Font(bold=True)

        ws_invoice['A9'] = constructor_profile.name

        ws_invoice['A9'] = constructor_profile.address

        ws_invoice['E9'] = ''

        ws_invoice['A10'] = 'HSN code:'
        ws_invoice['B10'] = constructor_profile.hsncode
        ws_invoice['A10'].font = Font(bold=True)

        ws_invoice['A11'] = 'GST No.:'
        ws_invoice['B11'] = constructor_profile.gst
        ws_invoice['A11'].font = Font(bold=True)

        ws_invoice['A12'] = 'Kind Attn:'
        ws_invoice['A12'].font = Font(bold=True)

        ws_invoice['A13'] = 'GST:'
        ws_invoice['A13'].font = Font(bold=True)

        # Add table headers
        table_headers = ['S. No', 'Description', 'Unit', 'Quantity', 'Rate', 'Amount excluding all taxes (INR)']
        header_font = Font(bold=True)
        for col_num, header in enumerate(table_headers, 1):
            cell = ws_invoice.cell(row=12, column=col_num, value=header)
            cell.font = header_font

        total_amount = total_sum_of_this_bill
        discount = total_amount * (constructor_profile.discount / 100)
        unit_no = ""
        rate = ""

        # Append rows for each stage
        ws_invoice.merge_cells('A13:A14')
        ws_invoice['A13'] = '1'
        ws_invoice['B13'] = 'Construction of Duplexes as per Annexure'
        ws_invoice['C13'] = unit_no
        ws_invoice['D13'] = ''
        ws_invoice['E13'] = rate
        ws_invoice['F13'] = total_amount
        ws_invoice['B14'] = f'Below {constructor_profile.discount}%'
        ws_invoice['F14'] = discount

        total_amount -= discount
        # Add bank details and calculations
        row_num = ws_invoice.max_row + 1
        ws_invoice[f'A{row_num}'] = 'Bank Details'
        ws_invoice[f'A{row_num+1}'] = 'Bank Account No.:'
        ws_invoice[f'B{row_num+1}'] = constructor_profile.bank_no
        ws_invoice[f'A{row_num+2}'] = 'IFSC Code'
        ws_invoice[f'B{row_num+2}'] = constructor_profile.ifsc_code
        ws_invoice[f'A{row_num+3}'] = 'Bank Name'
        ws_invoice[f'B{row_num+3}'] = constructor_profile.bank_name
        ws_invoice[f'A{row_num+4}'] = 'Branch'
        ws_invoice[f'B{row_num+4}'] = constructor_profile.branch

        cgst = total_amount * 0.09
        sgst = total_amount * 0.09
        tds = total_amount * 0.01
        total_invoice = total_amount + cgst + sgst
        to_paid = total_invoice - tds

        row_num += 0
        ws_invoice[f'D{row_num}'] = 'Work Done Value'
        ws_invoice[f'F{row_num}'] = total_amount
        ws_invoice[f'F{row_num}'].font = Font(bold=True)
        ws_invoice[f'D{row_num+1}'] = 'Add CGST'
        ws_invoice[f'E{row_num+1}'] = '9%'
        ws_invoice[f'F{row_num+1}'] = cgst
        ws_invoice[f'D{row_num+2}'] = 'Add SGST'
        ws_invoice[f'E{row_num+2}'] = '9%'
        ws_invoice[f'F{row_num+2}'] = sgst
        ws_invoice[f'D{row_num+3}'] = 'Add IGST'
        ws_invoice[f'E{row_num+3}'] = '--'
        
        ws_invoice.merge_cells(f'D{row_num+4}:E{row_num+4}')
        ws_invoice[f'D{row_num+4}'] = 'Total Invoice'
        ws_invoice[f'D{row_num+4}'].font = Font(bold=True)
        ws_invoice[f'F{row_num+4}'] = total_invoice
        ws_invoice[f'F{row_num+4}'].font = Font(bold=True)

        ws_invoice.merge_cells(f'D{row_num+5}:E{row_num+5}')
        ws_invoice[f'D{row_num+5}'] = 'Deduction:'
        ws_invoice[f'D{row_num+5}'].font = Font(bold=True)
        ws_invoice[f'D{row_num+6}'] = 'TDS'
        ws_invoice[f'E{row_num+6}'] = '1%'
        ws_invoice[f'F{row_num+6}'] = tds

        ws_invoice[f'D{row_num+7}'] = 'TO BE PAID'
        ws_invoice[f'D{row_num+7}'].font = Font(bold=True)
        ws_invoice[f'F{row_num+7}'] = to_paid
        ws_invoice[f'F{row_num+7}'].font = Font(bold=True)

        row_num += 9
        ws_invoice[f'A{row_num}'] = 'Amount in words:'
        word_amt = num2words(to_paid, to='currency', lang='en_IN')
        word_amt = word_amt.replace('euro','rupees')
        word_amt = word_amt.replace('cents','paise')
        ws_invoice[f'B{row_num}'] = word_amt  # Convert number to words
        ws_invoice.column_dimensions['B'].width = 100  # Adjust this value as needed

        # Set alignment to wrap text and center it vertically
        ws_invoice[f'B{row_num}'].alignment = Alignment(wrap_text=True, vertical='center', horizontal='center')

        ws_invoice[f'F{row_num}'] = f'For {constructor_profile.name}'

        # Alignments
        for row in ws_invoice.iter_rows():
            for cell in row:
                if cell.column == 1 and cell.row > 2:  # Column A and row 2 to the end
                    cell.alignment = Alignment(horizontal='left')
                else:
                    cell.alignment = Alignment(horizontal='center', vertical='center')

        # Set column widths
        column_widths = [30, 35, 20, 20, 20, 30]  # Customize widths as needed
        for i, width in enumerate(column_widths, start=1):
            ws_invoice.column_dimensions[get_column_letter(i)].width = width

        # Save workbook to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        wb.save(temp_file.name)

        # Read the temporary file and save it to the model
        with open(temp_file.name, 'rb') as f:
            file_content = ContentFile(f.read(), name=f'RA_{constructor_profile.name}_Bill_{contractor_id}.xlsx')

            # Create an instance of InvoiceCivilStages
            invoice_instance = InvoiceCivilStages(
                constructor_profile=constructor_profile,
                invoice=file_content
            )
            invoice_instance.save()

            # Add the units to the instance
            invoice_instance.unit.set(query.values_list('unit', flat=True))

        # Remove the temporary file
        os.remove(temp_file.name)

        # Prepare the response
        # response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        # response['Content-Disposition'] = f'attachment; filename=RA_{constructor_profile.name}_Bill_{constructor_profile_id}.xlsx'

        wb.save(output)
        output.seek(0)

        unit_numbers = list(set(stage.unit for stage in civil_stages))
        if not file_same:
            excel_record = ExcelFilesCivilStages(
                constructor_profile=contractor_profile,
                prev_bill=prev_bill_dict,
                bill_no=f"RA : {bill_number}",
                downloaded_sucessfully = True
            )
            # Update the bill_downloaded_ fields in CivilStatges
            civil_stages_qs = CivilStatges.objects.filter(
                constructor_profile=contractor_profile,
                unit__in=unit_numbers  # Assuming unit_numbers is a list of relevant units
            )

            for civil_stage in civil_stages:
                for i in range(1, 12):
                    completed_field = f'completed_stage_{i}'
                    bill_downloaded_field = f'bill_downloaded_{i}'

                    # If the stage is completed, set the bill_downloaded_ field to True

                    if getattr(civil_stage, completed_field):
                        setattr(civil_stage, bill_downloaded_field, True)

                # Save the updated CivilStatges instance
                civil_stage.save()
            excel_record.save()
            excel_record.unit.set(unit_numbers)

            file_content = ContentFile(output.getvalue(), name=f"Contractor_{bill_number}_Bill.xlsx")
            excel_record.file.save(file_content.name, file_content, save=True)

            response = HttpResponse(
                output,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="RA : {bill_number}.xlsx"'

            return response
        else:
            return Response({"message":"This has already been generated."}, status=status.HTTP_400_BAD_REQUEST)

# MB file to view remove saving the file in database and remove the color form file

class ContractorBillsProtectFormSavingRemoveColorAPIview(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        contractor_id = request.query_params.get('contractor_id')
        unit_nos = request.query_params.getlist('unit_no')

        if not contractor_id:
            return Response({"error": "Contractor ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            contractor_id = int(contractor_id)
        except ValueError:
            return Response({"error": "Invalid Contractor ID."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            contractor_profile = ConstructorProfile.objects.get(id=contractor_id)
        except ConstructorProfile.DoesNotExist:
            return Response({"error": "Contractor Profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Filter CivilStages by contractor_id and optionally by unit_nos
        if unit_nos:
            civil_stages = CivilStatges.objects.filter(
                constructor_profile_id=contractor_id,
                unit__unit_no__in=unit_nos
            ).order_by('-created_at')
        else:
            civil_stages = CivilStatges.objects.filter(
                constructor_profile_id=contractor_id
            ).order_by('-created_at')

        civil_stages_check = civil_stages.filter(
            Q(completed_stage_1=1) | 
            Q(completed_stage_2=1) | 
            Q(completed_stage_3=1) | 
            Q(completed_stage_4=1) | 
            Q(completed_stage_5=1) | 
            Q(completed_stage_6=1) | 
            Q(completed_stage_7=1) | 
            Q(completed_stage_8=1) | 
            Q(completed_stage_9=1) | 
            Q(completed_stage_10=1) | 
            Q(completed_stage_11=1)
            )
        if not civil_stages_check.exists():
            return Response({"message":"There's no bill to generate."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            constructor_profile = ConstructorProfile.objects.get(id=contractor_id)
        except ConstructorProfile.DoesNotExist:
            # return Response({"error": "Contractor Profile not found."}, status=status.HTTP_404_NOT_FOUND)
            constructor_profile = ConstructorProfile.objects.all().last()
            contractor_id = constructor_profile.id


        if unit_nos:
            query = CivilStatges.objects.filter(constructor_profile__id=contractor_id, unit__unit_no__in=unit_nos)
        else:
            query = CivilStatges.objects.filter(constructor_profile__id=contractor_id)

        rows = []
        # stages_set = set()
        stages_set = []

        total_amount_sum = 0
        prev_bill_sum = 0
        this_bill_sum = 0
        prev_bill_dict = {}
        
        green_fill = PatternFill(start_color="00FF00", end_color="00FF00", fill_type="solid")

        # Fetch the last entry for the same contractor
        last_excel_record = ExcelFilesCivilStages.objects.filter(constructor_profile=contractor_profile)
        file_same = False # to identify if the file has been saved before
        prev_bill_values = {}
        df_misc = pd.DataFrame()
        if len(last_excel_record)>0:
            # prev_bill_values = last_excel_record.prev_bill
            df_old = pd.DataFrame()
            for bills in last_excel_record:
                excel_path = bills.file.path
                df1 = pd.read_excel(excel_path, skiprows=4)
                df_old = pd.concat([df_old,df1], ignore_index=False)
            df_old.drop_duplicates(inplace=True)
            
            df_misc = df1[(df1['Sr No'].isnull()) & (~df1['Rate'].isnull()) & (~df1['This Bill'].isnull())]
            
            df_old = df_old[~((df_old['Sr No'].isnull()) & (df_old['Total Percentage'].isnull()))]
            df_check = df_old[~(df_old['Sr No'].isnull())]
            df_check['Sr No'] = df_check['Sr No'].astype(int).astype(str)
            df_check['Rate'] = df_check['Rate'].astype(int)
            df_check = df_check[df_check.columns[:-1]]

            df_check.drop_duplicates(inplace=True)
            units_no = [str(int(i)) for i in unit_nos]
            if unit_nos:
                df_check = df_check[df_check['Sr No'].isin(units_no)]

            df_check = df_check.groupby('Sr No').apply(filter_rows_with_fewest_missing).reset_index(drop=True)
            df_check.drop_duplicates(subset=df_check.columns[:-2], keep='last', inplace=True)
            
            if len(df_check)>0:
                count = 1
                for sr in df_check['Sr No'].unique():
                    df_sub = df_check[df_check['Sr No']==sr]
                    # prev_bill_values[f'row_{count}'] = df_sub['This Bill'].to_list()[-1]
                    prev_bill_values[sr] = df_sub['This Bill'].to_list()[-1]


        # Track newly added completed stages
        newly_completed_stages = set()
        stage_dict = {}
        for idx, stage in enumerate(civil_stages, start=1):
            area = float(stage.unit.square_fit if stage.unit.square_fit else 0.0)
            rate = float(stage.unit.rate if stage.unit.rate else 0.0)
            total_percentage = 0
            sr_1 = stage.unit.unit_no if stage.unit else ''
            try:
                # prev_bill_value = prev_bill_values[str(int(sr_1))]
                prev_row_amt = df_check[df_check['Sr No']==str(int(sr_1))]['Total Amount'].to_list()[0]
            except Exception as e:
                # prev_bill_value = 0
                prev_row_amt = 0
            row = {
                'Sr No': stage.unit.unit_no if stage.unit else '',
                'Area': area,
                'Rate': rate,
                'Total Percentage': 0,
                'Total Amount': 0,
                'Prv Bill Amount': prev_row_amt,
                'This Bill': 0,
                'Remarks': stage.remark.title if stage.remark else ''
            }

            current_stage_set = set()
            for i in range(1, 12):
                stage_name = getattr(stage, f'stage{i}', '')
                try:
                    percentage = float(getattr(stage, f'percentage_stage_{i}', 0))
                except:
                    percentage = 0
                completed = getattr(stage, f'completed_stage_{i}', False)
                if stage_name:
                    row[stage_name] = f"{percentage}%" if completed else ''
                    # stages_set.add(stage_name)
                    stage_dict[i] = stage_name
                    # if stage_name not in stages_set:
                    #     print(stage_name)
                    #     stages_set.append(stage_name)
                    if completed:
                        current_stage_set.add(stage_name)
                        total_percentage += percentage

            # Identify newly completed stages
            for stage_name in current_stage_set:
                if stage_name not in prev_bill_values or not prev_bill_values[stage_name]:
                    newly_completed_stages.add(stage_name)
            row['Total Percentage'] = f"{total_percentage}%"
            row['Total Amount'] = int(area * rate * (total_percentage / 100))
            if prev_row_amt==0:
                row['This Bill'] = row['Total Amount'] - row['Prv Bill Amount']
            else:
                row['This Bill'] = row['Total Amount'] - prev_row_amt
            prev_bill_dict[f'row_{idx}'] = row['Total Amount']

            total_amount_sum += row['Total Amount']
            prev_bill_sum += row['Prv Bill Amount']
            this_bill_sum += row['This Bill']

            rows.append(row)
        sorted_dict = {k: stage_dict[k] for k in sorted(stage_dict)}
        stages_set = sorted_dict.values()
        # Fetch miscellaneous data
        miscellaneous_records = Miscellaneous.objects.filter(unit__in=[stage.unit for stage in civil_stages], delete=False)

        for misc in miscellaneous_records:
            if misc.prev_bill:
                row = {
                    'Sr No': '',
                    'Area': '',
                    'Rate': misc.title,
                    'Total Percentage': '',
                    'Total Amount': misc.amount,
                    'Prv Bill Amount': misc.amount,
                    'This Bill': 0,
                    'Remarks': ''
                }
            else:
                row = {
                    'Sr No': '',
                    'Area': '',
                    'Rate': misc.title,
                    'Total Percentage': '',
                    'Total Amount': misc.amount,
                    'Prv Bill Amount': 0,
                    'This Bill': misc.amount,
                    'Remarks': ''
                }
                # misc.prev_bill = True
                # misc.save()
            rows.append(row)
        df = pd.DataFrame(rows)
        try : 
            df_check_new = df_check.copy()
            df_check_new['Rate'] = df_check_new['Rate'].astype(float)
            df_check_new.fillna("", inplace=True)
            df_new_check = df.copy()
            df_new_check = df_new_check[(~df_new_check['Sr No'].isnull()) & (df_new_check['Sr No']!='')]
            df_new_check.drop(columns=['Total Percentage', 'Total Amount', 'Prv Bill Amount', 'This Bill', 'Remarks'], inplace=True)
            df_new_check['Sr No'] = df_new_check['Sr No'].astype(int).astype(str)
            df_check_new.drop(columns=['Total Percentage', 'Total Amount', 'Prv Bill Amount', 'This Bill'], inplace=True)
            df_check_new.fillna('', inplace=True)
            df_new_check.fillna('', inplace=True)
            merged_df = df_new_check.merge(df_check_new, how='left', indicator=True)
            all_rows_in_df1 = merged_df['_merge'].eq('both').all()
            
        except Exception as e:
            print(e)
        
        df = df.sort_values(
                by='Sr No',
                key=lambda x: x.map(lambda val: float('inf') if pd.isna(val) or val == '' else int(val)),
                na_position='last'
            ).reset_index(drop=True)
        try:
            df_check = df_check.sort_values(
                by='Sr No',
                key=lambda x: x.map(lambda val: float('inf') if pd.isna(val) or val == '' else int(val)),
                na_position='last'
            ).reset_index(drop=True)
        except:
            pass

        for stage_name in stages_set:
            if stage_name not in df.columns:
                df[stage_name] = "0%"

        ordered_columns = ['Sr No', 'Area', 'Rate'] + list(stages_set) + [
            'Total Percentage', 'Total Amount', 'Prv Bill Amount', 'This Bill', 'Remarks'
        ]
        df = df[ordered_columns]
        # Values from the image for the stages
        stage_values = ['10%', '10%', '10%', '10%', '5%', '10%', '15%', '10%', '5%', '10%', '5%']

        # Create a dictionary for the new row with values for the stages and empty strings for the rest
        new_row = {col: "" for col in ordered_columns}
        for stage, value in zip(stages_set, stage_values):
            new_row[stage] = value

        new_row["Total Percentage"] = "100%"

        # Convert the new row to a DataFrame
        new_row_df = pd.DataFrame([new_row])
        df_totals = {
            'Total Amount': df['Total Amount'].sum(),
            'Prv Bill Amount': df['Prv Bill Amount'].sum(),
            'This Bill': df['This Bill'].sum(),
        }

        df = pd.concat([new_row_df,df]).reset_index(drop=True)
        # df = df.sort_values('Sr No')
        total_sum_of_total_amount = df_totals['Total Amount']
        total_sum_of_pre_bill_amount = df_totals['Prv Bill Amount']
        total_sum_of_this_bill = df_totals['This Bill']

        discount = contractor_profile.discount
        total_this_bill = total_sum_of_total_amount - total_sum_of_pre_bill_amount
        discounted_amount = total_this_bill * (discount / 100)
        total_sum = total_this_bill - discounted_amount
        gst = total_sum * 0.18
        total_with_gst = total_sum + gst
        #total_with_gst = total_sum 
        # less_1_percenatge_gst = total_with_gst * (1 / 100)
        less_1_percenatge_gst = total_sum * (1 / 100)
        final_total_amount = total_with_gst - less_1_percenatge_gst


        output = BytesIO()
        wb = Workbook()
        ws = wb.active
        ws.title = contractor_profile.name

        header_font = Font(bold=True, size=16)
        header_contactor_profile = Font(bold=True, size=24)
        bill_count = ExcelFilesCivilStages.objects.filter(constructor_profile=contractor_profile).count()
        bill_number = f"{bill_count + 1:02d}"

        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(ordered_columns))
        ws.cell(row=1, column=1).value = f"{contractor_profile.name}"
        ws.cell(row=1, column=1).font = header_contactor_profile
        ws.cell(row=1, column=1).alignment = Alignment(horizontal='center')

        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(ordered_columns))
        ws.cell(row=2, column=1).value = f"Date: {datetime.now().strftime('%d/%m/%y')}"
        ws.cell(row=2, column=1).font = header_font
        ws.cell(row=2, column=1).alignment = Alignment(horizontal='left')

        ws.merge_cells(start_row=3, start_column=1, end_row=3, end_column=len(ordered_columns))
        ws.cell(row=3, column=1).value = f"RA Bill No: {bill_number}"
        ws.cell(row=3, column=1).font = header_font
        ws.cell(row=3, column=1).alignment = Alignment(horizontal='right')

        thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        bold_border = Border(left=Side(style='medium'), right=Side(style='medium'), top=Side(style='medium'), bottom=Side(style='medium'))
        # print(df)
        # print(df_old)
        for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), 5):
            for c_idx, value in enumerate(row, 1):
                cell = ws.cell(row=r_idx, column=c_idx, value=value)
                if r_idx == 5:
                    cell.font = Font(bold=True, size=14)
                    ws.column_dimensions[cell.column_letter].width = 15
                    cell.border = bold_border
                else:
                    if any(misc.title == cell.value for misc in miscellaneous_records):
                        cell.border = None
                    else:
                        cell.border = thin_border
                cell.alignment = Alignment(horizontal='center', vertical='center')
                if r_idx > 5:
                    cell.font = Font(size=12)
                if r_idx == 6:
                    cell.font = Font(size=12, color="0000FF")
               # Apply green fill for newly completed stages
                column_name = ordered_columns[c_idx - 1]
                # if column_name in newly_completed_stages:
                #     cell.fill = green_fill
                try:
                    if r_idx>6:
                        if pd.isna(df_check.loc[df_check['Sr No']==str(int(df.loc[r_idx-6,'Sr No'])), column_name].to_list()[0]) and df_check.loc[df_check['Sr No']==str(int(df.loc[r_idx-6,'Sr No'])), column_name]=="" and not pd.isna(value) and value!="" and value not in ordered_columns and column_name in stages_set:
                            cell.fill = green_fill
                        elif len(df_check[df_check['Sr No']==str(int(df.loc[r_idx-6,'Sr No']))])==0 and not pd.isna(value) and value!="" and value not in ordered_columns and column_name in stages_set:
                            cell.fill = green_fill
                except Exception as e:
                    print(e)
                    try:
                        if column_name in stages_set and not pd.isna(value) and value!="" and value not in ordered_columns:
                            cell.fill = green_fill
                    except:
                        pass
        last_row = len(df) + 6
        total_font = Font(bold=True, size=14)

        row_offset = last_row
        for col_name in ['Total Amount', 'Prv Bill Amount', 'This Bill']:
            col_idx = ordered_columns.index(col_name) + 1
            ws.cell(row=row_offset, column=col_idx, value=df_totals[col_name]).font = total_font
            ws.cell(row=row_offset, column=col_idx).border = bold_border
            ws.cell(row=row_offset, column=col_idx).alignment = Alignment(horizontal='center', vertical='center')

        # total_amt = total_sum - discounted_amount
        additional_totals = [
            ("This Bill Amount", total_this_bill),
            (f"Below ({discount}%)", discounted_amount),
            (f"Total Amount", total_sum),
            ("Add 18% GST", gst),
            ("Total Amount with GST", total_with_gst),
            ("Less TDS 1%", less_1_percenatge_gst),
            ("Total Amount", final_total_amount)
        ]

        for i, (label, value) in enumerate(additional_totals):
            row_offset = last_row + 2 + i
            ws.cell(row=row_offset, column=len(ordered_columns) - 3, value=label).font = total_font
            ws.cell(row=row_offset, column=len(ordered_columns) - 2, value=value).font = total_font
            ws.cell(row=row_offset, column=len(ordered_columns) - 3).border = bold_border
            ws.cell(row=row_offset, column=len(ordered_columns) - 2).border = bold_border
            ws.cell(row=row_offset, column=len(ordered_columns) - 3).alignment = Alignment(horizontal='center', vertical='center')
            ws.cell(row=row_offset, column=len(ordered_columns) - 2).alignment = Alignment(horizontal='center', vertical='center')
            if label == "Total Amount":
                ws.cell(row=row_offset, column=len(ordered_columns) - 2).fill = green_fill
                ws.cell(row=row_offset, column=len(ordered_columns) - 3).fill = green_fill
        
        # Set the page size to A4
        ws.page_setup.paperSize = ws.PAPERSIZE_A4

        # Adjust print settings if needed
        ws.print_options.horizontalCentered = True
        ws.print_options.verticalCentered = True
        
        ws_invoice = wb.create_sheet(title="Invoice")

        # Set up the worksheet content
        ws_invoice['A1'] = constructor_profile.name
        ws_invoice['A1'].font = Font(bold=True,size=24)
        ws_invoice.merge_cells('A1:F1')

        ws_invoice['A2'] = 'Tax Invoice'
        ws_invoice['A2'].font = Font(bold=True)
        ws_invoice['E4'] = f'Date: {date.today()}'
        ws_invoice.merge_cells('A2:F2')

        ws_invoice['A4'] = 'TO,'
        ws_invoice['A4'].font = Font(bold=True)

        ws_invoice['A5'] = 'C.I. REAL ESTATE'
        ws_invoice['A5'].font = Font(bold=True)

        ws_invoice['A6'] = f'GST: {constructor_profile.gst}'

        ws_invoice['A7'] = 'M.P. NAGAR, BHOPAL'

        ws_invoice['A8'] = 'From,'
        ws_invoice['A8'].font = Font(bold=True)

        ws_invoice['A9'] = constructor_profile.name

        ws_invoice['A9'] = constructor_profile.address

        ws_invoice['E9'] = ''

        ws_invoice['A10'] = 'HSN code:'
        ws_invoice['B10'] = constructor_profile.hsncode
        ws_invoice['A10'].font = Font(bold=True)

        ws_invoice['A11'] = 'GST No.:'
        ws_invoice['B11'] = constructor_profile.gst
        ws_invoice['A11'].font = Font(bold=True)

        ws_invoice['A12'] = 'Kind Attn:'
        ws_invoice['A12'].font = Font(bold=True)

        ws_invoice['A13'] = 'GST:'
        ws_invoice['A13'].font = Font(bold=True)

        # Add table headers
        table_headers = ['S. No', 'Description', 'Unit', 'Quantity', 'Rate', 'Amount excluding all taxes (INR)']
        header_font = Font(bold=True)
        for col_num, header in enumerate(table_headers, 1):
            cell = ws_invoice.cell(row=12, column=col_num, value=header)
            cell.font = header_font

        total_amount = total_sum_of_this_bill
        discount = total_amount * (constructor_profile.discount / 100)
        unit_no = ""
        rate = ""
        # Append rows for each stage
        ws_invoice.merge_cells('A13:A14')
        ws_invoice['A13'] = '1'
        ws_invoice['B13'] = 'Construction of Duplexes as per Annexure'
        ws_invoice['C13'] = unit_no
        ws_invoice['D13'] = ''
        ws_invoice['E13'] = rate
        ws_invoice['F13'] = total_amount
        ws_invoice['B14'] = f'Below {constructor_profile.discount}%'
        ws_invoice['F14'] = discount

        total_amount -= discount
        # Add bank details and calculations
        row_num = ws_invoice.max_row + 1
        ws_invoice[f'A{row_num}'] = 'Bank Details'
        ws_invoice[f'A{row_num+1}'] = 'Bank Account No.:'
        ws_invoice[f'B{row_num+1}'] = constructor_profile.bank_no
        ws_invoice[f'A{row_num+2}'] = 'IFSC Code'
        ws_invoice[f'B{row_num+2}'] = constructor_profile.ifsc_code
        ws_invoice[f'A{row_num+3}'] = 'Bank Name'
        ws_invoice[f'B{row_num+3}'] = constructor_profile.bank_name
        ws_invoice[f'A{row_num+4}'] = 'Branch'
        ws_invoice[f'B{row_num+4}'] = constructor_profile.branch

        cgst = total_amount * 0.09
        sgst = total_amount * 0.09
        tds = total_amount * 0.01
        total_invoice = total_amount + cgst + sgst
        to_paid = total_invoice - tds

        row_num += 0
        ws_invoice[f'D{row_num}'] = 'Work Done Value'
        ws_invoice[f'F{row_num}'] = total_amount
        ws_invoice[f'F{row_num}'].font = Font(bold=True)
        ws_invoice[f'D{row_num+1}'] = 'Add CGST'
        ws_invoice[f'E{row_num+1}'] = '9%'
        ws_invoice[f'F{row_num+1}'] = cgst
        ws_invoice[f'D{row_num+2}'] = 'Add SGST'
        ws_invoice[f'E{row_num+2}'] = '9%'
        ws_invoice[f'F{row_num+2}'] = sgst
        ws_invoice[f'D{row_num+3}'] = 'Add IGST'
        ws_invoice[f'E{row_num+3}'] = '--'
        
        ws_invoice.merge_cells(f'D{row_num+4}:E{row_num+4}')
        ws_invoice[f'D{row_num+4}'] = 'Total Invoice'
        ws_invoice[f'D{row_num+4}'].font = Font(bold=True)
        ws_invoice[f'F{row_num+4}'] = total_invoice
        ws_invoice[f'F{row_num+4}'].font = Font(bold=True)

        ws_invoice.merge_cells(f'D{row_num+5}:E{row_num+5}')
        ws_invoice[f'D{row_num+5}'] = 'Deduction:'
        ws_invoice[f'D{row_num+5}'].font = Font(bold=True)
        ws_invoice[f'D{row_num+6}'] = 'TDS'
        ws_invoice[f'E{row_num+6}'] = '1%'
        ws_invoice[f'F{row_num+6}'] = tds

        ws_invoice[f'D{row_num+7}'] = 'TO BE PAID'
        ws_invoice[f'D{row_num+7}'].font = Font(bold=True)
        ws_invoice[f'F{row_num+7}'] = to_paid
        ws_invoice[f'F{row_num+7}'].font = Font(bold=True)

        row_num += 9
        ws_invoice[f'A{row_num}'] = 'Amount in words:'
        word_amt = num2words(to_paid, to='currency', lang='en_IN')
        word_amt = word_amt.replace('euro','rupees')
        word_amt = word_amt.replace('cents','paise')
        ws_invoice[f'B{row_num}'] = word_amt  # Convert number to words
        ws_invoice.column_dimensions['B'].width = 100  # Adjust this value as needed

        # Set alignment to wrap text and center it vertically
        ws_invoice[f'B{row_num}'].alignment = Alignment(wrap_text=True, vertical='center', horizontal='center')

        ws_invoice[f'F{row_num}'] = f'For {constructor_profile.name}'

        # Alignments
        for row in ws_invoice.iter_rows():
            for cell in row:
                if cell.column == 1 and cell.row > 2:  # Column A and row 2 to the end
                    cell.alignment = Alignment(horizontal='left')
                else:
                    cell.alignment = Alignment(horizontal='center', vertical='center')

        # Set column widths
        column_widths = [30, 35, 20, 20, 20, 30]  # Customize widths as needed
        for i, width in enumerate(column_widths, start=1):
            ws_invoice.column_dimensions[get_column_letter(i)].width = width

       
        # Save workbook to temporary file
        wb.save(output)
        output.seek(0)

        unit_numbers = list(set(stage.unit for stage in civil_stages))

        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="RA : {bill_number}.xlsx"'

        return response

class DownloadPreviousBillsAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return CivilStatges.objects.get(pk=pk)
        except CivilStatges.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = self.get_object(pk)
                serializer = CivilStatges(data)
                return Response(serializer.data)

            else:
                filterset = ExcelFilesDownloadFilter(request.GET, queryset=ExcelFilesCivilStages.objects.all().order_by('-created_at'))
                if filterset.is_valid():
                    queryset = filterset.qs
                else:
                    queryset = ExcelFilesCivilStages.objects.all().order_by('-created_at')
                serializer = ExcelFilesCivilStagesSerializer(queryset, many=True)

                return Response(serializer.data)
            


class InvoiceAPIview(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        constructor_profile_id = request.GET.get('contractor_id')
        unit_nos = request.query_params.getlist('unit_no')

        try:
            constructor_profile = ConstructorProfile.objects.get(id=constructor_profile_id)
        except ConstructorProfile.DoesNotExist:
            # return Response({"error": "Contractor Profile not found."}, status=status.HTTP_404_NOT_FOUND)
            constructor_profile = ConstructorProfile.objects.all().last()
            constructor_profile_id = constructor_profile.id


        if unit_nos:
            query = CivilStatges.objects.filter(constructor_profile__id=constructor_profile_id, unit__unit_no__in=unit_nos)
        else:
            query = CivilStatges.objects.filter(constructor_profile__id=constructor_profile_id)

        # Create a new workbook and select the active worksheet
        wb = Workbook()
        ws = wb.active

        # Set up the worksheet content
        ws['A1'] = constructor_profile.name
        ws['A1'].font = Font(bold=True,size=24)
        ws.merge_cells('A1:F1')

        ws['A2'] = 'Tax Invoice'
        ws['A2'].font = Font(bold=True)
        ws['E4'] = f'Date: {date.today()}'
        ws.merge_cells('A2:F2')

        ws['A4'] = 'TO,'
        ws['A4'].font = Font(bold=True)

        ws['A5'] = 'C.I. REAL ESTATE'
        ws['A5'].font = Font(bold=True)

        ws['A6'] = f'GST: {constructor_profile.gst}'

        ws['A7'] = 'M.P. NAGAR, BHOPAL'

        ws['A8'] = 'From,'
        ws['A8'].font = Font(bold=True)

        ws['A9'] = constructor_profile.name

        ws['A9'] = constructor_profile.address

        ws['E9'] = ''

        ws['A10'] = 'HSN code:'
        ws['B10'] = constructor_profile.hsncode
        ws['A10'].font = Font(bold=True)

        ws['A11'] = 'GST No.:'
        ws['B11'] = constructor_profile.gst
        ws['A11'].font = Font(bold=True)

        ws['A12'] = 'Kind Attn:'
        ws['A12'].font = Font(bold=True)

        ws['A13'] = 'GST:'
        ws['A13'].font = Font(bold=True)

        # Add table headers
        table_headers = ['S. No', 'Description', 'Unit', 'Quantity', 'Rate', 'Amount excluding all taxes (INR)']
        header_font = Font(bold=True)
        for col_num, header in enumerate(table_headers, 1):
            cell = ws.cell(row=12, column=col_num, value=header)
            cell.font = header_font

        total_amount = 0
        discount = 0
        unit_no = ""
        rate = float(constructor_profile.rate if constructor_profile and constructor_profile.rate else 0)
        for idx, stage in enumerate(query, start=1):
            area = float(stage.unit.square_fit if stage.unit.square_fit and stage.unit.square_fit else 0.0)
            rate = float(stage.unit.rate if stage.unit.rate else 0.0)  # Fetch rate from ConstructorUnitNo model
            total_percentage = 0

            for i in range(1, 11):
                stage_name = getattr(stage, f'stage{i}', '')
                try:
                    percentage = float(getattr(stage, f'percentage_stage_{i}', 0))
                except:
                    percentage = 0
                if stage_name:
                    total_percentage += percentage

            amount = area * rate * (total_percentage / 100)
            discount_amount = amount * (constructor_profile.discount / 100)
            total_amount += amount
            discount += discount_amount
            if unit_no == '':
                unit_no = stage.unit.unit_no if stage.unit else ''
        # Append rows for each stage
        ws.merge_cells('A13:A14')
        ws['A13'] = '1'
        ws['B13'] = 'Construction of Duplexes as per Annexure'
        ws['C13'] = unit_no
        ws['D13'] = ''
        ws['E13'] = rate
        ws['F13'] = total_amount
        ws['B14'] = f'Below {constructor_profile.discount}%'
        ws['F14'] = discount

        total_amount -= discount
        # Add bank details and calculations
        row_num = ws.max_row + 1
        ws[f'A{row_num}'] = 'Bank Details'
        ws[f'A{row_num+1}'] = 'Bank Account No.:'
        ws[f'B{row_num+1}'] = constructor_profile.bank_no
        ws[f'A{row_num+2}'] = 'IFSC Code'
        ws[f'B{row_num+2}'] = constructor_profile.ifsc_code
        ws[f'A{row_num+3}'] = 'Bank Name'
        ws[f'B{row_num+3}'] = constructor_profile.bank_name
        ws[f'A{row_num+4}'] = 'Branch'
        ws[f'B{row_num+4}'] = constructor_profile.branch

        cgst = total_amount * 0.09
        sgst = total_amount * 0.09
        tds = total_amount * 0.01
        total_invoice = total_amount + cgst + sgst
        to_paid = total_invoice - tds

        row_num += 0
        ws[f'D{row_num}'] = 'Work Done Value'
        ws[f'F{row_num}'] = total_amount
        ws[f'F{row_num}'].font = Font(bold=True)
        ws[f'D{row_num+1}'] = 'Add CGST'
        ws[f'E{row_num+1}'] = '9%'
        ws[f'F{row_num+1}'] = cgst
        ws[f'D{row_num+2}'] = 'Add SGST'
        ws[f'E{row_num+2}'] = '9%'
        ws[f'F{row_num+2}'] = sgst
        ws[f'D{row_num+3}'] = 'Add IGST'
        ws[f'E{row_num+3}'] = '--'
        
        ws.merge_cells(f'D{row_num+4}:E{row_num+4}')
        ws[f'D{row_num+4}'] = 'Total Invoice'
        ws[f'D{row_num+4}'].font = Font(bold=True)
        ws[f'F{row_num+4}'] = total_invoice
        ws[f'F{row_num+4}'].font = Font(bold=True)

        ws.merge_cells(f'D{row_num+5}:E{row_num+5}')
        ws[f'D{row_num+5}'] = 'Deduction:'
        ws[f'D{row_num+5}'].font = Font(bold=True)
        ws[f'D{row_num+6}'] = 'TDS'
        ws[f'E{row_num+6}'] = '1%'
        ws[f'F{row_num+6}'] = tds

        ws[f'D{row_num+7}'] = 'TO BE PAID'
        ws[f'D{row_num+7}'].font = Font(bold=True)
        ws[f'F{row_num+7}'] = to_paid
        ws[f'F{row_num+7}'].font = Font(bold=True)

        row_num += 9
        ws[f'A{row_num}'] = 'Amount in words:'
        word_amt = num2words(to_paid, to='currency', lang='en_IN')
        word_amt = word_amt.replace('euro','rupees')
        word_amt = word_amt.replace('cents','paise')
        ws[f'B{row_num}'] = word_amt  # Convert number to words
        ws.column_dimensions['B'].width = 100  # Adjust this value as needed

        # Set alignment to wrap text and center it vertically
        ws[f'B{row_num}'].alignment = Alignment(wrap_text=True, vertical='center', horizontal='center')

        ws[f'F{row_num}'] = f'For {constructor_profile.name}'

        # Alignments
        for row in ws.iter_rows():
            for cell in row:
                if cell.column == 1 and cell.row > 2:  # Column A and row 2 to the end
                    cell.alignment = Alignment(horizontal='left')
                else:
                    cell.alignment = Alignment(horizontal='center', vertical='center')

        # Set column widths
        column_widths = [30, 35, 20, 20, 20, 30]  # Customize widths as needed
        for i, width in enumerate(column_widths, start=1):
            ws.column_dimensions[get_column_letter(i)].width = width

        # Save workbook to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        wb.save(temp_file.name)

        # Read the temporary file and save it to the model
        with open(temp_file.name, 'rb') as f:
            file_content = ContentFile(f.read(), name=f'RA_{constructor_profile.name}_Bill_{constructor_profile_id}.xlsx')

            # Create an instance of InvoiceCivilStages
            invoice_instance = InvoiceCivilStages(
                constructor_profile=constructor_profile,
                invoice=file_content
            )
            invoice_instance.save()

            # Add the units to the instance
            invoice_instance.unit.set(query.values_list('unit', flat=True))

        # Remove the temporary file
        os.remove(temp_file.name)

        # Prepare the response
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=RA_{constructor_profile.name}_Bill_{constructor_profile_id}.xlsx'
        wb.save(response)
        return response


class InvoiceRemoveSavingFileAPIview(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        constructor_profile_id = request.GET.get('contractor_id')
        unit_nos = request.query_params.getlist('unit_no')

        try:
            constructor_profile = ConstructorProfile.objects.get(id=constructor_profile_id)
        except ConstructorProfile.DoesNotExist:
            # return Response({"error": "Contractor Profile not found."}, status=status.HTTP_404_NOT_FOUND)
            constructor_profile = ConstructorProfile.objects.all().last()
            constructor_profile_id = constructor_profile.id


        if unit_nos:
            query = CivilStatges.objects.filter(constructor_profile__id=constructor_profile_id, unit__unit_no__in=unit_nos)
        else:
            query = CivilStatges.objects.filter(constructor_profile__id=constructor_profile_id)

        # Create a new workbook and select the active worksheet
        wb = Workbook()
        ws = wb.active

        # Set up the worksheet content
        ws['A1'] = constructor_profile.name
        ws['A1'].font = Font(bold=True,size=24)
        ws.merge_cells('A1:F1')

        ws['A2'] = 'Tax Invoice'
        ws['A2'].font = Font(bold=True)
        ws['E4'] = f'Date: {date.today()}'
        ws.merge_cells('A2:F2')

        ws['A4'] = 'TO,'
        ws['A4'].font = Font(bold=True)

        ws['A5'] = 'C.I. REAL ESTATE'
        ws['A5'].font = Font(bold=True)

        ws['A6'] = f'GST: {constructor_profile.gst}'

        ws['A7'] = 'M.P. NAGAR, BHOPAL'

        ws['A8'] = 'From,'
        ws['A8'].font = Font(bold=True)

        ws['A9'] = constructor_profile.name

        ws['A9'] = constructor_profile.address

        ws['E9'] = ''

        ws['A10'] = 'HSN code:'
        ws['B10'] = constructor_profile.hsncode
        ws['A10'].font = Font(bold=True)

        ws['A11'] = 'GST No.:'
        ws['B11'] = constructor_profile.gst
        ws['A11'].font = Font(bold=True)

        ws['A12'] = 'Kind Attn:'
        ws['A12'].font = Font(bold=True)

        ws['A13'] = 'GST:'
        ws['A13'].font = Font(bold=True)

        # Add table headers
        table_headers = ['S. No', 'Description', 'Unit', 'Quantity', 'Rate', 'Amount excluding all taxes (INR)']
        header_font = Font(bold=True)
        for col_num, header in enumerate(table_headers, 1):
            cell = ws.cell(row=12, column=col_num, value=header)
            cell.font = header_font

        total_amount = 0
        discount = 0
        unit_no = ""
        rate = float(constructor_profile.rate if constructor_profile and constructor_profile.rate else 0)
        for idx, stage in enumerate(query, start=1):
            area = float(stage.unit.square_fit if stage.unit.square_fit and stage.unit.square_fit else 0.0)
            rate = float(stage.unit.rate if stage.unit.rate else 0.0)  # Fetch rate from ConstructorUnitNo model
            total_percentage = 0

            for i in range(1, 11):
                stage_name = getattr(stage, f'stage{i}', '')
                percentage = float(getattr(stage, f'percentage_stage_{i}', 0))
                if stage_name:
                    total_percentage += percentage

            amount = area * rate * (total_percentage / 100)
            discount_amount = amount * (constructor_profile.discount / 100)
            total_amount += amount
            discount += discount_amount
            if unit_no == '':
                unit_no = stage.unit.unit_no if stage.unit else ''
        # Append rows for each stage
        ws.merge_cells('A13:A14')
        ws['A13'] = '1'
        ws['B13'] = 'Construction of Duplexes as per Annexure'
        ws['C13'] = unit_no
        ws['D13'] = ''
        ws['E13'] = rate
        ws['F13'] = total_amount
        ws['B14'] = f'Below {constructor_profile.discount}%'
        ws['F14'] = discount

        total_amount -= discount
        # Add bank details and calculations
        row_num = ws.max_row + 1
        ws[f'A{row_num}'] = 'Bank Details'
        ws[f'A{row_num+1}'] = 'Bank Account No.:'
        ws[f'B{row_num+1}'] = constructor_profile.bank_no
        ws[f'A{row_num+2}'] = 'IFSC Code'
        ws[f'B{row_num+2}'] = constructor_profile.ifsc_code
        ws[f'A{row_num+3}'] = 'Bank Name'
        ws[f'B{row_num+3}'] = constructor_profile.bank_name
        ws[f'A{row_num+4}'] = 'Branch'
        ws[f'B{row_num+4}'] = constructor_profile.branch

        cgst = total_amount * 0.09
        sgst = total_amount * 0.09
        tds = total_amount * 0.01
        total_invoice = total_amount + cgst + sgst
        to_paid = total_invoice - tds

        row_num += 0
        ws[f'D{row_num}'] = 'Work Done Value'
        ws[f'F{row_num}'] = total_amount
        ws[f'F{row_num}'].font = Font(bold=True)
        ws[f'D{row_num+1}'] = 'Add CGST'
        ws[f'E{row_num+1}'] = '9%'
        ws[f'F{row_num+1}'] = cgst
        ws[f'D{row_num+2}'] = 'Add SGST'
        ws[f'E{row_num+2}'] = '9%'
        ws[f'F{row_num+2}'] = sgst
        ws[f'D{row_num+3}'] = 'Add IGST'
        ws[f'E{row_num+3}'] = '--'
        
        ws.merge_cells(f'D{row_num+4}:E{row_num+4}')
        ws[f'D{row_num+4}'] = 'Total Invoice'
        ws[f'D{row_num+4}'].font = Font(bold=True)
        ws[f'F{row_num+4}'] = total_invoice
        ws[f'F{row_num+4}'].font = Font(bold=True)

        ws.merge_cells(f'D{row_num+5}:E{row_num+5}')
        ws[f'D{row_num+5}'] = 'Deduction:'
        ws[f'D{row_num+5}'].font = Font(bold=True)
        ws[f'D{row_num+6}'] = 'TDS'
        ws[f'E{row_num+6}'] = '1%'
        ws[f'F{row_num+6}'] = tds

        ws[f'D{row_num+7}'] = 'TO BE PAID'
        ws[f'D{row_num+7}'].font = Font(bold=True)
        ws[f'F{row_num+7}'] = to_paid
        ws[f'F{row_num+7}'].font = Font(bold=True)

        row_num += 9
        ws[f'A{row_num}'] = 'Amount in words:'
        word_amt = num2words(to_paid, to='currency', lang='en_IN')
        word_amt = word_amt.replace('euro','rupees')
        word_amt = word_amt.replace('cents','paise')
        ws[f'B{row_num}'] = word_amt  # Convert number to words
        ws.column_dimensions['B'].width = 100  # Adjust this value as needed

        # Set alignment to wrap text and center it vertically
        ws[f'B{row_num}'].alignment = Alignment(wrap_text=True, vertical='center', horizontal='center')

        ws[f'F{row_num}'] = f'For {constructor_profile.name}'

        # Alignments
        for row in ws.iter_rows():
            for cell in row:
                if cell.column == 1 and cell.row > 2:  # Column A and row 2 to the end
                    cell.alignment = Alignment(horizontal='left')
                else:
                    cell.alignment = Alignment(horizontal='center', vertical='center')

        # Set column widths
        column_widths = [30, 35, 20, 20, 20, 30]  # Customize widths as needed
        for i, width in enumerate(column_widths, start=1):
            ws.column_dimensions[get_column_letter(i)].width = width

        # Save workbook to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        wb.save(temp_file.name)

        # Read the temporary file and save it to the model
        # with open(temp_file.name, 'rb') as f:
        #     file_content = ContentFile(f.read(), name=f'RA_{constructor_profile.name}_Bill_{constructor_profile_id}.xlsx')

        #     # Create an instance of InvoiceCivilStages
        #     invoice_instance = InvoiceCivilStages(
        #         constructor_profile=constructor_profile,
        #         invoice=file_content
        #     )
        #     invoice_instance.save()

        #     # Add the units to the instance
        #     invoice_instance.unit.set(query.values_list('unit', flat=True))

        # # Remove the temporary file
        # os.remove(temp_file.name)

        # Prepare the response
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=RA_{constructor_profile.name}_Bill_{constructor_profile_id}.xlsx'
        wb.save(response)
        return response

class DownloadInvoiceBillsAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return InvoiceCivilStages.objects.get(pk=pk)
        except InvoiceCivilStages.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = self.get_object(pk)
                serializer = InvoiceCivilStages(data)
                return Response(serializer.data)

            else:
                filterset = InvoiceCivilStagesFilter(request.GET, queryset=InvoiceCivilStages.objects.all().order_by('-created_at'))
                if filterset.is_valid():
                    queryset = filterset.qs
                else:
                    queryset = InvoiceCivilStages.objects.all().order_by('-created_at')
                serializer = InvoiceCivilStagesSerializer(queryset, many=True)

                return Response(serializer.data)