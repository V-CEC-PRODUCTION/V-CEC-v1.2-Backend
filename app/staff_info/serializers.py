from rest_framework import serializers
from .models import staffInfo

class StaffSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = staffInfo
        fields = ['id', 'name','designation','email_id','mobile_no','department']