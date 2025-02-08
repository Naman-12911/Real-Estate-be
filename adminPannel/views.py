from django.shortcuts import render
from .models import *
from propertyStatus.serializer import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http.response import Http404
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter
from rest_framework import status
from django_filters import rest_framework as filters
from rest_framework.status import HTTP_204_NO_CONTENT
from realEstate.pagination import CommonPagination

# Create your views here.

class ProjectAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = self.get_object(pk)
                serializer = ProjectSerializer(data)
                return Response(serializer.data)

            else:
                data = Project.objects.all().order_by('-created_at')
                serializer = ProjectSerializer(data, many=True)

                return Response(serializer.data)
    def post(self, request, format=None):
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            
            serializer = ProjectSerializer(data=mutable_data)

            # Check if the data passed is valid
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Return Response to User

            response = Response()

            response.data = {
                'message': 'Project Created Successfully',
                'data': serializer.data
            }
            return response
    
    def patch(self, request, pk=None, format=None):
                # Get the todo to update
            Booking_to_update = Project.objects.get(pk=pk)

            serializer = ProjectSerializer(instance=Booking_to_update,data=request.data, partial=True)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = Response()

            response.data = {
                'message': 'Project upated Successfully',
                'data': serializer.data
            }

            return response
    def delete(self, request, pk, format=None):
        Carrer_to_delete =  Project.objects.get(pk=pk)

            # delete the todo
        Carrer_to_delete.delete()

        return Response({
            'message': 'Project Deleted Successfully'
        })



class ProjectTypAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return ProjectType.objects.get(pk=pk)
        except ProjectType.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = self.get_object(pk)
                serializer = ProjectTypeSerializer(data)
                return Response(serializer.data)

            else:
                data = ProjectType.objects.all().order_by('-created_at')
                serializer = ProjectTypeSerializer(data, many=True)

                return Response(serializer.data)
    def post(self, request, format=None):
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            
            serializer = ProjectTypeSerializer(data=mutable_data)

            # Check if the data passed is valid
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Return Response to User

            response = Response()

            response.data = {
                'message': 'project type Created Successfully',
                'data': serializer.data
            }
            return response
    
    def patch(self, request, pk=None, format=None):
                # Get the todo to update
            Booking_to_update = ProjectType.objects.get(pk=pk)

            serializer = ProjectTypeSerializer(instance=Booking_to_update,data=request.data, partial=True)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = Response()

            response.data = {
                'message': 'Project type upated Successfully',
                'data': serializer.data
            }

            return response
    def delete(self, request, pk, format=None):
        Project_type_to_delete =  ProjectType.objects.get(pk=pk)

            # delete the todo
        Project_type_to_delete.delete()

        return Response({
            'message': 'Project type Deleted Successfully'
        })
    


class UnitNoAPIview(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class =CommonPagination
    def get_object(self, pk):
        try:
            return UnitNo.objects.get(pk=pk)
        except UnitNo.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = self.get_object(pk)
                serializer = UnitNoSerializer(data)
                return Response(serializer.data)

            else:
                data = UnitNo.objects.all().order_by('-created_at')
                paginator = self.pagination_class()
                result_page = paginator.paginate_queryset(data, request)
                serializer = UnitNoSerializer(result_page, many=True)
                return paginator.get_paginated_response(serializer.data)
    def post(self, request, format=None):
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            
            serializer = UnitNoSerializer(data=mutable_data)

            # Check if the data passed is valid
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Return Response to User

            response = Response()

            response.data = {
                'message': 'Unit number Created Successfully',
                'data': serializer.data
            }
            return response
    
    def patch(self, request, pk=None, format=None):
                # Get the todo to update
            phase_to_update = UnitNo.objects.get(pk=pk)

            serializer = UnitNoSerializer(instance=phase_to_update,data=request.data, partial=True)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = Response()

            response.data = {
                'message': 'Phase upated Successfully',
                'data': serializer.data
            }

            return response

          
    def delete(self, request, pk, format=None):
        Unit_no_to_delete =  UnitNo.objects.get(pk=pk)

            # delete the todo
        Unit_no_to_delete.delete()

        return Response({
            'message': 'unit number Deleted Successfully'
        })

class PhaseAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return Phase.objects.get(pk=pk)
        except Phase.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = self.get_object(pk)
                serializer = PhaseSerializer(data)
                return Response(serializer.data)

            else:
                data = Phase.objects.all().order_by('-created_at')
                serializer = PhaseSerializer(data, many=True)

                return Response(serializer.data)
    def post(self, request, format=None):
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            
            serializer = PhaseSerializer(data=mutable_data)

            # Check if the data passed is valid
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Return Response to User

            response = Response()

            response.data = {
                'message': 'Phase  Created Successfully',
                'data': serializer.data
            }
            return response
    
    def patch(self, request, pk=None, format=None):
                # Get the todo to update
            phase_to_update = Phase.objects.get(pk=pk)

            serializer = PhaseSerializer(instance=phase_to_update,data=request.data, partial=True)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = Response()

            response.data = {
                'message': 'Phase upated Successfully',
                'data': serializer.data
            }

            return response
    def delete(self, request, pk, format=None):
        Phase_to_delete =  Phase.objects.get(pk=pk)

            # delete the todo
        Phase_to_delete.delete()

        return Response({
            'message': 'phase Deleted Successfully'
        })

class StatusAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return Status.objects.get(pk=pk)
        except Status.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = self.get_object(pk)
                serializer =StatusSerializer(data)
                return Response(serializer.data)

            else:
                data = Status.objects.all().order_by('-created_at')
                serializer = StatusSerializer(data, many=True)

                return Response(serializer.data)
    def post(self, request, format=None):
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            
            serializer = StatusSerializer(data=mutable_data)

            # Check if the data passed is valid
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Return Response to User

            response = Response()

            response.data = {
                'message': 'Status  Created Successfully',
                'data': serializer.data
            }
            return response
    
    def patch(self, request, pk=None, format=None):
                # Get the todo to update
            phase_to_update = Status.objects.get(pk=pk)

            serializer = StatusSerializer(instance=phase_to_update,data=request.data, partial=True)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = Response()

            response.data = {
                'message': 'Status upated Successfully',
                'data': serializer.data
            }

            return response
    def delete(self, request, pk, format=None):
        phase_to_delete =  Status.objects.get(pk=pk)

            # delete the todo
        phase_to_delete.delete()

        return Response({
            'message': 'Status Deleted Successfully'
        })



class TaxTypeAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return TaxType.objects.get(pk=pk)
        except TaxType.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = self.get_object(pk)
                serializer =TaxTypeSerializer(data)
                return Response(serializer.data)

            else:
                data = TaxType.objects.all().order_by('-created_at')
                serializer = TaxTypeSerializer(data, many=True)

                return Response(serializer.data)
    def post(self, request, format=None):
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            
            serializer = TaxTypeSerializer(data=mutable_data)

            # Check if the data passed is valid
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Return Response to User

            response = Response()

            response.data = {
                'message': 'Tax Type  Created Successfully',
                'data': serializer.data
            }
            return response
    
    def patch(self, request, pk=None, format=None):
                # Get the todo to update
            tax_type_to_update = TaxType.objects.get(pk=pk)

            serializer = TaxTypeSerializer(instance=tax_type_to_update,data=request.data, partial=True)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = Response()

            response.data = {
                'message': 'Tax Type upated Successfully',
                'data': serializer.data
            }

            return response
    def delete(self, request, pk, format=None):
        tax_type_to_delete =  TaxType.objects.get(pk=pk)

            # delete the todo
        tax_type_to_delete.delete()

        return Response({
            'message': 'Tax Type Deleted Successfully'
        })
    



class UnitNoListunbookedAllViewunitnumber(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        print("View executed")  # Debugging statement

        project_id = request.query_params.get('project_id')
        print("Project ID:", project_id)  # Debugging statement

        queryset = UnitNo.objects.all()
        print("Original queryset:", queryset)  # Debugging statement

        if project_id:
            queryset = queryset.filter(projects_id=project_id, available=True)
        else:
            queryset = queryset.filter(available=True)

        print("Filtered queryset:", queryset)  # Debugging statement

        serializer = UnitNoSerializer(queryset, many=True)
        return Response(serializer.data)
    

class UnitNoListbookedAllViewunitnumber(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        project_id = request.query_params.get('project_id')

        queryset = UnitNo.objects.all()

        if project_id:
            queryset = queryset.filter(projects_id=project_id, available=False)
        else:
            queryset = queryset.filter(available=False)

        serializer = UnitNoSerializer(queryset, many=True)
        return Response(serializer.data)
 


class ProjectDocumentTypeAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return ProjectDocumentType.objects.get(pk=pk)
        except ProjectDocumentType.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = self.get_object(pk)
                serializer =ProjectDocumentTypeSerializer(data)
                return Response(serializer.data)

            else:
                data = ProjectDocumentType.objects.all().order_by('-created_at')
                serializer = ProjectDocumentTypeSerializer(data, many=True)

                return Response(serializer.data)
    def post(self, request, format=None):
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            
            serializer = ProjectDocumentTypeSerializer(data=mutable_data)

            # Check if the data passed is valid
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Return Response to User

            response = Response()

            response.data = {
                'message': 'Project Document Type  Created Successfully',
                'data': serializer.data
            }
            return response
    
    def patch(self, request, pk=None, format=None):
                # Get the todo to update
            ProjectDocumentType_to_update = ProjectDocumentType.objects.get(pk=pk)

            serializer = ProjectDocumentTypeSerializer(instance=ProjectDocumentType_to_update,data=request.data, partial=True)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = Response()

            response.data = {
                'message': 'Project Document Type upated Successfully',
                'data': serializer.data
            }

            return response
    def delete(self, request, pk, format=None):
        ProjectDocumentType_to_delete =  ProjectDocumentType.objects.get(pk=pk)

            # delete the todo
        ProjectDocumentType_to_delete.delete()

        return Response({
            'message': 'Project Document Type Deleted Successfully'
        })
    

class ProjectDocumentAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return ProjectDocument.objects.get(pk=pk)
        except ProjectDocument.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = self.get_object(pk)
                serializer =ProjectDocumentSerializer(data)
                return Response(serializer.data)

            else:
                data = ProjectDocument.objects.all().order_by('-created_at')
                serializer = ProjectDocumentSerializer(data, many=True)

                return Response(serializer.data)
    def post(self, request, format=None):
            current_user = request.user
            mutable_data = request.data.copy()
            mutable_data['user'] = current_user.id 
            
            serializer = ProjectDocumentSerializer(data=mutable_data)

            # Check if the data passed is valid
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Return Response to User

            response = Response()

            response.data = {
                'message': 'Project Document  Created Successfully',
                'data': serializer.data
            }
            return response
    
    def patch(self, request, pk=None, format=None):
                # Get the todo to update
            ProjectDocument_to_update = ProjectDocument.objects.get(pk=pk)

            serializer = ProjectDocumentSerializer(instance=ProjectDocument_to_update,data=request.data, partial=True)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = Response()

            response.data = {
                'message': 'Project Document upated Successfully',
                'data': serializer.data
            }

            return response
    def delete(self, request, pk, format=None):
        ProjectDocument_to_delete =  ProjectDocument.objects.get(pk=pk)

            # delete the todo
        ProjectDocument_to_delete.delete()

        return Response({
            'message': 'Project Document Deleted Successfully'
        })