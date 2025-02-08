import locale
import os.path
from contextlib import suppress
from datetime import datetime
from io import BytesIO

from django.conf import settings
from django.http import HttpResponse
from docxtpl import DocxTemplate
from jinja2 import Environment
from num2words import num2words
from rest_framework.exceptions import NotFound
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from bookingForm.models import PersonalDeatils
from documentation.models import DemandLetter
from docx_gen.serializers import DocxBookingPersonalDeatils
from profileSearch.models import PaymentStageDetail


def num_to_word(input_string):
    return num2words(float(input_string), to='cardinal', lang='en_IN').title().replace(',', '').replace('-', ' ')


def reformat_date(input_string, arg="%Y-%m-%d"):
    try:
        date_obj = datetime.strptime(input_string, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        date_obj = datetime.strptime(input_string, "%Y-%m-%dT%H:%M:%S")
    return date_obj.strftime(arg)


def reformat_currency(input_string):
    locale.setlocale(locale.LC_ALL, 'en_IN.UTF-8')
    if not input_string:
        return locale.currency(0, symbol=True, grouping=False)
    return locale.currency(float(input_string), symbol=True, grouping=False)


def subtract(value, arg):
    return value - arg


class RetrieveBookingPersonalDeatilsAPIView(RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = PersonalDeatils.objects.all()
    serializer_class = DocxBookingPersonalDeatils

    def get_object(self):
        unit_no = self.request.query_params.get('unit_no')
        if unit_no is None:
            raise NotFound('Unit number query parameter is required')

        try:
            personal_detail = self.get_queryset().get(booking__unit_no__unit_no=unit_no)
        except PersonalDeatils.DoesNotExist:
            raise NotFound('Personal detail not found for the provided unit number')

        return personal_detail


class BaseGenerateDocxView(RetrieveBookingPersonalDeatilsAPIView):
    template_name = None

    def get_data(self):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return serializer.data

    def get(self, request, *args, **kwargs):
        data = self.get_data()
        try:
            data['govt_extra_charges'] = float(data['booking']['govt_extra_charges'])
        except:
            data['govt_extra_charges'] = 0
        data['cost_payable_to_company'] = float(data['booking']['cost_payable_to_company']) - data['govt_extra_charges']
        unit_no = self.request.query_params.get('unit_no')

        if not self.template_name:
            raise NotFound('Template not defined')

        env = Environment(autoescape=False)
        env.filters['num_to_word'] = num_to_word
        env.filters['reformat_date'] = reformat_date
        env.filters['reformat_currency'] = reformat_currency
        env.filters['subtract'] = subtract

        template_filepath = settings.BASE_DIR / f'docx_gen/templates/{self.template_name}'
        doc = DocxTemplate(template_filepath)
        doc.render(data, jinja_env=env)

        byte_io = BytesIO()
        doc.save(byte_io)
        byte_io.seek(0)

        response = HttpResponse(
            byte_io.read(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = f'attachment; filename="{unit_no}-{os.path.basename(template_filepath)}"'
        return response


class AllotmentLetterDraft(BaseGenerateDocxView):
    template_name = 'ALLOTMENT LETTER Draft.docx'

    def get_data(self):
        data = super().get_data()
        relevant_data = self.get_relevant_data(data)
        return {
            **data,
            "current_date": data['booking']['created_at'].split('T')[0],
            **relevant_data
        }

    @staticmethod
    def get_relevant_data(data):
        total_amount = data['booking']['cost_payable_to_company']
        paid = 0
        profile = PersonalDeatils.objects.get(id=data['id'])
        payment_stages = PaymentStageDetail.objects.filter(personal_deatils=profile)
        if len(payment_stages) > 0:
            for payment_stage in payment_stages:
                with suppress(Exception):
                    if payment_stage.paybale_amount == "":
                        amount_received = 0
                    else:
                        amount_received = float(payment_stage.paybale_amount)
                    paid += amount_received

        balance = total_amount - paid
        if data['booking']['unit_cost'] == "":
            other_charges = total_amount
        else:
            other_charges = total_amount - float(data['booking']['unit_cost'])

        return {
            "remaining_amount": balance,
            "other_charges": other_charges,
            "paid_amount": paid
        }


class DemandLetterDraft(BaseGenerateDocxView):
    template_name = 'DEMAND LETTER DRAFT.docx'

    def get_data(self):
        data = super().get_data()

        demand_letter_id = self.request.query_params.get('demand_letter_id')
        if demand_letter_id is None:
            raise NotFound('demand_letter_id query parameter is required')

        demand_letter = DemandLetter.objects.select_related("payment_stage").get(id=demand_letter_id)
        return {**data, "paybale_amount": demand_letter.payment_stage.paybale_amount}


class LetterOfPossessionDraft(BaseGenerateDocxView):
    template_name = 'LETTER OF POSSESSION Draft.docx'


class NoDuesCertificateDraft(BaseGenerateDocxView):
    template_name = 'NO DUES CERTIFICATE Draft.docx'


class TAndCPLetterDraft(BaseGenerateDocxView):
    template_name = 'T&CP Letter Draft.docx'


class BookingForm(BaseGenerateDocxView):
    template_name = 'BOOKING FORM.docx'


class FinalCostSheet(BaseGenerateDocxView):
    template_name = 'Final Cost Sheet.docx'


class BankNocAxisBankNocDraft(BaseGenerateDocxView):
    template_name = 'BANK NOC/AXIS BANK NOC DRAFT.docx'


class BankNocCanaraBankNocDraft(BaseGenerateDocxView):
    template_name = 'BANK NOC/CANARA BANK NOC DRAFT.docx'


class BankNocHdfcBankNocDraft(BaseGenerateDocxView):
    template_name = 'BANK NOC/HDFC BANK NOC DRAFT.docx'


class BankNocLicBankNocDraft(BaseGenerateDocxView):
    template_name = 'BANK NOC/LIC BANK NOC DRAFT.docx'


class BankNocPnbBankNocDraft(BaseGenerateDocxView):
    template_name = 'BANK NOC/PNB BANK NOC DRAFT.docx'


class BankNocSbiRacpcNocDraft(BaseGenerateDocxView):
    template_name = 'BANK NOC/SBI RACPC NOC DRAFT.docx'


class BankNocSbiRacpc2NocDraft(BaseGenerateDocxView):
    template_name = 'BANK NOC/SBI RACPC2 NOC DRAFT.docx'
