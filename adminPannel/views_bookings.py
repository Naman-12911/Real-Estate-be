from django.shortcuts import render
from rest_framework.views import APIView
from bookingForm.models import *
from bookingForm.serializers import *
from rest_framework.permissions import IsAuthenticated
from django.http.response import Http404
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter
from rest_framework import status
from django_filters import rest_framework as filters
from realEstate.pagination import CommonPagination
# Create your views here.



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
                if 'page' in request.query_params:
                    paginator = self.pagination_class()
                    result_page = paginator.paginate_queryset(data, request)
                    serializer = BookingSerializers(result_page, many=True)
                    return paginator.get_paginated_response(serializer.data)
                else:
                    # No pagination applied, return all data
                    serializer = BookingSerializers(data, many=True)
                    return Response(serializer.data)
    def post(self, request, format=None):
        current_user = request.user
        mutable_data = request.data.copy()
        mutable_data['user'] = current_user.id
        
        # Set default value for cost_payable_to_company if not present
        if "cost_payable_to_company" not in mutable_data:
            mutable_data["cost_payable_to_company"] = 0.0
        
        if mutable_data["cost_payable_to_company"] == "":
            mutable_data["cost_payable_to_company"] = 0
            
        # Define costs to consider for calculating cost_payable_to_company
        costs = ["unit_cost", "maintainance_charges_2_year", "external_electrical_charges",
                "water_connection_charges", "corner_plot_charges", "park_face_charges",
                "registry_extra_charges", "mutation_charges", "socity_maintaince_charges",
                "govt_extra_charges", "other_charges", "wide_road_facing_charges"]

        # Calculate cost_payable_to_company
        for i in costs:
            # Handle empty strings and convert them to 0
            if mutable_data.get(i, '') == '':
                mutable_data[i] = 0
            
            mutable_data["cost_payable_to_company"] = float(mutable_data["cost_payable_to_company"]) + float(mutable_data[i])

            
            #mutable_data["cost_payable_to_company"] += float(mutable_data[i])

        # Initialize serializer with modified data
        serializer = BookingSerializers(data=mutable_data)

        # Check if the data passed is valid
        serializer.is_valid(raise_exception=True)
        
        # Save the serializer
        serializer.save()

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

        # Initialize serializer with instance to update and data
        serializer = BookingSerializers(booking_to_update, data=request.data, partial=True)

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
    pagination_class = CommonPagination
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
            data = PersonalDeatils.objects.filter(deleted=False, cancelled=False)
            
            # Check for the presence of the 'page' parameter
            if 'page' in request.query_params:
                paginator = self.pagination_class()
                result_page = paginator.paginate_queryset(data, request)
                serializer = BookingPersonalDeatils(result_page, many=True)
                
                paginated_response = paginator.get_paginated_response(serializer.data)
                
                # Add total number of pages to the response
                paginated_response.data['total_pages'] = paginator.page.paginator.num_pages
                
                return paginated_response
            else:
                # No pagination applied, return all data
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
    pagination_class = CommonPagination
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
                data = CoApplicantForm.objects.filter(deleted=False, cancelled=False).order_by('-created_at')
                if 'page' in request.query_params:
                    paginator = self.pagination_class()
                    result_page = paginator.paginate_queryset(data, request)
                    serializer = CoApplicantFormSerializers(result_page, many=True)
                    return paginator.get_paginated_response(serializer.data)
                
                else:
                    serializer = BookingPersonalDeatils(data, many=True)
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
    



    

class CoApplicantFormByUnitNo(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, unit_id):
        co_applicants = CoApplicantForm.objects.filter(personal_deatils__booking__unit_no_id=unit_id, deleted=False)
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
                data = AllDocument.objects.all()
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
