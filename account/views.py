from .serializer import UserSerializers,UserLoginSerializer,PasswordResetSerializer,HolidaySerializer,FCMSerializer
from rest_framework.response import Response
from .models import User # import models
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework import status
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User,UserHoliday, FCMTokens
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from django.contrib.auth.forms import PasswordResetForm
from django.http.response import Http404
from datetime import datetime
from social.models import FbLeads, LeadEdit
from django.db.models import Q
from social.fcm_manager import sendPush
from social.serializer import NotificationStoreSerializer
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from fcm_django.models import FCMDevice

# register the user
class Register(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializers
    # renderer_classes = (UserRenderer,)
    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        success_message = "User created successfully."
        user = User.objects.get(email=user_data['email'])
       # token = RefreshToken.for_user(user).access_token
        return Response(user_data, status=status.HTTP_201_CREATED)
    
# login apis
class Login(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class userData(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        serializer = UserSerializers(self.request.user)
        return Response(serializer.data)

# update the user details
class update_profile(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializers
    def update(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class PasswordResetAPIView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        form = PasswordResetForm(serializer.validated_data)
        if form.is_valid():
            form.save(request=request)
            return Response({'detail': 'Password reset email has been sent.'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Failed to send password reset email.'}, status=status.HTTP_400_BAD_REQUEST)
        


# Get ALl users only sales Person
        
class AccountUsersApiview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = self.get_object(pk)
                serializer = User(data)
                return Response(serializer.data)

            else:
                data = User.objects.all()
                serializer = UserSerializers(data, many=True)

                return Response(serializer.data)
            
class HolidayView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return UserHoliday.objects.filter(user__pk=pk)
        except UserHoliday.DoesNotExist:
            raise Http404
        
    def get(self, request, format=None):
        users = User.objects.all()
        today = datetime.now().date()
        holiday_status_data = []

        for user in users:
            is_on_holiday = UserHoliday.objects.filter(user=user,from_date__lte=today, to_date__gte=today).exists()
            reason ='N/A'
            if is_on_holiday:
                reason = ""
                holiday_entry = UserHoliday.objects.filter(user=user, from_date__lte=today, to_date__gte=today)
                for i in holiday_entry:
                    reason+=i.reason+"\n"
            user_data = {
                'id': user.pk,
                'name': user.name,  # Replace 'name' with the actual field name in your User model
                'phone_no': user.phone_no,  # Replace 'phone_no' with the actual field name in your User model
                'email': user.email,  # Replace 'email' with the actual field name in your User model
                'holiday_status': is_on_holiday,
                'reason':reason,
                'assign':user.assign,
                'is_active': user.is_active,
                'sales_employee' : user.sales_employee,
                'accounts_employee':user.accounts_employee,
                'site_worker':user.site_worker,
                'normal_user':user.normal_user,
                'admin':user.admin
            }
            holiday_status_data.append(user_data)

        return Response(holiday_status_data, status=status.HTTP_200_OK)
    
    # def post(self, request):
    #     data = request.data
    #     data['user'] = request.user.pk

    #     serializer = HolidaySerializer(data=data)
    #     if not serializer.is_valid():
    #         return Response(serializer.errors)
        
    #     serializer.save()

    #     return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.pk
        serializer = HolidaySerializer(data=request.data)
        
        # Check if the data passed is valid
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        
        response_data = {
            'message': 'Holiday of agent created successfully',
            'data': serializer.data
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
    
class FCMTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return FCMTokens.objects.filter(user__pk=pk)
        except FCMTokens.DoesNotExist:
            raise Http404
        
    def get(self, request,pk=None,format=None):
        user_id = request.user.pk
        queryset = self.get_object(user_id)
        serializer = FCMSerializer(queryset,many=True)

        return Response(serializer.data)
    
    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.pk

        serializer = FCMSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors)
        
        serializer.save()

        response = Response()

        response.data = {
            'message': 'Device token saved Successfully',
            'data': serializer.data
        }

        return response

class AccountUsersSalesPersonApiview(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404
        
    def get(self, request, pk=None, format=None):
            if pk:
                data = self.get_object(pk)
                serializer = User(data)
                return Response(serializer.data)

            else:
                data = User.objects.filter(sales_employee=True)
                serializer = UserSerializers(data, many=True)

                return Response(serializer.data)

class DeactivateAccount(APIView):
    permission_classes = [IsAuthenticated]

    def get_last(self):
        query = FbLeads.objects.all().last()
        users = User.objects.filter(sales_employee=True)
        users_on_leave = UserHoliday.objects.filter(Q(from_date__lte=datetime.now()),Q(to_date__gte=datetime.now())).values('user')
        user_holiday_user_ids = {user_holiday['user'] for user_holiday in users_on_leave}
        if query:
            query = query.assigned_to
            rearrange_idx = 0
            for idx in range(len(users)):
                if users[idx].pk==query.pk:
                    if len(users)-1>idx:
                        rearrange_idx = idx
                    else:
                        rearrange_idx = 0
                    break
            users = users[rearrange_idx+1:] + users[:rearrange_idx+1]
        users_list = []
        for idx in range(len(users)):
            if users[idx] not in user_holiday_user_ids:
                users_list.append(users[idx])

        return users_list

    def post(self, request):
        user = request.user
        if user.admin:
            response = Response()
            try:
                dis_user = User.objects.get(email=request.data['email'])
                dis_user.is_active = False
                dis_user.save()
                response.data = {'message': 'User account deactivated successfully'}
            except Exception as e:
                # print("Error during deactivation process", e)
                response.data = {'message': 'User account deactivation failed'}
        else:
            response.data = {'message': 'Permission denied'}

        return response
        
        # else:
        #     return Response({'message':'You do not have permission to perform this action'})
        
class AgentAssignAPI(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = User.objects.get(phone_no=request.GET.get('phone_no'))
        user.assign = False
        user.save()
        return Response({'message':'User account deactivated for lead assignment sucessfully'})

class GetFMCTokens(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tokens = FCMTokens.objects.filter(user=request.user)

        response = {'token':[]}
        for i in tokens:
            response['token'].append(str(i.device_token))

        return Response(response)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Get the platform from the request data
            # platform = request.data.get('platform')
            # if platform not in ['web', 'app']:
            #     return Response({"detail": "Invalid platform."}, status=status.HTTP_400_BAD_REQUEST)

            # Blacklist the refresh token
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            # Delete the FCM token for the specific platform
            FCMTokens.objects.filter(user=request.user).delete()

            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class DeleteAccountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        token = request.auth  # Get the current token from the request

        try:
            # Blacklist the current token
            if isinstance(token, OutstandingToken):
                BlacklistedToken.objects.get_or_create(token=token)
            
            # Delete the FCM tokens associated with this device/user
            FCMDevice.objects.filter(user=user).delete()
            
            # Delete the user account
            user.is_active = False
            user.save()

            return Response({"detail": "Account deleted successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Get all the employee deatils like active employee and in active employee

class ActiveAndInActiveEmployee(APIView):
    def get(self, request, *args, **kwargs):
        active_employees = User.objects.filter(is_active=True)
        inactive_employees = User.objects.filter(is_active=False)

        active_serializer = UserSerializers(active_employees, many=True)
        inactive_serializer = UserSerializers(inactive_employees, many=True)

        return Response({
            'active_employees': active_serializer.data,
            'inactive_employees': inactive_serializer.data
        }, status=status.HTTP_200_OK)