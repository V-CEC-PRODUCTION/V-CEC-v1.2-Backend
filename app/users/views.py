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
from .serializers import UserSerializer,UserImageSerializer, EmailSerializer, OtpSerializer, UserGoogleSerializer,GetUserDetailsSerializer,UserSerializerToken
from datetime import datetime, timedelta
from celery import shared_task
from .utils import TokenUtil
from io import BytesIO
from PIL import Image as PilImage
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.files.uploadedfile import InMemoryUploadedFile
import random,time, string, os, jwt
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.core.cache import cache
from azure.storage.blob import BlobServiceClient, ContentSettings

connection_string = f"DefaultEndpointsProtocol=https;AccountName={os.getenv('AZURE_STORAGE_ACCOUNT_NAME')};AccountKey={os.getenv('AZURE_ACCOUNT_KEY')};EndpointSuffix=core.windows.net"

blob_service_client = BlobServiceClient.from_connection_string(connection_string)

def generate_token(user_id, email):
    # Set the expiration time for the token (e.g., 1 hour from now)
    expiration_time = datetime.utcnow() + timedelta(minutes=5)
    
    # Create the payload dictionary
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': expiration_time  # Expiration time
    }
    
    # Replace 'your_secret_key' with your own secret key
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token

class ForgotPassword(APIView):
    def post(self,request):
       
        email = request.data.get('email')
        
        try:
            user = User.objects.get(email=email, login_type='email')
        except User.DoesNotExist:
            user = None

        if user is not None:
            token = generate_token(user.id, email)
            
            reset_link = f"http://{request.get_host()}/users/auth/reset/password/{token}/"
            
            subject = 'Password Reset Mail for VCEC'

            from_email = 'proddecapp@gmail.com'
            
            receipient = [email]
            html_message = render_to_string('reset_mail.html', {'reset_link': reset_link})

            # Send the email with HTML content
            send_mail(subject, '', from_email, receipient, html_message=html_message)

            return Response({'message': 'Password reset mail sent successfully'}, status=status.HTTP_200_OK)
        else:

            return Response({'message': 'No user with that email address found.'}, status=status.HTTP_404_NOT_FOUND)
        
class ResetPassword(APIView):
    def get(self, request, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            expiration_time = datetime.utcfromtimestamp(payload['exp'])
            current_time = datetime.utcnow()

            if current_time <= expiration_time:
                return render(request, 'password_change.html', {'validlink': True, 'user_id': payload['user_id']})
            else:
                return render(request, 'password_change.html', {'validlink': False})
        except jwt.ExpiredSignatureError:
            return HttpResponseBadRequest('Password reset link has expired.')
        except jwt.InvalidTokenError:
            return HttpResponseBadRequest('Invalid password reset link.')
        
        
class ResetPasswordSubmit(APIView):
    def get(self, request):
        user_id = request.GET['user_id']
        password = request.GET['password']
        confirm_password = request.GET['confirm_password']
        
        try:
            
            if password == confirm_password:
                admin_instance = User.objects.get(id=user_id)
                
                admin_instance.password = make_password(password)
                
                admin_instance.save()
                
                return render(request, 'password_change_success.html')
            
            else:
                return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
 
@api_view(['POST'])
@shared_task
def send_otp(request):
    try:
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid():
            user_email = serializer.validated_data['email']
            
            email_db = User.objects.filter(email=user_email, login_type='email').first()
            
            if email_db:
                return Response({'error': 'Email already exists.'}, status=status.HTTP_409_CONFLICT)
            
            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])

            subject = 'Your OTP'
            
            from_email = 'proddecapp@gmail.com'
            
            html_message = render_to_string('otp_mail.html', {'otp': otp})

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
    
    except Exception as e:
        return Response({"detail": "An error occurred while processing your request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ImageFile(APIView):
    def get(self,request, pk):
        try:
            image_instance = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if image_instance.profile_image:
            image_path = image_instance.profile_image.path
            with open(image_path, "rb") as image_file:
                response = HttpResponse(image_file.read(), content_type="image/jpeg")
                response["Content-Disposition"] = f"inline; filename={image_instance.profile_image.name}"
                return response

        return Response(status=status.HTTP_404_NOT_FOUND)


class ThumbnailFile(APIView):
    def get(self,request, pk):
        try:
            image_instance = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if image_instance.thumbnail_profile_image:
            thumbnail_path = image_instance.thumbnail_profile_image.path
            with open(thumbnail_path, "rb") as thumbnail_file:
                response = HttpResponse(thumbnail_file.read(), content_type="image/jpeg")
                response["Content-Disposition"] = f"inline; filename={image_instance.thumbnail_profile_image.name}"
                return response

        return Response(status=status.HTTP_404_NOT_FOUND)


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
                return Response({'error': 'Email already exists.'}, status=status.HTTP_409_CONFLICT)
            
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

class UpdateProfilePhotoUser(APIView):
    def put(self, request):
        try:
            authorization_header = request.META.get("HTTP_AUTHORIZATION")

            if not authorization_header:
                return Response({"error": "Access token is missing."}, status=status.HTTP_401_UNAUTHORIZED)
            
            _, access_token = authorization_header.split()
            
            token_key = Token.objects.filter(access_token=access_token).first()
            
            if not token_key:
                return Response({"error": "Access token not found please log in again."}, status=status.HTTP_401_UNAUTHORIZED)

            # Validate the refresh token
            access_token_payload = TokenUtil.decode_token(token_key.refresh_token)
            
            if not access_token_payload:
                return Response({'error': 'Invalid refresh token or expired refresh token.'}, status=status.HTTP_401_UNAUTHORIZED)

            # Check if the refresh token is associated with a user (add your logic here)
            user_id = access_token_payload.get('id')
            
            if not user_id:
                return Response({'error': 'The refresh token is not associated with a user.'}, status=status.HTTP_404_NOT_FOUND)
            
            user = User.objects.get(id=user_id)
            
            try:
                blob_service_client.delete_blob('media', f"{user.profile_image.name}")
                
            except Exception as e:
                print(f"An error occurred: {e}")
                
            try:
                blob_service_client.delete_blob('media', f"{user.thumbnail_profile_image.name}")
                
            except Exception as e:
                print(f"An error occurred: {e}")
                    
            if user.profile_image:
                user.profile_image.delete()
            if user.thumbnail_profile_image:
                user.thumbnail_profile_image.delete()
            
            serializer = UserImageSerializer(instance=user,data=request.data)
            
            print(user.id)
            # Generate and save the thumbnail
            if serializer.is_valid():
                image_instance = serializer.save()
                
                if image_instance.profile_image:
                    img = PilImage.open(BytesIO(image_instance.profile_image.read()))
                    img.thumbnail((100, 100))
                    thumb_io = BytesIO()
                    img.save(thumb_io, format='JPEG')
                    thumb_io.seek(0)

                    # Generate a unique filename for the thumbnail
                    timestamp = int(time.time())
                    random_string = ''.join(random.choices(string.ascii_letters, k=6))
                    unique_filename = f"{timestamp}_{random_string}_thumbnail.jpg"

                    folder_name = "thumbnails"
                    
                    blob_media_name = f"users/{folder_name}/{unique_filename}"
                
                    blob_client = blob_service_client.get_blob_client(container="media", blob=blob_media_name)
                    blob_client.upload_blob(thumb_io, content_settings=ContentSettings(content_type='image/jpeg'))

                    image_instance.thumbnail = blob_media_name
                    image_instance.save()
                    
                    event_cache_name = "forum_events*"
        
                    cache.delete_pattern(event_cache_name)
                    
                    announcement_cache_name = "forum_announcements*"
                    
                    cache.delete_pattern(announcement_cache_name)
                    
                    return Response({"result": "successfully updated profile image"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Profile photo is missing."}, status=status.HTTP_400_BAD_REQUEST)  
        except Exception as e:
            print(e)
            return Response({"detail": "An error occurred while processing your request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def delete_file(file_path):
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"Error deleting file: {e}")

# update user
class UpdateUser(APIView):
    def put(self,request):
        authorization_header = request.META.get("HTTP_AUTHORIZATION")

        if not authorization_header:
            return Response({"error": "Access token is missing."}, status=status.HTTP_401_UNAUTHORIZED)
        
        _, access_token = authorization_header.split()
        
        token_key = Token.objects.filter(access_token=access_token).first()
        
        if not token_key:
            return Response({"error": "Access token not found please log in again."}, status=status.HTTP_401_UNAUTHORIZED)

        # Validate the refresh token
        access_token_payload = TokenUtil.decode_token(token_key.refresh_token)
        
        if not access_token_payload:
            return Response({'error': 'Invalid refresh token or expired refresh token.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Check if the refresh token is associated with a user (add your logic here)
        user_id = access_token_payload.get('id')
        
        if not user_id:
            return Response({'error': 'The refresh token is not associated with a user.'}, status=status.HTTP_404_NOT_FOUND)
        
        user = User.objects.get(id=user_id)
        if request.data.get('name'):
            user.name = request.data.get('name')
        if request.data.get('email'):
            user.email = request.data.get('email')
        if request.data.get('admission_no'):
            user.admission_no = request.data.get('admission_no')
        if request.data.get('register_no'):
            user.register_no = request.data.get('register_no') 
        if request.data.get('ieee_membership_no'):
            user.ieee_membership_no = request.data.get('ieee_membership_no')
        if request.data.get('branch'):
            user.branch = request.data.get('branch')
        if request.data.get('semester'):
            user.semester = request.data.get('semester')
        if request.data.get('division'):
            user.division = request.data.get('division')

        user.save() 
        print(user.admission_no, request.data.get('admission_no'))
        serializer = UserSerializer(instance=user)
        
        event_cache_name = "forum_events*"

        cache.delete_pattern(event_cache_name)
        
        announcement_cache_name = "forum_announcements*"
        
        cache.delete_pattern(announcement_cache_name)
            
        return Response({"result":serializer.data}, status = status.HTTP_200_OK)


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
            print(e)
            return Response(f"Missing key: {str(e)}", status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as e:
            print(e)
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(e)
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
                
                if user.role == 'guest':
                    user.name = request.data['name']
                    user.device_id = request.data['device_id']
                    user.logged_in = True
                
                elif user.role == 'student':
                
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
            
            print(user.email)
            if user is not None:
                
                
                if user.device_id is not None:
                    
                    try:
                        user_token = Token.objects.get(user_id=user.id)
                        
                        user_token.delete()
                    except Exception as e:
                        print(e)
                        pass
                    
                
                
                access_token, refresh_token = TokenUtil.generate_tokens(user)
                
                # Validate tokens
                if TokenUtil.validate_tokens(access_token, refresh_token):
                    
                    return Response({'access_token': access_token, 'refresh_token': refresh_token}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid tokens.'}, status=status.HTTP_401_UNAUTHORIZED) 


            else:
                return Response("User is not registered with google!", status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            print(e)
            return Response("User does not exist!", status=status.HTTP_404_NOT_FOUND)
    
# login user
class LoginUser(APIView):
    def post(self,request):
        try:
            print(request.data['email'])
            user = User.objects.get(email=request.data['email'], login_type='email')
            print(user)
            
            if user is not None:

                try:
                    user_token = Token.objects.get(user_id=user.id)
                    user_token.delete()
                except Token.DoesNotExist:
                    pass
                

                if check_password(request.data['password'], user.password):
                    # Generate refresh and access tokens
                    access_token, refresh_token = TokenUtil.generate_tokens(user)
                    

                    return Response({'access_token': access_token, 'refresh_token': refresh_token}, status=status.HTTP_200_OK)

                else:
                    return Response("Password is incorrect!", status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            print(e)
            return Response("User does not exist!", status=status.HTTP_404_NOT_FOUND)

class CheckEmailExist(APIView): 
    def post(self,request):
        try:
            user = User.objects.get(email=request.data['email'], login_type=request.data['login_type'])
            
            if user is not None:
                return Response("Email already exists!", status=status.HTTP_409_CONFLICT)
            else:
                return Response("Email does not exist!", status=status.HTTP_404_NOT_FOUND)
        
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
                     
            print("User logged out and starting to blacklist token")
            if TokenUtil.is_token_valid(token):
                TokenUtil.blacklist_token(token)
                
                return Response({'message': 'Logout successful.'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Invalid access token or expired access token'}, status=status.HTTP_401_UNAUTHORIZED)

        except ObjectDoesNotExist:
            return Response("User does not exist!", status=status.HTTP_404_NOT_FOUND)


class GetUserDetails(APIView):
    def get(self, request):
        authorization_header = request.META.get("HTTP_AUTHORIZATION")

        if not authorization_header:
            return Response({"error": "Access token is missing."}, status=status.HTTP_401_UNAUTHORIZED)
        
        _, access_token = authorization_header.split()
        
        token_key = Token.objects.filter(access_token=access_token).first()
        
        if not token_key:
            return Response({"error": "Access token not found please log in again."}, status=status.HTTP_401_UNAUTHORIZED)

        # Validate the refresh token
        access_token_payload = TokenUtil.decode_token(token_key.refresh_token)
        
        if not access_token_payload:
            return Response({'error': 'Invalid refresh token or expired refresh token.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Check if the refresh token is associated with a user (add your logic here)
        user_id = access_token_payload.get('id')
        
        if not user_id:
            return Response({'error': 'The refresh token is not associated with a user.'}, status=status.HTTP_404_NOT_FOUND)

        # Generate a new access token
        user = User.objects.get(id=user_id)
        
        serializer = GetUserDetailsSerializer(user)
        
        if user and user.role == 'student':

            
            pass
        return Response(serializer.data)
