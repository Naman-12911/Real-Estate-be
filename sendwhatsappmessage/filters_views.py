from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import WhatsAppMessage
from .serializer import WhatsAppMessageSerializer
from rest_framework.permissions import IsAuthenticated
from .filters import WhatsAppMessageFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import status
from propertyStatus.models import Project


    

class WhatsAppMessageFilterGenric(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WhatsAppMessageSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = WhatsAppMessageFilter
    queryset = WhatsAppMessage.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        if not queryset.exists():
            return Response({'detail': 'No data found'}, status=status.HTTP_204_NO_CONTENT)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    