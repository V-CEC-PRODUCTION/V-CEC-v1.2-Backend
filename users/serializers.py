from rest_framework import serializers
from .models import User
from .models import Token

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        
    
class UserGoogleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email','name','profile_image','thumbnail_profile_image','login_type','device_id','logged_in','role','branch','semester','division','admission_no','register_no','image_url', 'thumbnail_url']

class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
class OtpSerializer(serializers.Serializer):
    user_otp = serializers.CharField(max_length=6)

class GetUserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=["name","email","branch","image_url","thumbnail_url","semester","division","admission_no","register_no","ieee_membership_no"]
    
class UserSerializerToken(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = '__all__'