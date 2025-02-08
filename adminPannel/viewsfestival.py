from django.shortcuts import render
from rest_framework.views import APIView
from festival.serializer import *
from rest_framework.permissions import IsAuthenticated
from django.http.response import Http404
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework import status
from django_filters import rest_framework as filters
from festival.models import *


class FestivalPostAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return FestivalPost.objects.get(pk=pk)
        except FestivalPost.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = self.get_object(pk)
                serializer = FestivalPost(data)
                return Response(serializer.data)

            else:
                data = FestivalPost.objects.all()
                serializer = FestivalPostSerializer(data, many=True)

                return Response(serializer.data)
            
    def post(self, request, format=None):
        current_user = request.user
        mutable_data = request.data.copy() if request.data else {}

        mutable_data['user'] = current_user.id 
                
        serializer = FestivalPostSerializer(data=mutable_data)

        # Check if the data passed is valid
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Return Response to User
        response = Response({
            'message': 'Festival Created Successfully',
            'data': serializer.data
        })
        return response

    
    def patch(self, request, pk=None, format=None):
        # Get the todo to update
        FestivalPost_deatils_to_update = FestivalPost.objects.get(pk=pk)

        serializer = FestivalPostSerializer(instance=FestivalPost_deatils_to_update, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = Response()
        response.data = {
            'message': 'Festival updated Successfully',
            'data': serializer.data
        }

        return response

    def delete(self, request, pk, format=None):
        Festival_to_delete =  FestivalPost.objects.get(pk=pk)

            # delete the todo
        Festival_to_delete.delete()

        return Response({
            'message': 'Festival Deleted Successfully'
        })