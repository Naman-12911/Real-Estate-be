from .models import User, UserHoliday, FCMTokens
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from django.contrib import auth
from datetime import datetime

class SalesSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'sales_employee',
            'sales_my_job_desk',
            'sales_add_new_lead',
            'sales_view_lead',
            'sales_dump_data',
            'sales_site_visit',
            'sales_corporate_visit'
        ]

class AccountSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
           'account_report',
            'account_property_status', 'account_direct_booking', 'account_booking_form',
            'account_payment_stages', 'account_demand_letter', 'account_documentation',
            'account_billing', 'account_clinet_loan_profile', 'account_project_document',
            'accounts_all_details','accounts_customer_details','accounts_registry_details'
        ]
# register serializers
class UserSerializers(serializers.ModelSerializer):
    sales_section = SalesSectionSerializer(source='*', required=False)
    account_section = AccountSectionSerializer(source='*', required=False)
    class Meta:
        model = User
        fields = [
            'id', 'phone_no', 'email', 'password', 'sales_employee', 
            'sales_section',  'accounts_employee', 'account_section','normal_user','name','admin', 'site_worker','is_active','platform',
            'account_report','account_property_status','account_direct_booking','account_booking_form',
            'account_payment_stages','account_demand_letter','account_documentation','account_billing','account_clinet_loan_profile',
            'account_project_document','sales_my_job_desk','sales_add_new_lead','sales_view_lead','sales_dump_data','sales_site_visit',
            'sales_corporate_visit','accounts_all_details','accounts_customer_details','accounts_registry_details'
        ]
        extra_kwargs = {
            'password' :{'write_only':True}  #  to does not return password in api ## postman
        }
    # convert password to hash key
    def create(self, validated_data):
        password = validated_data.pop('password',None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        if len(password) <6:
            raise serializers.ValidationError("entre strong password")
        instance.save()
        return instance
# login serializers


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    tokens = serializers.SerializerMethodField()
    sales_section = SalesSectionSerializer(source='*', required=False)
    account_section = AccountSectionSerializer(source='*', required=False)
    def get_tokens(self, obj):
        user = User.objects.get(email=obj['email'])

        return {
            'refresh': user.tokens()['refresh'],
            'access': user.tokens()['access']
        }

    class Meta:
        model = User
        fields = ['email', 'password', 'tokens','sales_employee','accounts_employee','site_worker','admin','normal_user','sales_section', 
                'account_section','name','phone_no','platform','account_report','account_property_status','account_direct_booking','account_booking_form',
                'account_payment_stages','account_demand_letter','account_documentation','account_billing','account_clinet_loan_profile','account_project_document',
                'sales_my_job_desk','sales_add_new_lead','sales_view_lead','sales_dump_data','sales_site_visit','sales_corporate_visit',
                'accounts_all_details','accounts_customer_details','accounts_registry_details']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        filtered_user_by_email = User.objects.filter(email=email)
        user = auth.authenticate(email=email, password=password)

        if filtered_user_by_email.exists() and filtered_user_by_email[0].auth_provider != 'email':
            raise AuthenticationFailed(
                detail='Please continue your login using ' + filtered_user_by_email[0].auth_provider)
        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')
        
        if user.sales_employee:
            if user.check_password(password):
                user_type = 'user'
                return {
                    'email': user.email,
                    'user_type': user_type,
                    'tokens': user.tokens(),
                    'sales_employee': user.sales_employee,
                    'accounts_employee': user.accounts_employee,
                    'sales_section': SalesSectionSerializer(user).data,
                     'phone_no' : user.phone_no,
                    'site_worker': user.site_worker,
                    'normal_user': user.normal_user,
                     'admin': user.admin,
                    'id': user.id,
                    'name': user.name
                }
        
        elif user.accounts_employee:
            if user.check_password(password):
                user_type = 'user'
                return {
                    'email': user.email,
                    'user_type': user_type,
                    'tokens': user.tokens(),
                    'sales_employee': user.sales_employee,
                    'accounts_employee': user.accounts_employee,
                    'phone_no' : user.phone_no,
                    'account_section': AccountSectionSerializer(user).data,
                    'site_worker': user.site_worker,
                     'normal_user': user.normal_user,
                     'admin': user.admin,
                    'id': user.id,
                    'name': user.name
                }
        elif user.site_worker:
            if user.check_password(password):
                user_type = 'user'
                return {
                    'email': user.email,
                    'user_type': user_type,
                    'tokens': user.tokens(),
                    'sales_employee': user.sales_employee,
                    'accounts_employee': user.accounts_employee,
                    'phone_no' : user.phone_no,
                    'site_worker': user.site_worker,
                     'admin': user.admin,
                      'normal_user': user.normal_user,
                    'id': user.id,
                    'name': user.name
                }
            
        elif user.admin:
            if user.check_password(password):
                user_type = 'user'
                return {
                    'email': user.email,
                    'user_type': user_type,
                    'tokens': user.tokens(),
                    'sales_employee': user.sales_employee,
                    'accounts_employee': user.accounts_employee,
                     'phone_no' : user.phone_no,
                    'site_worker': user.site_worker,
                     'admin': user.admin,
                      'normal_user': user.normal_user,
                    'id': user.id,
                    'name': user.name
                }
        elif user.normal_user:
            if user.check_password(password):
                user_type = 'user'
                return {
                    'email': user.email,
                    'user_type': user_type,
                    'tokens': user.tokens(),
                    'sales_employee': user.sales_employee,
                    'accounts_employee': user.accounts_employee,
                    'site_worker': user.site_worker,
                     'phone_no' : user.phone_no,
                     'admin': user.admin,
                      'normal_user': user.normal_user,
                    'id': user.id,
                    'name': user.name
                }
        else:
            raise AuthenticationFailed('Invalid authentication type')

        return {
            'email': user.email,
            'tokens': user.tokens
        }

        return super().validate(attrs)




class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

class HolidaySerializer(serializers.ModelSerializer):
   
    class Meta:
        model = UserHoliday
        fields = '__all__'
   
    

class FCMSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMTokens
        fields = '__all__'

    