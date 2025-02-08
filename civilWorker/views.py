from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http.response import Http404
from rest_framework.response import Response
from .models import *
from .serializer import *
from social.fcm_manager import sendPush
from account.models import *
from .filters import *
from rest_framework import status
from django.db.models import Count,Sum,Q,Func, IntegerField
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

class MiscellaneousAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return Miscellaneous.objects.get(pk=pk)
        except Miscellaneous.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = self.get_object(pk)
                serializer = Miscellaneous(data)
                return Response(serializer.data)

            else:
                filterset = MiscellaneousFilter(request.GET, queryset=Miscellaneous.objects.exclude(delete=True).order_by('-created_at'))
                if filterset.is_valid():
                    queryset = filterset.qs
                else:
                    queryset = Miscellaneous.objects.exclude(delete=True).order_by('-created_at')
                serializer = MiscellaneousSerializer(queryset, many=True)

                return Response(serializer.data)
            
    def post(self, request, format=None):
        current_user = request.user
        mutable_data = request.data.copy() if request.data else {}

        mutable_data['user'] = current_user.id 
                
        serializer = MiscellaneousSerializer(data=mutable_data)

        # Check if the data passed is valid
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Return Response to User
        response = Response({
            'message': 'Miscellaneous Created Successfully',
            'data': serializer.data
        })
        return response
    
    def patch(self, request, pk=None, format=None):
        # Get the todo to update
        miscellaneous_deatils_to_update = Miscellaneous.objects.get(pk=pk)

        serializer = MiscellaneousSerializer(instance=miscellaneous_deatils_to_update, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = Response()
        response.data = {
            'message': 'Miscellaneous updated Successfully',
            'data': serializer.data
        }

        return response


class RemarksAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return Remarks.objects.get(pk=pk)
        except Remarks.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = self.get_object(pk)
                serializer = Remarks(data)
                return Response(serializer.data)

            else:
                filterset = RemarksFilter(request.GET, queryset=Remarks.objects.exclude(delete=True).order_by('-created_at'))
                if filterset.is_valid():
                    queryset = filterset.qs
                else:
                    queryset = Remarks.objects.exclude(delete=True).order_by('-created_at')
                serializer = RemarkSerializer(queryset, many=True)

                return Response(serializer.data)
            
    def post(self, request, format=None):
        current_user = request.user
        mutable_data = request.data.copy() if request.data else {}

        mutable_data['user'] = current_user.id 
                
        serializer = RemarkSerializer(data=mutable_data)

        # Check if the data passed is valid
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Return Response to User
        response = Response({
            'message': 'Remarks Created Successfully',
            'data': serializer.data
        })
        return response
    
    def patch(self, request, pk=None, format=None):
        # Get the todo to update
        remarks_deatils_to_update = Remarks.objects.get(pk=pk)

        serializer = RemarkSerializer(instance=remarks_deatils_to_update, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = Response()
        response.data = {
            'message': 'Remarks updated Successfully',
            'data': serializer.data
        }

        return response


class BillsAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return Bills.objects.get(pk=pk)
        except Bills.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = self.get_object(pk)
                serializer = Bills(data)
                return Response(serializer.data)

            else:
                filterset = BillsFilter(request.GET, queryset=Bills.objects.exclude(delete=True).order_by('-created_at'))
                if filterset.is_valid():
                    queryset = filterset.qs
                else:
                    queryset = Bills.objects.exclude(delete=True).order_by('-created_at')
                serializer = BillsSerializer(queryset, many=True)

                return Response(serializer.data)
            
    def post(self, request, format=None):
        current_user = request.user
        mutable_data = request.data.copy() if request.data else {}

        mutable_data['user'] = current_user.id 
                
        serializer = BillsSerializer(data=mutable_data)

        # Check if the data passed is valid
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Return Response to User
        response = Response({
            'message': 'Bills Created Successfully',
            'data': serializer.data
        })
        return response
    
    def patch(self, request, pk=None, format=None):
        # Get the todo to update
        bills_deatils_to_update = Bills.objects.get(pk=pk)

        serializer = BillsSerializer(instance=bills_deatils_to_update, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = Response()
        response.data = {
            'message': 'Bills updated Successfully',
            'data': serializer.data
        }

        return response

class CastToInteger(Func):
    function = 'CAST'
    template = '%(function)s(%(expressions)s AS INTEGER)'

    def __init__(self, expression, **extra):
        super().__init__(expression, output_field=IntegerField(), **extra)


class CivilStatgesAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        return get_object_or_404(CivilStatges, pk=pk)
    def get(self, request, pk=None, format=None):
        if pk:
            data = self.get_object(pk)
            # Calculate total miscellaneous amount for a single CivilStatges instance
            total_miscellaneous_amount = data.miscellaneous_expense.filter(delete=False).aggregate(
                total_amount=Sum('amount')
            )['total_amount'] or 0
            serializer = CivilStatgesSerializer(data)
            response_data = {
                "total_miscellaneous_amount": total_miscellaneous_amount,
                "result": serializer.data
            }
            return Response(response_data)

        else:
            constructor_id = request.GET.get('constructor_id')
            filterset = CivilStatgesFilter(request.GET, queryset=CivilStatges.objects.exclude(delete=True))
            if filterset.is_valid():
                queryset = filterset.qs
            else:
                queryset = CivilStatges.objects.exclude(delete=True).order_by(CastToInteger('unit__unit_no'))

            if constructor_id:
                queryset = queryset.filter(constructor_profile__id=constructor_id)

            results = []
            total_miscellaneous_amount = 0

            # Loop through each CivilStatges instance to calculate individual and total miscellaneous amounts
            for civil_stage in queryset:
                stage_total = civil_stage.miscellaneous_expense.filter(delete=False).aggregate(
                    stage_total=Sum('amount')
                )['stage_total'] or 0
                total_miscellaneous_amount += stage_total

                serializer = CivilStatgesSerializer(civil_stage)
                result_data = {
                    "civil_stage": serializer.data,
                    "miscellaneous_total": stage_total
                }
                results.append(result_data)

            response_data = {
                # "total_miscellaneous_amount": total_miscellaneous_amount,
                "results": results
            }

            return Response(response_data)
    
    # def patch(self, request, pk=None, format=None):
    #     # Get the civil stages instance to update
    #     civil_stages_details_to_update = CivilStatges.objects.get(pk=pk)

    #     # Update the instance with the provided data
    #     serializer = CivilStatgesUpdateSerializer(instance=civil_stages_details_to_update, data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)
        
    #     # Apply the logic for completed_before_hand fields before saving
    #     for i in range(1, 12):
    #         target_date_field = f'target_date_stage_{i}'
    #         completed_date_field = f'completed_date_stage_{i}'
    #         completed_before_hand_field = f'completed_before_hand_stage_{i}'
    #         percentage_stage_field = f'percentage_stage_{i}'
    #         updated_percentage_stage_field = f'updated_percentage_stage_{i}'

    #         target_date = serializer.validated_data.get(target_date_field, getattr(civil_stages_details_to_update, target_date_field))
    #         completed_date = serializer.validated_data.get(completed_date_field, getattr(civil_stages_details_to_update, completed_date_field))
    #         new_percentage = serializer.validated_data.get(percentage_stage_field, getattr(civil_stages_details_to_update, percentage_stage_field))

    #         if target_date and completed_date and completed_date <= target_date:
    #             serializer.validated_data[completed_before_hand_field] = True
    #         else:
    #             serializer.validated_data[completed_before_hand_field] = False
    #         # Save previous and new percentage values
    #         previous_percentage = getattr(civil_stages_details_to_update, percentage_stage_field)
    #         if previous_percentage != new_percentage:
    #             updated_percentage = f"Previous: {previous_percentage}, New: {new_percentage}"
    #             serializer.validated_data[updated_percentage_stage_field] = updated_percentage

    #     # Check if 'miscellaneous_expense' is provided in the request data
    #     misc_data = request.data.get('miscellaneous_expense')
    #     if misc_data:
    #         unit = civil_stages_details_to_update.unit
    #         title = misc_data.get('title')
    #         amount = misc_data.get('amount')

    #         # Check if a Miscellaneous object exists with the same unit, title, and amount
    #         misc_instance = Miscellaneous.objects.filter(
    #             Q(unit=unit) & Q(title=title) & Q(amount=amount)
    #         ).first()

    #         if not misc_instance:
    #             # If not found, create a new Miscellaneous instance
    #             misc_instance = Miscellaneous.objects.create(
    #                 user=request.user,  # assuming the user is set in the request
    #                 unit=unit,
    #                 title=title,
    #                 amount=amount
    #             )

    #         # Add the Miscellaneous instance to the CivilStatges
    #         civil_stages_details_to_update.miscellaneous_expense.add(misc_instance)

    #     # Save the updated instance
    #     serializer.save()

    #     # Create a response with the updated data
    #     response = Response()
    #     response.data = {
    #         'message': 'Civil Stages updated Successfully',
    #         'data': serializer.data
    #     }

    #     return response
    def patch(self, request, pk=None, format=None):
        # Get the CivilStatges instance to update
        civil_stages_details_to_update = CivilStatges.objects.get(pk=pk)

        # Handle 'miscellaneous_expense' separately
        misc_data = request.data.get('miscellaneous_expense', [])
        misc_ids = list(civil_stages_details_to_update.miscellaneous_expense.values_list('id', flat=True))  # Get existing IDs

        if isinstance(misc_data, dict):
            unit = civil_stages_details_to_update.unit
            title = misc_data.get('title')
            amount = misc_data.get('amount')

            # Check if a Miscellaneous object exists with the same unit, title, and amount
            misc_instance = Miscellaneous.objects.filter(
                Q(unit=unit) & Q(title=title) & Q(amount=amount)
            ).first()

            if not misc_instance:
                # If not found, create a new Miscellaneous instance
                misc_instance = Miscellaneous.objects.create(
                    user=request.user,  # assuming the user is set in the request
                    unit=unit,
                    title=title,
                    amount=amount
                )

            misc_ids.append(misc_instance.id)

        # Prepare the data for the serializer
        request_data = request.data.copy()
        request_data['miscellaneous_expense'] = misc_ids

        # Update the instance with the provided data
        serializer = CivilStatgesUpdateSerializer(instance=civil_stages_details_to_update, data=request_data, partial=True)
        serializer.is_valid(raise_exception=True)
        # Calculate the sum of all percentage_stage fields
        total_percentage = 0
        for i in range(1, 12):
            percentage_stage_field = f'percentage_stage_{i}'
            percentage_stage_value = serializer.validated_data.get(percentage_stage_field, getattr(civil_stages_details_to_update, percentage_stage_field))
            total_percentage += percentage_stage_value or 0  # Add the percentage to the total

        # Validate that the total percentage does not exceed 100
        if total_percentage > 100:
            raise ValidationError({"detail": "The total of all percentage stages must not exceed 100%."})

        # Apply the logic for completed_before_hand fields before saving
        for i in range(1, 12):
            target_date_field = f'target_date_stage_{i}'
            completed_date_field = f'completed_date_stage_{i}'
            completed_before_hand_field = f'completed_before_hand_stage_{i}'
            percentage_stage_field = f'percentage_stage_{i}'
            updated_percentage_stage_field = f'updated_percentage_stage_{i}'

            target_date = serializer.validated_data.get(target_date_field, getattr(civil_stages_details_to_update, target_date_field))
            completed_date = serializer.validated_data.get(completed_date_field, getattr(civil_stages_details_to_update, completed_date_field))
            new_percentage = serializer.validated_data.get(percentage_stage_field, getattr(civil_stages_details_to_update, percentage_stage_field))

            if target_date and completed_date and completed_date <= target_date:
                serializer.validated_data[completed_before_hand_field] = True
            else:
                serializer.validated_data[completed_before_hand_field] = False

            # Save previous and new percentage values
            previous_percentage = getattr(civil_stages_details_to_update, percentage_stage_field)
            if previous_percentage != new_percentage:
                updated_percentage = f"{previous_percentage}→{new_percentage}"
                serializer.validated_data[updated_percentage_stage_field] = updated_percentage

        # Save the updated instance
        serializer.save()

        # Create a response with the updated data
        response = Response()
        response.data = {
            'message': 'Civil Stages updated Successfully',
            'data': serializer.data
        }

        return response




class ConstructorProfileAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return ConstructorProfile.objects.get(pk=pk)
        except ConstructorProfile.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = self.get_object(pk)
                queryset = ConstructorProfile.objects.get(pk=data)
                serializer = ConstructorProfileSerializer(queryset)
                return Response(serializer.data)

            else:
                filterset = ConstructorProfileFilter(request.GET, queryset=ConstructorProfile.objects.exclude(delete=True).order_by('-created_at'))
                if filterset.is_valid():
                    queryset = filterset.qs
                else:
                    queryset = ConstructorProfile.objects.exclude(delete=True).order_by('-created_at')
                serializer = ConstructorProfileSerializer(queryset, many=True)

                return Response(serializer.data)
            
    def post(self, request, format=None):
        current_user = request.user
        mutable_data = request.data.copy() if request.data else {}

        mutable_data['user'] = current_user.id 
        # Create CivilStatges for each unit associated with the ConstructorProfile
        unit_ids = mutable_data.get('unit', [])
        square_fit_value = mutable_data.get('square_fit')
        try:
            # Fetch units and raise an exception if any unit does not exist
            units = ConstructorUnitNo.objects.filter(id__in=unit_ids)
            if (not units.exists() or len(units) != len(unit_ids)) and mutable_data['profile']!='Development Work':
                raise ValueError("One or more units provided do not exist.")

             # Check if any of the units are already assigned to another ConstructorProfile
            existing_profiles = ConstructorProfile.objects.filter(unit__in=units,delete=False).distinct()
            if existing_profiles.exists() and mutable_data['profile']!='Development Work':
                raise ValueError("One or more units are already assigned to another contractor.")

            total_percentage = 0
            if mutable_data['profile']!='Development Work':
                for i in range(1, 12):
                    percentage_value = float(mutable_data.get(f'percentage_stage_{i}', 0))
                    if percentage_value < 0 or percentage_value > 100:
                        raise ValueError(f"Percentage for stage {i} is out of bounds. It must be between 0 % and 100 %.")
                    total_percentage += percentage_value

            if total_percentage > 100:
                raise ValueError("Total percentage across all stages exceeds 100 %.")

           # If all validations pass, proceed with serialization and saving
            serializer = ConstructorProfilePostSerializer(data=mutable_data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            # serializer.is_valid(raise_exception=True)
            constructor_profile = serializer.save()
            # Update the units with the provided rate and square_fit

            units.update(rate=mutable_data['rate'])

            if square_fit_value:
                units.update(square_fit=square_fit_value)

            # Create CivilStatges for each unit associated with the ConstructorProfile
            for unit in units:
            # Prepare data for percentage fields
                percentage_data = {
                    f'percentage_stage_{i}': mutable_data.get(f'percentage_stage_{i}')
                    for i in range(1, 12)
                    if f'percentage_stage_{i}' in mutable_data
                }

                CivilStatges.objects.create(
                    user=current_user,
                    unit=unit,
                    constructor_profile=constructor_profile,
                    **percentage_data,  # Set percentage fields
                )

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
        # General catch-all for any other exceptions that may occur
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Return Response to User
        response = Response({
            'message': 'Constructor Profile Created Successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
        return response
    
    def patch(self, request, pk=None, format=None):
        # Get the ConstructorProfile instance to update
        try:
            constructor_profile = ConstructorProfile.objects.get(pk=pk)
        except ConstructorProfile.DoesNotExist:
            return Response({'error': 'ConstructorProfile not found.'}, status=status.HTTP_404_NOT_FOUND)

        mutable_data = request.data.copy() if request.data else {}

        # Get the units associated with the profile before the update
        old_units = set(constructor_profile.unit.all().values_list('id', flat=True))
        new_units = set(mutable_data.get('unit', []))

        # Detect added and removed units
        units_to_add = new_units - old_units
        units_to_remove = old_units - new_units

        conflicting_units = ConstructorUnitNo.objects.filter(
            id__in=units_to_add
        ).exclude(
            constructorprofile__isnull=True
        ).exclude(
            constructorprofile__delete=True  # Only exclude profiles that are not soft-deleted
        ).exclude(
            constructorprofile=constructor_profile  # Exclude the current constructor profile
        )

        if conflicting_units.exists():
            unit_ids = ', '.join(map(str, conflicting_units.values_list('id', flat=True)))
            return Response(
                {'error': f'Unit are already assigned to another contractor.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update the ConstructorProfile instance
        serializer = ConstructorProfilePostSerializer(instance=constructor_profile, data=mutable_data, partial=True)
        serializer.is_valid(raise_exception=True)
        constructor_profile = serializer.save()

        # Update CivilStatges: Add or Remove as needed
        current_user = request.user
        square_fit_value = mutable_data.get('square_fit')

        # Handle added units
        if units_to_add:
            new_units_objs = ConstructorUnitNo.objects.filter(id__in=units_to_add)

            # Update the units with the provided rate and square_fit if available
            if 'rate' in mutable_data:
                new_units_objs.update(rate=mutable_data['rate'])

            if square_fit_value:
                new_units_objs.update(square_fit=square_fit_value)

            for unit in new_units_objs:
                # Check if a CivilStatges entry already exists for this unit and profile
                if not CivilStatges.objects.filter(constructor_profile=constructor_profile, unit=unit).exists():
                    # Prepare percentage data with default values to avoid null constraint issues
                    percentage_data = {
                        f'percentage_stage_{i}': float(mutable_data[f'percentage_stage_{i}'])
                        for i in range(1, 12)
                        if mutable_data.get(f'percentage_stage_{i}') not in ['', None]
                    }

                    CivilStatges.objects.create(
                        user=current_user,
                        unit=unit,
                        constructor_profile=constructor_profile,
                        **percentage_data,
                    )

        # Handle removed units
        if units_to_remove:
            CivilStatges.objects.filter(
                constructor_profile=constructor_profile,
                unit_id__in=units_to_remove
            ).delete()

        response = Response({
            'message': 'Constructor Profile updated successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

        return response



class COnstructorUnitNoAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return ConstructorUnitNo.objects.get(pk=pk)
        except ConstructorUnitNo.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
        # Check if 'unassigned' filter is present in the query parameters
        unassigned_only = request.query_params.get('unassigned', None)
        
        if pk:
            data = self.get_object(pk)
            serializer = ConstructorUnitNoSerializer(data)
            return Response(serializer.data)
        else:
            if unassigned_only == 'true':
                # Filter for unassigned units only
                units = ConstructorUnitNo.objects.annotate(
                    num_profiles=Count('constructorprofile',filter=Q(constructorprofile__delete=False))
                ).filter(num_profiles=0)
            else:
                # Return all units
                units = ConstructorUnitNo.objects.all()

            serializer = ConstructorUnitNoSerializer(units, many=True)
            return Response(serializer.data)
            
    def post(self, request, format=None):
        current_user = request.user
        mutable_data = request.data.copy() if request.data else {}

        mutable_data['user'] = current_user.id 
                
        serializer = ConstructorUnitNoSerializer(data=mutable_data)

        # Check if the data passed is valid
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Return Response to User
        response = Response({
            'message': 'Constructor Unit No Created Successfully',
            'data': serializer.data
        })
        return response
    
    def patch(self, request, pk=None, format=None):
        # Get the todo to update
        COnstructorUnitNo_update = ConstructorUnitNo.objects.get(pk=pk)

        serializer = ConstructorUnitNoSerializer(instance=COnstructorUnitNo_update, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = Response()
        response.data = {
            'message': 'Constructor Unit No updated Successfully',
            'data': serializer.data
        }

        return response


