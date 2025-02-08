import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from io import BytesIO

def filter_rows_with_fewest_missing(group):
    # Exclude the last two columns when checking for missing values
    cols_to_check = group.columns[:-2]
    # Count missing values per row within the group, for selected columns
    missing_counts = group[cols_to_check].isna().sum(axis=1) + (group[cols_to_check] == '').sum(axis=1)
    # Find the minimum number of missing values
    min_missing = missing_counts.min()
    # Return rows with the fewest missing values, but keep all columns in the output
    return group[missing_counts == min_missing]


def sort_key(val):
    if pd.isna(val) or val == '':
        return (float('inf'), val)  # Assign high value for NaN and ""
    else:
        return (int(val), val)


def generate_pdf(df, stages_set, total_amount):
    output_pdf = BytesIO()
    pdf_canvas = canvas.Canvas(output_pdf, pagesize=A4)
    
    # Set margins and offsets
    width, height = A4
    margin = 50
    x_offset = margin
    y_offset = height - margin

    def draw_table(df, y_offset, pdf_canvas):
        # Draw table headers
        pdf_canvas.setFont("Helvetica-Bold", 10)
        table_headers = ['Sr No', 'Area', 'Rate'] + list(stages_set) + [
            'Total Percentage', 'Total Amount', 'Prv Bill Amount', 'This Bill', 'Remarks'
        ]

        pdf_canvas.setFillColor(colors.gray)
        pdf_canvas.rect(x_offset, y_offset, width - 2 * margin, 20, stroke=1, fill=1)
        pdf_canvas.setFillColor(colors.white)
        col_width = (width - 2 * margin) / len(table_headers)
        
        for i, header in enumerate(table_headers):
            pdf_canvas.drawString(x_offset + i * col_width + 2, y_offset + 5, header)

        # Add data rows
        pdf_canvas.setFont("Helvetica", 8)
        y_offset -= 20
        pdf_canvas.setFillColor(colors.black)
        for idx, row in df.iterrows():
            for i, cell_value in enumerate(row):
                pdf_canvas.drawString(x_offset + i * col_width + 2, y_offset, str(cell_value))
            y_offset -= 15

            if y_offset < margin:  # New page if space is less
                pdf_canvas.showPage()
                y_offset = height - margin

        # Return the updated y_offset
        return y_offset

    # Set up the PDF for the first sheet
    pdf_canvas.setFont("Helvetica-Bold", 16)
    pdf_canvas.drawString(x_offset, y_offset, f"{contractor_profile.name} - Sheet 1")

    pdf_canvas.setFont("Helvetica", 10)
    pdf_canvas.drawString(x_offset, y_offset - 20, f"Date: {datetime.now().strftime('%d/%m/%y')}")
    pdf_canvas.drawString(x_offset, y_offset - 40, f"RA Bill No: {bill_number}")
    pdf_canvas.drawString(x_offset, y_offset - 60, "Civil Contractor Bill - Sheet 1")

    y_offset -= 100
    y_offset = draw_table(df1, y_offset, pdf_canvas)

    # Add totals for the first sheet
    y_offset -= 20
    pdf_canvas.setFont("Helvetica-Bold", 10)
    pdf_canvas.drawString(x_offset + (len(table_headers) - 3) * col_width + 2, y_offset, "Total Amount")
    pdf_canvas.drawString(x_offset + (len(table_headers) - 2) * col_width + 2, y_offset, str(total_amount_df1))

    pdf_canvas.showPage()

    # Set up the PDF for the second sheet
    y_offset = height - margin
    pdf_canvas.setFont("Helvetica-Bold", 16)
    pdf_canvas.drawString(x_offset, y_offset, f"{contractor_profile.name} - Sheet 2")

    pdf_canvas.setFont("Helvetica", 10)
    pdf_canvas.drawString(x_offset, y_offset - 20, f"Date: {datetime.now().strftime('%d/%m/%y')}")
    pdf_canvas.drawString(x_offset, y_offset - 40, f"RA Bill No: {bill_number}")
    pdf_canvas.drawString(x_offset, y_offset - 60, "Civil Contractor Bill - Sheet 2")

    y_offset -= 100
    y_offset = draw_table(df2, y_offset, pdf_canvas)

    # Add totals for the second sheet
    y_offset -= 20
    pdf_canvas.setFont("Helvetica-Bold", 10)
    pdf_canvas.drawString(x_offset + (len(table_headers) - 3) * col_width + 2, y_offset, "Total Amount")
    pdf_canvas.drawString(x_offset + (len(table_headers) - 2) * col_width + 2, y_offset, str(total_amount_df2))

    pdf_canvas.showPage()
    pdf_canvas.save()

    output_pdf.seek(0)
    response = HttpResponse(output_pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{contractor_profile.name}_bill.pdf"'

    return response