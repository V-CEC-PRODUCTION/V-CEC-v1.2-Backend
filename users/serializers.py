from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        

class EmailSerializer(serializers.Serializer):
    user_email = serializers.EmailField()
    
class OtpSerializer(serializers.Serializer):
    user_otp = serializers.CharField(max_length=6)