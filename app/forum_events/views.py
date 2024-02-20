from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.http import HttpResponse 
from PIL import Image as PilImage
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from .serializers import FormSerializer,FormGetSerializer
import time,random ,string
from .models import create_tables,forumEvents,create_dynamic_models
from django.db import connection
from django.core.cache import cache
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from vcec_bk.pagination import CustomPageNumberPagination
import json
from users.models import User, Token
from users.utils import TokenUtil
from forum_management.models import AddForum
class EventForumView(APIView):
    def get(self,request):
        try:
            events=forumEvents.objects.all().order_by('-publish_date')
            serializer=FormGetSerializer(events,many=True)
            return Response({"events":serializer.data},status=status.HTTP_200_OK)
        except forumEvents.DoesNotExist:
            return Response({"error":"Events not found"},status=status.HTTP_404_NOT_FOUND)
        
@api_view(['POST'])
def create_event(request):
    if request.data["register_button_link"]=='':
        request.data["register_button_link"]='vcec_form'
        
    serializer=FormSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer_instance=serializer.save()

        img = PilImage.open(serializer_instance.poster_image.path)
        img.thumbnail((100, 100))
        thumb_io = BytesIO()
        img.save(thumb_io, format='JPEG')

        # Generate a unique filename for the thumbnail
        timestamp = int(time.time())
        random_string = ''.join(random.choices(string.ascii_letters, k=6))
        unique_filename = f"{timestamp}_{random_string}_thumbnail.jpg"
        # serializer_instance.hashtags=extract_unique_meaningful_words(serializer_instance.content)
        serializer_instance.save()

        thumbnail = InMemoryUploadedFile(thumb_io, None, unique_filename, 'image/jpeg', None, None)
        serializer_instance.thumbnail_poster_image.save(unique_filename, thumbnail, save=True)
        create_tables("forum_events",serializer_instance.id)
        
        event_cache_name = "forum_events*"
        
        cache.delete_pattern(event_cache_name)
        
        return Response(serializer.data,status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

class GetLikesEventInd(APIView):
    def get(self,request):
        try:
            event_id = request.query_params.get('event_id')
            model_name = "forum_events_forum_events" + '_' + str(event_id) + '_likes'
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
class get_events(APIView,CustomPageNumberPagination):
    def get(self,request):
        try:
            page_number = request.query_params.get('page')
            page_count = request.query_params.get('page_count')
            forum = request.query_params.get('forum')
                
            if page_number is None:
                page_number = 1
                
            if page_count is None:
                page_count = 1000
                
            status_event = request.query_params.get('status')
               
            event_result_name = f"forum_events_{page_number}_{page_count}_{status_event}"
            # event_cache_result = cache.get(event_result_name)
            
            event_cache_result = None
            
            if event_cache_result is None:
            
                if (status_event == 'Upcoming' or status_event == 'Ended') and forum == 'all':
                    events = forumEvents.objects.filter(status=status_event).order_by('-publish_date')
                elif (status_event == 'Upcoming' or status_event == 'Ended') and forum != 'all':
                    events = forumEvents.objects.filter(status=status_event, published_by__contains=forum).order_by('-publish_date')
                else:
                    return Response({"status": "Invalid status value"}, status=status.HTTP_400_BAD_REQUEST)
                  
                events_result = self.paginate_queryset(events, request)
                serializer = FormGetSerializer(events_result, many=True)
                
                event_data = serializer.data
                
                for event in event_data:
                    likes_table = "forum_events_forum_events" + '_' + str(event['id']) + '_likes'
                    
                    if event['register_button_link'] == "vcec_form":
                        register_table = "forum_events_forum_events" + '_' + str(event['id']) + '_registration'
                        
                        cursor = connection.cursor()
                        
                        cursor.execute(f"SELECT COUNT(*) FROM {register_table}")
                        
                        total_registrations = cursor.fetchone()[0]
                        
                        if total_registrations is not None:
                            print(total_registrations)
                            if total_registrations >= 1:
                                event['total_registrations'] = total_registrations
                        else:
                            event['total_registrations'] = 0
                        
                        cursor.execute(f"SELECT user_id FROM {likes_table} WHERE is_liked=true ORDER BY id DESC LIMIT 3")
                        
                        user_ids = cursor.fetchall()
                        
                        print(user_ids)
                        event['liked_by'] = []
                        for user_id in user_ids:
                           
                            user_instance = User.objects.get(id=user_id[0])
                            event['liked_by'].append(user_instance.image_url)
                        
                        cursor.execute(f"SELECT COUNT(*) FROM {likes_table} WHERE is_liked=true")
                        
                        total_likes = cursor.fetchone()[0]
                        
                   
                        event['total_likes'] = total_likes
                 
                            
                        cursor.close()
                        
                for event_serialized in serializer.data:
                    if 'total_registrations' not in event_serialized:
                        event_serialized['total_registrations'] = 0
                    if 'liked_by' not in event_serialized:
                        event_serialized['liked_by'] = []
                        
                    if 'total_likes' not in event_serialized:
                        event_serialized['total_likes'] = 0
                        
                cache.set(event_result_name, json.dumps(event_data),timeout=60*60*24*7)
                
                return Response({"events":event_data}, status=status.HTTP_200_OK)
            else:
                print("Data from cache")
                event_cache_result = json.loads(event_cache_result)
                return Response({"events":event_cache_result}, status=status.HTTP_200_OK)
        except forumEvents.DoesNotExist:
            return Response({"status": "Forms not found"}, status=status.HTTP_404_NOT_FOUND)

class StudentRegisterEvent(APIView):
    def post(self, request):
        try:
            event_id = request.query_params.get('event_id')
            
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
        
        try:
            user_instance = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        registration_table = "forum_events_forum_events"+'_'+str(event_id)+'_registration'
        
        cursor = connection.cursor()
        
        cursor.execute(f"INSERT INTO {registration_table} (name, event_id_id, user_id, semester, division, email,gender) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (user_id) DO NOTHING;", [user_instance.name, event_id, user_id, user_instance.semester, user_instance.division, user_instance.email, user_instance.gender])
        
        cursor.close()
        
        event_cache_name = "forum_events*"
        
        cache.delete_pattern(event_cache_name)
        
        return Response({"message": "Registration successful."}, status=status.HTTP_200_OK)
class DeleteEvent(APIView):
    def delete(self,request,pk):
        #deleting image and thumbnail image
        try:
            ob = forumEvents.objects.get(pk=pk)
            
        except ob.DoesNotExist:
            return Response({"error": "Image not found."}, status=404)
        
        if ob.poster_image:
            ob.poster_image.delete()
        if ob.thumbnail_poster_image:
            ob.thumbnail_poster_image.delete()
        
        tables=["forum_events_forum_events"+ '_'+str(ob.id)+'_likes', "forum_events_forum_events"+'_'+str(ob.id)+'_registration']

        
        if ob.register_button_link=='vcec_form':
            
            ob.delete()
            
            try:
                cursor= connection.cursor()
                for table_name in tables:
                    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            
            except forumEvents.DoesNotExist:
                return Response( "Event not found.")
            except Exception as e:
                return Response( f"An error occurred: {str(e)}")
        else:
            ob.delete()
            
            cursor=connection.cursor()
            cursor.execute(f"DROP TABLE IF EXISTS {tables[0]}")

        connection.close()
        
        event_cache_name = "forum_events*"
            
        cache.delete_pattern(event_cache_name)
            
        return Response({"status":"Event deleted successfully"},status=status.HTTP_200_OK)
                
                    
class GetEventAnalysis(APIView):
    def get(self,request):
        try:
            event_id = request.query_params.get('event_id')
            
            
            register_table = "forum_events_forum_events"+'_'+str(event_id)+'_registration'
            
            cursor = connection.cursor()
            
            cursor.execute(f"SELECT COUNT(*), semester FROM {register_table} GROUP BY semester")
            
            instance = cursor.fetchall()    
            print(instance)
            
            cursor.close()
            
            return Response({"message": "Analysis retrieved successfully."},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "Event not found"}, status=status.HTTP_404_NOT_FOUND)
@api_view(['PUT'])
def update_event(request,id):

    serializer=FormSerializer(data=request.data)
    cur=connection.cursor()    
    
    if serializer.is_valid():
        if request.data.get('content'):
            cur.execute(f"UPDATE forum_events_forumevents SET content='{serializer.data['content']}' WHERE id={id}")
       
        if request.data.get("title"):
            cur.execute(f"UPDATE forum_events_forumevents SET title='{serializer.data['title']}' WHERE id={id}")
         
        if request.data.get('whatsapp_link'):
            cur.execute(f"UPDATE forum_events_forumevents SET whatsapp_link='{serializer.data['whatsapp_link']}' WHERE id={id}")

        if request.data.get('register_button_link'):
            model_name =["..placeholder..","forum_events"+'_'+str(id)+'_registration']
            table_name="forum_events_forum_events"+'_'+str(id)+'_registration'
            cur.execute(f"UPDATE forum_events_forumevents SET register_button_link='{serializer.data['register_button_link']}' WHERE id={id}")
            if serializer.data['register_button_link']!='vcec_form':
                cur.execute(f"DROP TABLE IF EXISTS {table_name}")
                
            else:
                cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
                tables = [row[0] for row in cur.fetchall()]
                if table_name not in tables:
                    create_dynamic_models(model_name)
                
        cur.close()
        connection.close()
        
        event_cache_name = "forum_events*"
        
        cache.delete_pattern(event_cache_name)
        
        return Response({"message": "Record Updated successfully."},status=status.HTTP_200_OK)

    else:
        cur.close()
        connection.close()
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def image_file(request, pk):
    try:
        image_instance = forumEvents.objects.get(id=pk)
    except forumEvents.DoesNotExist:
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
        image_instance = forumEvents.objects.get(id=pk)
    except forumEvents.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if image_instance.thumbnail_poster_image:
        thumbnail_path = image_instance.thumbnail_poster_image.path
        with open(thumbnail_path, "rb") as thumbnail_file:
            response = HttpResponse(thumbnail_file.read(), content_type="image/jpeg")
            response["Content-Disposition"] = f"inline; filename={image_instance.thumbnail_poster_image.name}"
            return response

    return Response(status=status.HTTP_404_NOT_FOUND)

class EventStatus(APIView):
    def post(self,request,id):
        event=forumEvents.objects.get(id=id)

        if event.status=='Upcoming':
            event.status='Ended'
        else:
            event.status='Upcoming'
        event.save()
        return Response({"message":"status updated successfully"},status=status.HTTP_200_OK)

class GetEventById(APIView):
    def get(self,request,id):
        try:
            event=forumEvents.objects.get(id=id)
            
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

            
            forums_divided = event.published_by.split(',')
            
            print(forums_divided)
            forum_image_url = []
            
            for forum in forums_divided:
                forum_instance = AddForum.objects.get(forum_role_name=forum)
                forum_image_url.append({"image_url": forum_instance.image_url})
                
            model_name ="forum_events_forum_events" + '_'+str(id)+'_likes'
            print(user_id,id)
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
                
            user_instance = User.objects.get(id=user_id)
            
            if user_instance.role == "guest":
                register_button = False
            else:
                register_button = True
            
            if event.register_button_link == "vcec_form":
                register_table = "forum_events_forum_events"+'_'+str(id)+'_registration'
                
                cursor.execute(f"SELECT COUNT(*) FROM {register_table} WHERE user_id=%s", [user_id])
                
                fetch_result = cursor.fetchone()[0]
                
                if fetch_result > 0:
                    already_registered = True
                else:
                    already_registered = False
            else:
                already_registered = False
            
            serializer=FormGetSerializer(event)
            return Response({"event_result": serializer.data, "total_likes": count_likes,"conducted_by": forum_image_url,"is_liked": is_liked, "register_button": register_button,"already_registered": already_registered},status=status.HTTP_200_OK)
        except forumEvents.DoesNotExist:
            return Response({"status": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

def extract_unique_meaningful_words(text):
   
    words = word_tokenize(text)
    words = [word.lower() for word in words if word.isalnum()]
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word not in stop_words and not word.isdigit()]
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words]

    words = [word for word in words if len(word) > 2]

    unique_words = set(words)

    return unique_words

class LikeEvent(APIView):
    def post(self,request):
        try:
            event_id = request.query_params.get('event_id')
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
           
            model_name ="forum_events_forum_events" + '_'+str(event_id)+'_likes'
            cursor= connection.cursor()
            cursor.execute(f"UPDATE {model_name} SET is_liked=%s WHERE user_id=%s", [like_status , user_id])
            cursor.close()
            
            event_cache_name = "forum_events*"
        
            cache.delete_pattern(event_cache_name)
            
            return Response({"message": "Likes record added successfully."}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response( f"An error occurred: {str(e)}")
        
class SetView(APIView):
    def post(self, request):
       
        try:
            event_id = request.query_params.get('event_id')
            
            event_instance = forumEvents.objects.get(id=event_id)
            
            if event_instance is None:
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
            
            model_name = "forum_events_forum_events" + '_' + str(event_id) + '_likes'
            
            print(model_name)
            
            user_id = str(user_id)
            
            cursor = connection.cursor()
            
            cursor.execute(f"INSERT INTO {model_name} (user_id,name,event_id_id,is_liked,views) VALUES ({user_id},'{user_instance.name}',{event_id},false,true) ON CONFLICT (user_id) DO NOTHING;")
            cursor.close()
            
            event_cache_name = "forum_events*"
        
            cache.delete_pattern(event_cache_name)
            
            return Response({"message": "Views record added successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            print(str(e))
            return Response(f"An error occurred: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
