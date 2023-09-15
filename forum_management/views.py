from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import AddForum, Token
from .utils import TokenUtil
from django.http import HttpResponse
from .serializers import ForumSerializer, ForumGetSerializer, ForumDetailsSerializer, ForumImageSerializer
from PIL import Image as PilImage
from io import BytesIO
from users.models import User
from users.serializers import UserGoogleSerializer
from forum_stories.models import UserCountStories
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ObjectDoesNotExist
import random, string, time, jwt, json


class CreateForum(APIView):
    def post(delf,request):
        data = request.data.copy()
        serializer = ForumSerializer(data=request.data)
        if serializer.is_valid():
            image_instance = serializer.save()
                        # Generate and save the thumbnail
                        
            if image_instance.forum_image:
                img = PilImage.open(image_instance.forum_image.path)
                img.thumbnail((100, 100))
                thumb_io = BytesIO()
                img.save(thumb_io, format='JPEG')

                # Generate a unique filename for the thumbnail
                timestamp = int(time.time())
                random_string = ''.join(random.choices(string.ascii_letters, k=6))
                unique_filename = f"{timestamp}_{random_string}_thumbnail.jpg"

                thumbnail = InMemoryUploadedFile(thumb_io, None, unique_filename, 'image/jpeg', None, None)
                image_instance.thumbnail_forum_image.save(unique_filename, thumbnail, save=True)
                
                
                
            email_db = User.objects.filter(email=data['email_id'], login_type='google').first()
            
            forum_user = AddForum.objects.filter(email_id=data['email_id']).first()
            
            if email_db:
                return Response({'error': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
            
            
            user_serializer = UserGoogleSerializer(data={'email': data['email_id'], 'login_type': 'google', 'role': data['forum_role_name'],'image_url': forum_user.image_url, 'thumbnail_url': forum_user.thumbnail_url, 'name': data['display_name']})
            
            if user_serializer.is_valid():
                user_instance = user_serializer.save()
                
                roles = AddForum.objects.values('forum_role_name').distinct()
        
                print(roles)
                
                # Convert the QuerySet to a list of dictionaries
                roles_list = list(roles)

                converted_data = {item['forum_role_name']: 0 for item in roles_list}

                user_count_stories_instance = UserCountStories(user_id=user_instance, count=converted_data)

                # Save the UserCountStories instance to store the JSON data
                user_count_stories_instance.save()
                
                user_stories_count = UserCountStories.objects.all()
                
                if user_stories_count:
                    
                    for record in user_stories_count:
                        record.count = converted_data
                        record.save()
                
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                             
                
            return Response({"message": "Record Added successfully."},status=status.HTTP_200_OK)
        return Response({"message": "Record not Added."},status=status.HTTP_400_BAD_REQUEST)
    
class UpdateForumImage(APIView):
    def put(self, request, pk):
        try:
            ob = AddForum.objects.filter(id=pk).first()
        except AddForum.DoesNotExist:
            return Response({"message": "Record not found."},status=status.HTTP_404_NOT_FOUND)
        
        if ob:
            serializer = ForumImageSerializer(ob, data=request.data)
            
            if serializer.is_valid():
                serializer.save()
                
                if ob.forum_image:
                    img = PilImage.open(ob.forum_image.path)
                    img.thumbnail((100, 100))
                    thumb_io = BytesIO()
                    img.save(thumb_io, format='JPEG')

                    # Generate a unique filename for the thumbnail
                    timestamp = int(time.time())
                    random_string = ''.join(random.choices(string.ascii_letters, k=6))
                    unique_filename = f"{timestamp}_{random_string}_thumbnail.jpg"

                    thumbnail = InMemoryUploadedFile(thumb_io, None, unique_filename, 'image/jpeg', None, None)
                    ob.thumbnail_forum_image.save(unique_filename, thumbnail, save=True)
                    
                
                return Response({"message": "Record Updated successfully."},status=status.HTTP_200_OK)
            
            return Response({"message": "Record not Updated."},status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"message": "Record not Updated."},status=status.HTTP_400_BAD_REQUEST)
        
class AllforumRoles(APIView):
    def get(self,request):
        roles = UserCountStories.objects.values('count').distinct()
        
        # print(roles)
        
        # # Convert the QuerySet to a list of dictionaries
        # roles_list = list(roles)

        # converted_data = {item['forum_role_name']: 0 for item in roles_list}
        
        # print(converted_data)

        # converted_json = json.dumps(converted_data)
        
        # print(converted_json)
        #serializer = ForumDetailsSerializer(roles, many=True)
        return Response(roles[0]['count'])
    
class DeleteForum(APIView):
    def delete(self, request, pk):
        try:
            ob = AddForum.objects.filter(id=pk).first()
            
            forum = User.objects.filter(email=ob.email_id, login_type='google').first()
            
            if forum:
                forum.delete()
                
            if ob.forum_image:
                ob.forum_image.delete()
            
            if ob.thumbnail_forum_image:
                ob.thumbnail_forum_image.delete()
                
            ob.delete()
            
            
            
            return Response({"message": "Record Deleted successfully."},status=status.HTTP_200_OK)
        except AddForum.DoesNotExist:
            return Response({"message": "Record not found."},status=status.HTTP_404_NOT_FOUND)
        
        
class ImageFile(APIView):
    def get(self,request, pk):
        try:
            image_instance = AddForum.objects.get(id=pk)
        except AddForum.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if image_instance.forum_image:
            image_path = image_instance.forum_image.path
            with open(image_path, "rb") as image_file:
                response = HttpResponse(image_file.read(), content_type="image/jpeg")
                response["Content-Disposition"] = f"inline; filename={image_instance.forum_image.name}"
                return response

        return Response(status=status.HTTP_404_NOT_FOUND)


class ThumbnailFile(APIView):
    def get(self,request, pk):
        try:
            image_instance = AddForum.objects.get(id=pk)
        except AddForum.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if image_instance.thumbnail_forum_image:
            thumbnail_path = image_instance.thumbnail_forum_image.path
            with open(thumbnail_path, "rb") as thumbnail_file:
                response = HttpResponse(thumbnail_file.read(), content_type="image/jpeg")
                response["Content-Disposition"] = f"inline; filename={image_instance.thumbnail_forum_image.name}"
                return response

        return Response(status=status.HTTP_404_NOT_FOUND)
    
class GetAllUsers(APIView):
    def get(self,request):
        forums = AddForum.objects.all()
        serializer = ForumGetSerializer(forums, many=True)
        return Response({'all_forums': serializer.data})
    
    
class GetUserById(APIView):
    def get(self,request, pk):
        forums = AddForum.objects.get(id=pk)
        serializer = ForumGetSerializer(forums, many=False)
        return Response(serializer.data)

class UpdateForumdetails(APIView):
    def put(self, request,pk):
        try:
            data = request.data.copy()
            ob = AddForum.objects.filter(id=pk).first()
        except AddForum.DoesNotExist:
            return Response({"message": "Record not found."},status=status.HTTP_404_NOT_FOUND)
        
        if ob:
            forum = User.objects.filter(email= ob.email_id, login_type='google').first()
                
            if forum:
                forum.role = data['forum_role_name']
                forum.email_id = data['email_id']
                forum.name = data['display_name']
                forum.save()
                
            serializer = ForumDetailsSerializer(ob, data=request.data)
            
            if serializer.is_valid():
                serializer.save()
            
            
            return Response({"message": "Record Updated successfully."},status=status.HTTP_200_OK)
        
        return Response({"message": "Record not Updated."},status=status.HTTP_400_BAD_REQUEST)
    
    
    
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

        except (jwt.ExpiredSignatureError, jwt.DecodeError, ValueError, AddForum.DoesNotExist):
            return Response({"error": "Invalid or expired access token."}, status=status.HTTP_401_UNAUTHORIZED)

        # Access token is valid; you can proceed with request processing
        return Response({"message": "Access token is valid."}, status=status.HTTP_200_OK)
        
# login using google auth
class LoginUserGoogle(APIView):
    def post(self,request):
        try:
            user=AddForum.objects.get(email_id=request.data['email'])
            
            if user is not None:
                
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
        
        
class RequestAccessToken(APIView):
    def post(self, request):
        authorization_header = request.META.get("HTTP_AUTHORIZATION")

        if not authorization_header:
            return Response({"error": "Access token is missing."}, status=status.HTTP_401_UNAUTHORIZED)
        
        _, refresh_token = authorization_header.split()
        
        token_key = Token.objects.filter(refresh_token=refresh_token).first()
        
        if not token_key:
            return Response({"error": "Invalid refresh token."}, status=status.HTTP_401_UNAUTHORIZED)

        # Validate the refresh token
        refresh_token_payload = TokenUtil.decode_token(refresh_token)
        
        if not refresh_token_payload:
            return Response({'error': 'Invalid refresh token or expired refresh token.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Check if the refresh token is associated with a user (add your logic here)
        user_id = refresh_token_payload.get('id')
        
        if not user_id:
            return Response({'error': 'The refresh token is not associated with a user.'}, status=status.HTTP_404_NOT_FOUND)

        # Generate a new access token
        user = AddForum.objects.get(id=user_id)
        
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
            
            user = AddForum.objects.get(id=user_id) 
                
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