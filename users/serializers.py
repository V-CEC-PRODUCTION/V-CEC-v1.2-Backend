from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        
        
class UserGoogleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email','name','profile_image','thumbnail_profile_image','login_type','device_id','logged_in','role','branch','semester','division','admission_no','register_no']
        
class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
class OtpSerializer(serializers.Serializer):
    user_otp = serializers.CharField(max_length=6)