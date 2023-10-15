from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.core.mail import send_mail
from django.template.loader import render_to_string 
from forum_stories.models import UserCountStories
from forum_management.models import AddForum
from .models import User, Token
from .serializers import UserSerializer, EmailSerializer, OtpSerializer, UserGoogleSerializer
import random
from datetime import datetime, timedelta
from celery import shared_task
from .utils import TokenUtil
import jwt, json



@api_view(['POST'])
@shared_task
def send_otp(request):
    serializer = EmailSerializer(data=request.data)
    if serializer.is_valid():
        user_email = serializer.validated_data['email']
        
        email_db = User.objects.filter(email=user_email, login_type='email').first()
        
        if email_db:
            return {'error': 'Email already exists.'}
        
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

        return Response({'message': 'OTP sent successfully.','otp': otp}, status=status.HTTP_200_OK)
    
    return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class VerifyOtp(APIView):
    def post(self, request):
        serializer = OtpSerializer(data=request.data)
        if serializer.is_valid():
            user_entered_otp = serializer.validated_data['user_otp']
            stored_otp_data = request.session.get('otp')

            if stored_otp_data and (datetime.now()).strftime('%Y-%m-%dT%H:%M:%S') < stored_otp_data['expiry']:
                stored_otp = stored_otp_data['code']
                if user_entered_otp == stored_otp:
                    request.session.pop('otp', None)
                    return Response({'message': 'OTP verification successful.'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'OTP verification failed.'}, status=status.HTTP_400_BAD_REQUEST)
                
            else:
                request.session.pop('otp', None)
                return Response({'error': 'OTP has expired.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
# get all users
class GetAllUsers(APIView):
    def get(self,request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response({'all_users': serializer.data})

#get user by id
class GetUserById(APIView):
    def get(self,request, pk):
        user = User.objects.get(id=pk)
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)

# create user
class SignUpUser(APIView):
    def post(self,request):
        try:
            data = request.data.copy()
            
            email_db = User.objects.filter(email=data['email'], login_type='email').first()
            
            if email_db:
                return Response({'error': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
            
            if 'password' in data:
                data['password'] = make_password(data['password'])

            domain = data['email'].split('@')[1]

            if data['email'][0:3] != 'chn' and domain != 'ceconline.edu':
                data['role'] = 'guest'
            else:
                data['register_no'] = str(data['email'].split('@')[0]).upper()

            serializer = UserSerializer(data=data)

            if serializer.is_valid():
                user = serializer.save()
                

                converted_data = UserCountStories.objects.values('count').distinct()

                        
                user_count_stories_instance = UserCountStories(user_id=user, count=converted_data[0]['count'])

                # Save the UserCountStories instance to store the JSON data
                user_count_stories_instance.save()
                

                access_token, refresh_token = TokenUtil.generate_tokens(user)
                

    # Validate tokens
                if TokenUtil.validate_tokens(access_token, refresh_token):
                    return Response({'access_token': access_token, 'refresh_token': refresh_token}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid tokens.'}, status=status.HTTP_401_UNAUTHORIZED)
                
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except KeyError as e:
            return Response(f"Missing key: {str(e)}", status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError as e:
            return Response({"detail": "An error occurred while processing your request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# update user
class UpdateUser(APIView):
    def update(request, pk):
        user = User.objects.get(id=pk)
        serializer = UserSerializer(instance=user, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            
        return Response(serializer.data)


# delete user
class DeleteUser(APIView):
    def delete(self,request,pk):
        
        try:
            user = User.objects.get(id=pk)
            
            user.delete()
        
            return Response("User deleted successfully!", status=status.HTTP_204_NO_CONTENT)
        
        except ObjectDoesNotExist:
            return Response("User does not exist!", status=status.HTTP_404_NOT_FOUND)
    
# sign up user using google auth
class SignUpUserGoogle(APIView):
    def post(self,request):
        try:
            data = request.data.copy()
            
            email_db = User.objects.filter(email=data['email'], login_type='google').first()
            
            if email_db:
                return Response({'error': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
            
            domain = data['email'].split('@')[1]
            
            if data['email'][0:3] != 'chn' and domain != 'ceconline.edu':
                data['role'] = 'guest'
            else:
                data['register_no'] = str(data['email'].split('@')[0]).upper()
            
            data['login_type'] = 'google'
            
            serializer = UserGoogleSerializer(data=data)
            
            if serializer.is_valid():
                
                
                user = serializer.save()
                
                converted_data = UserCountStories.objects.values('count').distinct()

                        
                user_count_stories_instance = UserCountStories(user_id=user, count=converted_data[0]['count'])

                # Save the UserCountStories instance to store the JSON data
                user_count_stories_instance.save()
                

                access_token, refresh_token = TokenUtil.generate_tokens(user)
                
                # Validate tokens
                if TokenUtil.validate_tokens(access_token, refresh_token):
                    return Response({'access_token': access_token, 'refresh_token': refresh_token}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid tokens.'}, status=status.HTTP_401_UNAUTHORIZED)     
                
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except KeyError as e:
            return Response(f"Missing key: {str(e)}", status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"detail": "An error occurred while processing your request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      

class UserDetails(APIView):
    def post(self, request):
        authorization_header = request.META.get("HTTP_AUTHORIZATION")
        
        if not authorization_header:
            return Response({"error": "Access token is missing."}, status=status.HTTP_401_UNAUTHORIZED)


        _, token = authorization_header.split()
        
        token_key = Token.objects.filter(access_token=token).first()
        
        if not token_key:
            return Response({"error": "Invalid access token."}, status=status.HTTP_401_UNAUTHORIZED)
        

        payload = TokenUtil.decode_token(token_key.access_token)

        # Optionally, you can extract user information or other claims from the payload
        if not payload:
            return Response({"error": "Invalid access token."}, status=status.HTTP_401_UNAUTHORIZED)

        # Check if the refresh token is associated with a user (add your logic here)
        user_id = payload.get('id')
        
        if not user_id:
            return Response({'error': 'The access token is not associated with a user.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        user = User.objects.get(id=user_id) 
        
        if not user:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        
        try:
            if request.data:
                
                user.name = request.data['name']
                user.branch = request.data['branch']
                user.semester = request.data['semester']
                user.division = request.data['division']
                user.admission_no = request.data['admission_no']
                user.device_id = request.data['device_id']
                user.gender = request.data['gender']
                user.logged_in = True
                
                user.save()      
                    
                return Response({'message': 'User details updated successfully.'}, status=status.HTTP_200_OK)
            
        except ObjectDoesNotExist:
            return Response("User does not exist!", status=status.HTTP_404_NOT_FOUND)
        
         
class GetUserRole(APIView):
    def get(self,request):
        authorization_header = request.META.get("HTTP_AUTHORIZATION")
        
        if not authorization_header:
            return Response({"error": "Access token is missing."}, status=status.HTTP_401_UNAUTHORIZED)


        _, token = authorization_header.split()
        
        token_key = Token.objects.filter(access_token=token).first()
        
        if not token_key:
            return Response({"error": "Invalid access token."}, status=status.HTTP_401_UNAUTHORIZED)
        

        payload = TokenUtil.decode_token(token_key.access_token)

        # Optionally, you can extract user information or other claims from the payload
        if not payload:
            return Response({"error": "Invalid access token."}, status=status.HTTP_401_UNAUTHORIZED)

        # Check if the refresh token is associated with a user (add your logic here)
        user_id = payload.get('id')
        
        if not user_id:
            return Response({'error': 'The access token is not associated with a user.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        user = User.objects.get(id=user_id) 
        
        if not user:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        
        try: 
            return Response({'role': user.role}, status=status.HTTP_200_OK)
        
        except ObjectDoesNotExist:
            return Response("User does not exist!", status=status.HTTP_404_NOT_FOUND)
             
class ValidateTokenView(APIView):
    def post(self, request):
        authorization_header = request.META.get("HTTP_AUTHORIZATION")

        if not authorization_header:
            return Response({"error": "Access token is missing."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            _, token = authorization_header.split()
            
            token_key = Token.objects.filter(access_token=token).first()
            
            if not token_key:
                return Response({"error": "Invalid access token."}, status=status.HTTP_401_UNAUTHORIZED)
            

            payload = TokenUtil.decode_token(token_key.access_token)

            # Optionally, you can extract user information or other claims from the payload
            if not payload:
                return Response({"error": "Invalid access token."}, status=status.HTTP_401_UNAUTHORIZED)

            # Implement additional authorization logic here if needed

        except (jwt.ExpiredSignatureError, jwt.DecodeError, ValueError, User.DoesNotExist):
            return Response({"error": "Invalid or expired access token."}, status=status.HTTP_401_UNAUTHORIZED)

        # Access token is valid; you can proceed with request processing
        return Response({"message": "Access token is valid."}, status=status.HTTP_200_OK)
        
# login using google auth
class LoginUserGoogle(APIView):
    def post(self,request):
        try:
            user=User.objects.get(email=request.data['email'], login_type='google')
            
            if user is not None:
                
                
                if user.logged_in and user.device_id != '':
                    user_token = Token.objects.get(user_id=user.id)
                    
                    user_token.delete()
                
                
                
                access_token, refresh_token = TokenUtil.generate_tokens(user)
                
                # Validate tokens
                if TokenUtil.validate_tokens(access_token, refresh_token):
                    user.logged_in = True
                    user.save()

                    return Response({'access_token': access_token, 'refresh_token': refresh_token}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid tokens.'}, status=status.HTTP_401_UNAUTHORIZED) 


            else:
                return Response("User is not registered with google!", status=status.HTTP_400_BAD_REQUEST)
        
        except ObjectDoesNotExist:
            return Response("User does not exist!", status=status.HTTP_404_NOT_FOUND)
    
# login user
class LoginUser(APIView):
    def post(self,request):
        try:
            user = User.objects.get(email=request.data['email'], login_type='email')
            
            if user is not None:
                
                if user.logged_in:
                    user_token = Token.objects.get(user_id=user.id)
                    
                    user_token.delete()
                    
                if check_password(request.data['password'], user.password):
                    # Generate refresh and access tokens
                    access_token, refresh_token = TokenUtil.generate_tokens(user)
                    
                    # Validate tokens
                    if TokenUtil.validate_tokens(access_token, refresh_token):
                        user.logged_in = True
                        user.save()

                        return Response({'access_token': access_token, 'refresh_token': refresh_token}, status=status.HTTP_200_OK)
                    else:
                        return Response({'error': 'Invalid tokens.'}, status=status.HTTP_401_UNAUTHORIZED) 

                else:
                    return Response("Password is incorrect!", status=status.HTTP_400_BAD_REQUEST)
        
        except ObjectDoesNotExist:
            return Response("User does not exist!", status=status.HTTP_404_NOT_FOUND)

class RequestAccessToken(APIView):
    def post(self, request):
        authorization_header = request.META.get("HTTP_AUTHORIZATION")

        if not authorization_header:
            return Response({"error": "Access token is missing."}, status=status.HTTP_401_UNAUTHORIZED)
        
        _, refresh_token = authorization_header.split()
        
        token_key = Token.objects.filter(refresh_token=refresh_token).first()
        
        if not token_key:
            return Response({"error": "refresh token not found please log in again."}, status=status.HTTP_401_UNAUTHORIZED)

        # Validate the refresh token
        refresh_token_payload = TokenUtil.decode_token(refresh_token)
        
        if not refresh_token_payload:
            return Response({'error': 'Invalid refresh token or expired refresh token.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Check if the refresh token is associated with a user (add your logic here)
        user_id = refresh_token_payload.get('id')
        
        if not user_id:
            return Response({'error': 'The refresh token is not associated with a user.'}, status=status.HTTP_404_NOT_FOUND)

        # Generate a new access token
        user = User.objects.get(id=user_id)
        
        access_token = TokenUtil.generate_access_token(user)
        
        if TokenUtil.validate_access_token(access_token):
            return Response({'error': 'Failed to generate access token.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            
            user_token = Token.objects.get(refresh_token=refresh_token)
            user_token.access_token = access_token
            user_token.save()
            
            return Response({'access_token': access_token}, status=status.HTTP_200_OK)
 
class ForgotPassword(APIView):
    def post(self, request):
        try:
            user = User.objects.get(email=request.data['email'], login_type='email')
            
            if user is not None:
                user.password = make_password(request.data['password'])
                
                user_token = Token.objects.get(user_id=user.id)
                
                user_token.delete()
                
            else:
                return Response("User is not registered with google!", status=status.HTTP_400_BAD_REQUEST)
            
        except ObjectDoesNotExist:
            
            return Response("User does not exist!", status=status.HTTP_404_NOT_FOUND)
        
# logout user
class LogoutUser(APIView):
    def post(self,request):
        try:
            
            authorization_header = request.META.get("HTTP_AUTHORIZATION")
                
            if not authorization_header:
                return Response({"error": "Access token is missing."}, status=status.HTTP_401_UNAUTHORIZED)


            _, token = authorization_header.split()
            
            token_key = Token.objects.filter(access_token=token).first()
            
            if not token_key:
                return Response({"error": "Invalid access token."}, status=status.HTTP_401_UNAUTHORIZED)
            

            payload = TokenUtil.decode_token(token_key.access_token)

            # Optionally, you can extract user information or other claims from the payload
            if not payload:
                return Response({"error": "Invalid access token."}, status=status.HTTP_401_UNAUTHORIZED)

            # Check if the refresh token is associated with a user (add your logic here)
            user_id = payload.get('id')
            
            if not user_id:
                return Response({'error': 'The access token is not associated with a user.'}, status=status.HTTP_401_UNAUTHORIZED)
            
            user = User.objects.get(id=user_id) 
                
            if user.logged_in:
                # Blacklist the user's refresh token to invalidate it
                        
                user.logged_in = False
                user.save()
                
                print("User logged out and starting to blacklist token")
                if TokenUtil.is_token_valid(token):
                    TokenUtil.blacklist_token(token)
                    
                    return Response({'message': 'Logout successful.'}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'Invalid access token or expired access token'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response("User is not logged in!", status=status.HTTP_400_BAD_REQUEST)
        
        except ObjectDoesNotExist:
            return Response("User does not exist!", status=status.HTTP_404_NOT_FOUND)