from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ForumStories, UserCountStories
from forum_management.models import AddForum    
from .serializers import ForumStoriesSerializer, ForumStoriesGetSerializer
from users.models import User, Token
from users.utils import TokenUtil
from PIL import Image as PilImage
import time, random, string, json, os
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpResponse
from datetime import datetime, timedelta
from django.http import FileResponse
from django.utils import timezone
class AddForumStories(APIView):
    def post(self,request):
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
        
        
        if user.role == 'student' or user.role == 'guest':
            return Response({'error': 'User not allowed to add stories.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        #data = request.data.copy()
        
        media_file = request.FILES.get('media_file')
        content = request.data.get('content')
        
        forum = AddForum.objects.filter(forum_role_name=user.role).first()

        if not media_file:
            return Response({"error": "No media file found"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        if media_file.content_type.startswith('image'):
            # Handle image uploads
            media_item = ForumStoriesSerializer(data={'content': content, 'forum_tag': user.role, 'file_tag': 'img', 'forum_id': forum.id, 'media_file': media_file})

            if media_item.is_valid():
                media_instance = media_item.save()

                # Generate and save the thumbnail
                img = PilImage.open(media_file)
                img.thumbnail((100, 100))
                thumb_io = BytesIO()
                img.save(thumb_io, format='JPEG')

                # Generate a unique filename for the thumbnail
                timestamp = int(time.time())
                random_string = ''.join(random.choices(string.ascii_letters, k=6))
                unique_filename = f"{timestamp}_{random_string}_thumbnail.jpg"

                thumbnail = InMemoryUploadedFile(thumb_io, None, unique_filename, 'image/jpeg', None, None)
                media_instance.thumbnail_media_file.save(unique_filename, thumbnail, save=True)

        elif media_file.content_type.startswith('video'):
            # Handle video uploads
            video_item = ForumStoriesSerializer(data={'content': content, 'forum_tag': user.role, 'file_tag': 'vid', 'forum_id': forum.id, 'media_file': media_file})

            if video_item.is_valid():
                media_instance = video_item.save()

                # Set the media_url for videos
                media_instance.media_url = f"forum/stories/video/media/{media_instance.id}/file/"
                
                
                media_instance.save()

        # Update user's story count (your existing code)
        user_stories_count = UserCountStories.objects.all()

        if user_stories_count:
            for record in user_stories_count:
                count_data = record.count
                count_data = json.loads(count_data)
                count_data[user.role] += 1
                record.count = json.dumps(count_data)
                record.save()

        return Response({"message": "Stories added successfully"}, status=status.HTTP_201_CREATED)
    
class DeleteForumStories(APIView):
    def delete(self, request, pk):
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
        
        
        if user.role == 'student' or user.role == 'guest':
            return Response({'error': 'User not allowed to delete stories.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            story = ForumStories.objects.get(id=pk)
        except ForumStories.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if story.forum_tag != user.role:
            return Response({'error': 'User not allowed to delete this story.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if story.media_file:
            story.media_file.delete()
            
        if story.thumbnail_media_file:
            story.thumbnail_media_file.delete()
            
        story.delete()
        
        
        user_stories_count = UserCountStories.objects.all()

        if user_stories_count:
            for record in user_stories_count:
                count_data = record.count
                count_data = json.loads(count_data)
                
                if count_data[user.role] == 0:
                    continue
                else:
                    count_data[user.role] -= 1
                record.count = json.dumps(count_data)
                record.save()
        
        return Response({"message": "Story deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class SeeStories(APIView):
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
        
        user = UserCountStories.objects.get(user_id=user_id) 
        
        if not user:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        
        forum_tag = request.data.get('forum_tag')
        
        if not forum_tag:
            return Response({'error': 'Forum tag is missing.'}, status=status.HTTP_400_BAD_REQUEST)
        
      
        count_data = json.loads(user.count)
        
        if forum_tag in count_data:
            
            
            if count_data[forum_tag] == 0:
                pass
            else:
                count_data[forum_tag] -= 1
                
            user.count = json.dumps(count_data)
            user.save()
            
            return Response({"message": "Story marked as seen"}, status=status.HTTP_200_OK)
            
        else:
            return Response({'error': 'Forum tag not found.'}, status=status.HTTP_404_NOT_FOUND)
        


class StreamVideo(APIView):
    def get(self,request, pk):
        try:
            video_instance = ForumStories.objects.get(id=pk)
            video_path = video_instance.media_file.path
        except ForumStories.DoesNotExist:
            return HttpResponse(status=404)  # Video not found
        
        # Open the video file in binary mode
        video_file = open(video_path, 'rb')

        # Create a FileResponse instance for streaming
        response = FileResponse(video_file, content_type='video/mp4')
        
        # Set the Content-Disposition header to inline to show video in the browser
        response['Content-Disposition'] = f'inline; filename="{os.path.basename(video_path)}"'
        
        return response
class ImageFile(APIView):
    def get(self,request, pk):
        try:
            image_instance = ForumStories.objects.get(id=pk)
        except AddForum.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if image_instance.media_file:
            image_path = image_instance.media_file.path
            with open(image_path, "rb") as image_file:
                response = HttpResponse(image_file.read(), content_type="image/jpeg")
                response["Content-Disposition"] = f"inline; filename={image_instance.media_file.name}"
                return response

        return Response(status=status.HTTP_404_NOT_FOUND)


class ThumbnailFile(APIView):
    def get(self,request, pk):
        try:
            image_instance = ForumStories.objects.get(id=pk)
        except AddForum.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if image_instance.thumbnail_media_file:
            thumbnail_path = image_instance.thumbnail_media_file.path
            with open(thumbnail_path, "rb") as thumbnail_file:
                response = HttpResponse(thumbnail_file.read(), content_type="image/jpeg")
                response["Content-Disposition"] = f"inline; filename={image_instance.thumbnail_media_file.name}"
                return response

        return Response(status=status.HTTP_404_NOT_FOUND)
    
class GetForumStories(APIView):
    def get(self, request):
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
        
        
        forum_stories = ForumStories.objects.all().order_by('-upload_time')

        # Group forum_stories by forum_tag
        grouped_stories = {}
        for story in forum_stories:
            forum_tag = story.forum_tag
            image_url = User.objects.get(role=forum_tag).image_url
            display_name = User.objects.get(role=forum_tag).name
            thumbnail_url = User.objects.get(role=forum_tag).thumbnail_url
            if forum_tag not in grouped_stories:
                grouped_stories[forum_tag] = {
                    "forum_tag": forum_tag,
                    "forum_image_url": image_url,  # Add your logic to get the image URL
                    "forum_thumbnail_url": thumbnail_url,  # Add your logic to get the thumbnail URL
                    "display_name": display_name,  # Add your logic to get the display name
                    "stories": [],
                }
            grouped_stories[forum_tag]["stories"].append({
                "content": story.content,
                "media_url": story.media_url,
                "thumbnail_url": story.thumbnail_media_url,
                "file_tag": story.file_tag,
                "upload_time": story.upload_time,
            })

        for forum_data in grouped_stories.values():
            forum_data["stories"].sort(key=lambda x: x["upload_time"])  # Assuming "id" is the story's ID field

        response_data = {"forum_stories": list(grouped_stories.values())}

        return Response(response_data, status=status.HTTP_200_OK)




                
                

                    
                
                