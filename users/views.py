from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.core.mail import send_mail
from django.template.loader import render_to_string 
from .models import User
from .serializers import UserSerializer, EmailSerializer, OtpSerializer
import random
from datetime import datetime, timedelta
from celery import shared_task

@api_view(['POST'])
@shared_task
def send_otp(request):
    serializer = EmailSerializer(data=request.data)
    if serializer.is_valid():
        user_email = serializer.validated_data['user_email']
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])

        subject = 'Your OTP'
        
        from_email = 'proddecapp@gmail.com'
        
        html_message = render_to_string('otp_email_template.html', {'otp': otp})

        # Send the email with HTML content
        send_mail(subject, '', from_email, [user_email], html_message=html_message)

        # Convert the datetime to a string
        expiry_time = (datetime.now() + timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M:%S')

        request.session['otp'] = {
            'code': otp,
            'expiry': expiry_time
        }

        return Response({'message': 'OTP sent successfully.'}, status=status.HTTP_200_OK)
    
    return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Use the 'email' field as the username for authentication
        email = data.get('email')
        try:
            user = User.objects.get(email=email)
            
            data['username'] = user.email
        except User.DoesNotExist:
            raise print("No user found with this email address")
        
        return data

@api_view(['POST'])
def verify(request):
    serializer = OtpSerializer(data=request.data)
    if serializer.is_valid():
        user_entered_otp = serializer.validated_data['user_otp']
        stored_otp_data = request.session.get('otp')

        if stored_otp_data and (datetime.now()).strftime('%Y-%m-%dT%H:%M:%S') < stored_otp_data['expiry']:
            stored_otp = stored_otp_data['code']
            if user_entered_otp == stored_otp:
                request.session.pop('otp', None)
                return Response({'message': 'OTP verification successful.'}, status=status.HTTP_200_OK)
        return Response({'error': 'OTP verification failed.'}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
# get all users
@api_view(['GET'])
def get_all_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response({'all_users': serializer.data})

#get user by id
@api_view(['GET'])
def get_user_by_id(request, pk):
    user = User.objects.get(id=pk)
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)

# create user
@api_view(['POST'])
def sign_up_user(request):
    try:
        data = request.data.copy()

        if 'password' in data:
            data['password'] = make_password(data['password'])

        domain = data['email'].split('@')[1]

        if data['email'][0:3] != 'chn' and domain != 'ceconline.edu':
            data['role'] = 'guest'

        serializer = UserSerializer(data=data)

        if serializer.is_valid():
            user = serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except KeyError as e:
        return Response(f"Missing key: {str(e)}", status=status.HTTP_400_BAD_REQUEST)

    except ValidationError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    except IntegrityError as e:
        return Response({"detail": "An error occurred while processing your request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# update user
@api_view(['PUT'])
def update_user(request, pk):
    user = User.objects.get(id=pk)
    serializer = UserSerializer(instance=user, data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        
    return Response(serializer.data)


# delete user
@api_view(['DELETE'])
def delete_user(request, pk):
     
    try:
        user = User.objects.get(id=pk)
        
        user.delete()
    
        return Response("User deleted successfully!", status=status.HTTP_204_NO_CONTENT)
    
    except ObjectDoesNotExist:
        return Response("User does not exist!", status=status.HTTP_404_NOT_FOUND)
    
# sign up user using google auth
@api_view(['POST'])
def sign_up_user_google(request):
    try:
        data = request.data.copy()
        
        domain = data['email'].split('@')[1]
        
        if data['email'][0:3] != 'chn' and domain != 'ceconline.edu':
            data['role'] = 'guest'
            
        serializer = UserSerializer(data=data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            refresh = RefreshToken.for_user(user)
            
            return Response({'user': serializer.data,'refresh': str(refresh),  'access': str(refresh.access_token) }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except KeyError as e:
        return Response(f"Missing key: {str(e)}", status=status.HTTP_400_BAD_REQUEST)

    except ValidationError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"detail": "An error occurred while processing your request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      

# login using google auth
@api_view(['POST'])
def login_user_google(request):
    try:
        user_instance=User.objects.get(email=request.data['email'])
        
        if user_instance.login_type == 'google':
            refresh = RefreshToken.for_user(user_instance)
            
            user_instance.logged_in = True
            user_instance.save()
            
            serializer = UserSerializer(user_instance, many=False)
            return Response({'user': serializer.data, 'refresh': str(refresh), 'access': str(refresh.access_token)})
        else:
            return Response("User is not registered with google!", status=status.HTTP_400_BAD_REQUEST)
    
    except ObjectDoesNotExist:
        return Response("User does not exist!", status=status.HTTP_404_NOT_FOUND)
    
# login user
@api_view(['POST'])
def login_user(request):
    try:
        user = User.objects.get(email=request.data['email'])
        
        if check_password(request.data['password'], user.password):
            # Generate refresh and access tokens
            refresh = RefreshToken.for_user(user)
            
            # Update user's login status
            user.logged_in = True
            user.save()
            
            # Return user data along with tokens
            serializer = UserSerializer(user, many=False)
            return Response({'user': serializer.data, 'refresh': str(refresh), 'access': str(refresh.access_token)})
        else:
            return Response("Password is incorrect!", status=status.HTTP_400_BAD_REQUEST)
    
    except ObjectDoesNotExist:
        return Response("User does not exist!", status=status.HTTP_404_NOT_FOUND)
    
# logout user
@api_view(['POST'])
def logout_user(request):
    try:
        user = User.objects.get(email=request.data['email'])
        
        if user.logged_in:
            # Blacklist the user's refresh token to invalidate it
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                try:
                    refresh = RefreshToken(refresh_token)
                    refresh.blacklist()
                except TokenError:
                    pass  # Invalid token, no action required
                    
            user.logged_in = False
            user.save()
            serializer = UserSerializer(user, many=False)
            return Response(serializer.data)
        else:
            return Response("User is not logged in!", status=status.HTTP_400_BAD_REQUEST)
    
    except ObjectDoesNotExist:
        return Response("User does not exist!", status=status.HTTP_404_NOT_FOUND)