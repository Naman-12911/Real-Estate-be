from rest_framework import fields, serializers
from .models import *



class ConstructorUnitNoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConstructorUnitNo
        fields = '__all__'

class MiscellaneousSerializer(serializers.ModelSerializer):
    class Meta:
        model = Miscellaneous
        fields = '__all__'
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['name'] = self.get_user_name(instance)
        response['unit_no'] = self.get_unit_number(instance)
        return response
    def get_user_name(self, instance):
        return instance.user.name if instance.user else None
    def get_unit_number(self, instance):
        return instance.unit.unit_no if instance.unit else None


class RemarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Remarks
        fields = '__all__'
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['name'] = self.get_user_name(instance)
        response['unit_no'] = self.get_unit_number(instance)
        return response
    def get_user_name(self, instance):
        return instance.user.name if instance.user else None
    def get_unit_number(self, instance):
        return instance.unit.unit_no if instance.unit else None


class BillsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bills
        fields = '__all__'
    
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['name'] = self.get_user_name(instance)
        response['unit_no'] = self.get_unit_number(instance)
        return response
    def get_user_name(self, instance):
        return instance.user.name if instance.user else None
    def get_unit_number(self, instance):
        return instance.unit.unit_no if instance.unit else None



class CivilStatgesSerializer(serializers.ModelSerializer):
    stages = serializers.SerializerMethodField()
    miscellaneous_expense = serializers.StringRelatedField(many=True)

    class Meta:
        model = CivilStatges
        fields = ['id', 'user', 'unit', 'miscellaneous_expense', 'remark', 'bill', 'stages','created_at','updated_at','constructor_profile']
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['name'] = self.get_user_name(instance)
        response['unit_no'] = self.get_unit_number(instance)
        response['unit'] = ConstructorUnitNoSerializer(instance.unit).data
        return response
    def get_user_name(self, instance):
        return instance.user.name if instance.user else None
    def get_unit_number(self, instance):
       return instance.unit.unit_no if instance.unit else None

    def get_stages(self, obj):
        stages = [
            {
                "stage": f"Stage {i}",
                "completed": getattr(obj, f'completed_stage_{i}'),
                "completedBeforeHand": getattr(obj, f'completed_before_hand_stage_{i}'),
                "targetDate": getattr(obj, f'target_date_stage_{i}'),
                "completedDate": getattr(obj, f'completed_date_stage_{i}'),
                "percentage": getattr(obj, f'percentage_stage_{i}'),
                "updated_percentage": getattr(obj, f'updated_percentage_stage_{i}'),
                "bill_downloaded": getattr(obj, f'bill_downloaded_{i}')
            } for i in range(1, 12)
        ]
        return stages
    



class CivilStatgesUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CivilStatges
        fields = "__all__"


class ConstructorProfileSerializer(serializers.ModelSerializer):
    unit = serializers.StringRelatedField(many=True)
    class Meta:
        model = ConstructorProfile
        fields = '__all__'
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['user_name'] = self.get_user_name(instance)
        return response
    def get_user_name(self, instance):
        return instance.user.name if instance.user else None


class ConstructorProfilePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConstructorProfile
        fields = '__all__'

class ExcelFilesCivilStagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExcelFilesCivilStages
        fields = '__all__'

class InvoiceCivilStagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceCivilStages
        fields = '__all__'