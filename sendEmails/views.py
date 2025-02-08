from django.shortcuts import render
from .helper import mass_email
from rest_framework import status
from account.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import MailTemplate
from .serializer import SendMailSerializer, MailTemplateSerializer
from social.models import FbLeads

# Create your views here.
class MassEmail(APIView):
    permission_class = [IsAuthenticated]

    def post(self, request):
        # all_users = User.objects.all()
        all_fblead_obj = FbLeads.objects.filter(id__in=request.data['email_list'])
        email_list  = [i.email for i in all_fblead_obj]

        if request.data['project_name']!='All' and (request.data['project_type']=='' or  request.data['project_type']==None):
            project_name = MailTemplate.objects.get(project_name=request.data['project_name'], project_type=None)
            mail_body = project_name.mail
            project = request.data['project_name']
            all_project = False
        elif request.data['project_name']!='All' and request.data['project_type']!='':
            project_name = MailTemplate.objects.get(project_name=request.data['project_name'], project_type=request.data['project_type'])
            mail_body = project_name.mail
            project = request.data['project_name']
            all_project = False
        elif (request.data['project_name']=='' or request.data['project_name']==None) and request.data['project_type']!='':
            project_name = MailTemplate.objects.get(project_name=None, project_type=request.data['project_type'])
            mail_body = project_name.mail
            project = request.data['project_name']
            all_project = False
        else:
            mail_body = """https://www.youtube.com/watch?v=g7nltVkaYVw
                🏠 Elevate Life with CI Grand - 3BHK Duplexes 🏡

                Experience luxury at CI Grand's 3BHK duplexes in Bhopal. Prices start at just 79.95 Lakh INR for 840 sqft and 89.95 Lakh INR for 945 sqft

                🌳 1st Oxygen Park in Gated Community
                ⚽ Futsal Court for Football Enthusiasts
                🛍 Convenient Shopping Nearby
                🌿 Serene Lush Green Gardens
                🏋 Luxurious AC Gym, Yoga Room, Snooker & More
                🚪 Grand Entrance with Advanced Security
                ✨ Aesthetically Designed Entrance Lounge
                🛣 Spacious 9-meter Wide Roads
                🕉 Spiritual Haven - Temple
                🚶‍♂ Walking/Jogging Track
                💪 Outdoor Fitness Station
                🌄 Abundant Open Spaces, Beautiful Landscapes
                🧘 Vastu-Based Layout for Harmony
                🔒 Top-notch Security Services
                🚽 Modern Underground Sewage Disposal

                VIDEO - https://youtu.be/g7nltVkaYVw

                GHAR BAITHE GHAR DEKHO -https://rb.gy/412vt 

                PHOTOS - https://cibuilders.in/ci-grand-images/

                PRICE DETAILS - https://drive.google.com/file/d/11zRS4Qjqjbm23YmfwYsUbqNXMdiTOqay/view?usp=sharing

                SITE ADDRESS - https://goo.gl/maps/X5MghftNxLMnjJnH7

                CI Gateway, beside Holycross School, D- MART, Kolar Road, Bhopal (MP)

                OFFICE ADDRESS - 182, Zone-I, Maharana Pratap Nagar, Bhopal, Madhya Pradesh 462011
            """
            project = None
            project_type = None
            all_project = True

        response = mass_email(email_list, mail_body)
        data = []
        for i in request.data['email_list']:
            data.append({'user':User.objects.get(email=i), 'project_name':project, 'project_type':project_type, 'all_projects':all_project,
                "name":"", "subject_line":"","mail":mail_body})

        serializer = SendMailSerializer(data=data, many=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

class EmailTemplate(APIView):
    permission_class = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return MailTemplate.objects.get(pk=pk)
        except MailTemplate.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = MailTemplate.objects.filter(project_name=pk)
                serializer = MailTemplateSerializer(data)
                return Response(serializer.data)

            else:
                data = MailTemplate.objects.all()
                serializer = MailTemplateSerializer(data, many=True)

                return Response(serializer.data)


    def post(self, request):
        
        serializer = MailTemplateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)