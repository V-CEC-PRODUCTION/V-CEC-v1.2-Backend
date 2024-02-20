import time,random ,string
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse 
from .serializers import FormGetSerializer, FormSerializer
from PIL import Image as PilImage
from io import BytesIO
from rest_framework import status
from django.core.files.uploadedfile import InMemoryUploadedFile
from .models import create_dynamic_model,forumAnnouncements
from django.db import connection
# Create your views here.
import json
from vcec_bk.pagination import CustomPageNumberPagination
from django.core.cache import cache
from users.utils import Token, TokenUtil
from users.models import User
from forum_management.models import AddForum

@api_view(['POST'])
def create_announcement(request):
    serializer=FormSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer_instance=serializer.save()
        if not (serializer_instance.button_name and serializer_instance.button_link):
            serializer_instance.button_name=''
            serializer_instance.button_link=''
        serializer_instance.save()
            

        img = PilImage.open(serializer_instance.poster_image.path)
        img.thumbnail((100, 100))
        thumb_io = BytesIO()
        img.save(thumb_io, format='JPEG')

        # Generate a unique filename for the thumbnail
        timestamp = int(time.time())
        random_string = ''.join(random.choices(string.ascii_letters, k=6))
        unique_filename = f"{timestamp}_{random_string}_thumbnail.jpg"

        thumbnail = InMemoryUploadedFile(thumb_io, None, unique_filename, 'image/jpeg', None, None)
        serializer_instance.thumbnail_poster_image.save(unique_filename, thumbnail, save=True)
        
        model_name ="forum_announcements" + '_'+str(serializer_instance.id)+'_likes'
        
        announcement_cache_name = "forum_announcements*"
        
        cache.delete_pattern(announcement_cache_name)
        
        if create_dynamic_model(model_name,serializer_instance.id):
            return Response(serializer.data,status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

class GetLikesAnnouncementInd(APIView):
    def get(self,request):
        try:
            announcement_id = request.query_params.get('announcement_id')
            model_name = "forum_announcements_forum_announcements" + '_' + str(announcement_id) + '_likes'
            cursor = connection.cursor()
            cursor.execute(f"SELECT name, user_id FROM {model_name} WHERE is_liked=true")
            count_likes = cursor.fetchall()
            
            all_likes = []
            for like in count_likes:
                user_instance = User.objects.get(id=like[1])
                all_likes.append({"name": user_instance.name, "image_url": user_instance.image_url})
            cursor.close()
            
            return Response({"event_likes": all_likes}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response( f"An error occurred: {str(e)}")
@api_view(['PUT'])
def update_announcement(request,id):

    serializer=FormSerializer(data=request.data)
    cur=connection.cursor()    
    
    if serializer.is_valid():
        if request.data.get('content'):
            cur.execute(f"UPDATE forum_announcements_forumannouncements SET content='{serializer.data['content']}' WHERE id={id}")
       
        if request.data.get("title"):
            cur.execute(f"UPDATE forum_announcements_forumannouncements SET title='{serializer.data['title']}' WHERE id={id}")
         
        if request.data.get('whatsapp_link'):
            cur.execute(f"UPDATE forum_announcements_forumannouncements SET whatsapp_link='{serializer.data['whatsapp_link']}' WHERE id={id}")
        if request.data.get('button_link'):
            cur.execute(f"UPDATE forum_announcements_forumannouncements SET button_link='{serializer.data['button_link']}' WHERE id={id}")
        if request.data.get('button_name'):
            cur.execute(f"UPDATE forum_announcements_forumannouncements SET button_name='{serializer.data['button_name']}' WHERE id={id}")

        cur.close()

        announcement_cache_name = "forum_announcements*"
        
        cache.delete_pattern(announcement_cache_name)
        

        return Response({"message": "Record Updated successfully."},status=status.HTTP_200_OK)

    else:
        cur.close()
        connection.close()
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def delete_announcement(request,pk):

    try:
        ob = forumAnnouncements.objects.get(pk=pk)
        
    except ob.DoesNotExist:
        return Response({"error": "Image not found."}, status=404)
    
    if ob.poster_image:
        ob.poster_image.delete()
    if ob.thumbnail_poster_image:
        ob.thumbnail_poster_image.delete()
    
    model_name ="forum_announcements_forum_announcements" + '_'+str(ob.id)+'_likes'

    try:
        cursor= connection.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {model_name}")

        announcement_cache_name = "forum_announcements*"
        
        cache.delete_pattern(announcement_cache_name)
    except forumAnnouncements.DoesNotExist:
        return Response( "Event not found.")
    except Exception as e:
        return Response( f"An error occurred: {str(e)}")


    ob.delete()
    connection.close()
    return Response({"status":"Event deleted successfully"},status=status.HTTP_200_OK)

@api_view(['GET'])
def image_file(request, pk):
    try:
        image_instance = forumAnnouncements.objects.get(id=pk)
    except forumAnnouncements.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if image_instance.poster_image:
        image_path = image_instance.poster_image.path
        with open(image_path, "rb") as image_file:
            response = HttpResponse(image_file.read(), content_type="image/jpeg")
            response["Content-Disposition"] = f"inline; filename={image_instance.poster_image.name}"
            return response

    return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def thumbnail_file(request, pk):
    try:
        image_instance = forumAnnouncements.objects.get(id=pk)
    except forumAnnouncements.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if image_instance.thumbnail_poster_image:
        thumbnail_path = image_instance.thumbnail_poster_image.path
        with open(thumbnail_path, "rb") as thumbnail_file:
            response = HttpResponse(thumbnail_file.read(), content_type="image/jpeg")
            response["Content-Disposition"] = f"inline; filename={image_instance.thumbnail_poster_image.name}"
            return response

    return Response(status=status.HTTP_404_NOT_FOUND)

class GetAllAnnouncementsClientSide(APIView, CustomPageNumberPagination):
    def get(self,request):
        try:
            page_number = request.query_params.get('page')
            page_count = request.query_params.get('page_count')
            forum = request.query_params.get('forum')
                
            if page_number is None:
                page_number = 1
                
            if page_count is None:
                page_count = 1000
                

            announcements_result_name = f"forum_announcements_{page_number}_{page_count}"
            # announcements_cache_result = cache.get(announcements_result_name)
            
            announcements_cache_result = None
            
            if announcements_cache_result is None:
                
                if forum == "all":
                    
                    announcements = forumAnnouncements.objects.all().order_by('-publish_date')
                    
                elif forum != "all":
                    announcements = forumAnnouncements.objects.filter(published_by__contains=forum).order_by('-publish_date')
                    
                self.paginate_queryset(announcements, request)
                serializer = FormGetSerializer(announcements, many=True)
                
                announcement_data = serializer.data
                
                for announcement in announcement_data:
                    likes_table = "forum_announcements_forum_announcements" + '_' + str(announcement['id']) + '_likes'
                    
                    cursor = connection.cursor()
                        
                    cursor.execute(f"SELECT user_id FROM {likes_table} WHERE is_liked=true ORDER BY id DESC LIMIT 3")
                    
                    user_ids = cursor.fetchall()
                    
                    print(user_ids)
                    announcement['liked_by'] = []
                    for user_id in user_ids:
                        
                        user_instance = User.objects.get(id=user_id[0])
                        announcement['liked_by'].append(user_instance.image_url)
                    
                    cursor.execute(f"SELECT COUNT(*) FROM {likes_table} WHERE is_liked=true")
                    
                    total_likes = cursor.fetchone()[0]
                    
                
                    announcement['total_likes'] = total_likes
                
                        
                    cursor.close()
                        
                for announcement_serialized in serializer.data:

                    if 'liked_by' not in announcement_serialized:
                        announcement_serialized['liked_by'] = []
                        
                    if 'total_likes' not in announcement_serialized:
                        announcement_serialized['total_likes'] = 0
                        
                cache.set(announcements_result_name, json.dumps(announcement_data),timeout=60*60*24*7)
                
                return Response({"annoucements":serializer.data}, status=status.HTTP_200_OK)
            else:
                print("Data from cache")
                announcements_cache_result = json.loads(announcements_cache_result)
                return Response({"events":announcements_cache_result}, status=status.HTTP_200_OK)
        except forumAnnouncements.DoesNotExist:
            return Response({"status": "Records not found"}, status=status.HTTP_404_NOT_FOUND)

class LikeEvent(APIView):
    def post(self,request):
        try:
            announcement_id = request.query_params.get('announcement_id')
            like_status = request.query_params.get('like_status')
            
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
            
            user_id = str(user_id)
           
            model_name ="forum_announcements_forum_announcements" + '_'+str(announcement_id)+'_likes'
            cursor= connection.cursor()
            cursor.execute(f"UPDATE {model_name} SET is_liked=%s WHERE user_id=%s", [like_status , user_id])
            cursor.close()
            
            announcement_cache_name = "forum_announcements*"
        
            cache.delete_pattern(announcement_cache_name)    
                    
            return Response({"message": "Likes record added successfully."}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response( f"An error occurred: {str(e)}")
        
class SetView(APIView):
    def post(self, request):
       
        try:
            announcement_id = request.query_params.get('announcement_id')
            
            announcement_instance = forumAnnouncements.objects.get(id=announcement_id)
            
            if announcement_instance is None:
                return Response({"error": "Event not found."}, status=status.HTTP_404_NOT_FOUND)
            
            
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
                return Response({'error': 'Invalid refresh token or expired refresh token.'}, status=status.HTTP_401_UNAUTHORIZED)

            user_instance = User.objects.get(id=user_id)
            
            model_name = "forum_announcements_forum_announcements" + '_' + str(announcement_id) + '_likes'
            
            print(model_name)
            
            user_id = str(user_id)
            
            cursor = connection.cursor()
            
            cursor.execute(f"INSERT INTO {model_name} (user_id,name,event_id,is_liked,views) VALUES ({user_id},'{user_instance.name}',{announcement_id},false,true) ON CONFLICT (user_id) DO NOTHING;")
            cursor.close()
            
            announcement_cache_name = "forum_announcements*"
        
            cache.delete_pattern(announcement_cache_name)
            
            return Response({"message": "Views record added successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            print(str(e))
            return Response(f"An error occurred: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class GetAnnoucement(APIView):
    def get(self,request,id):
        try:
            model_name ="forum_announcements_forum_announcements" + '_'+str(id)+'_likes'
            
            announcement = forumAnnouncements.objects.get(id=id)
            
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
                    return Response({'error': 'Invalid refresh token or expired refresh token.'}, status=status.HTTP_401_UNAUTHORIZED)

            except Exception as e:
                print(str(e))
                return Response({"error": "An error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            forums_divided = announcement.published_by.split(',')
            
            print(forums_divided)
            forum_image_url = []
            
            for forum in forums_divided:
                forum_instance = AddForum.objects.get(forum_role_name=forum)
                forum_image_url.append({"image_url": forum_instance.image_url})
            
            cursor= connection.cursor()
            
            cursor.execute(f"SELECT COUNT(*) FROM {model_name} WHERE is_liked=true")
            
            count_likes = cursor.fetchone()[0]
            
            user_id = str(user_id)
            
            cursor.execute(f"SELECT is_liked FROM {model_name} WHERE user_id=%s", [user_id])
            
            fetch_result = cursor.fetchone()
            if fetch_result is None:
                is_liked = False
            else:
                is_liked = fetch_result[0]
            serializer = FormGetSerializer(announcement)

            return Response({"announcement_result": serializer.data, "total_likes": count_likes, "conducted_by": forum_image_url, "is_liked": is_liked}, status=status.HTTP_200_OK)
        except forumAnnouncements.DoesNotExist:
            return Response({"status": "Records not found"}, status=status.HTTP_404_NOT_FOUND)
    