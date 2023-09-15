from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ForumStories, UserCountStories
from .serializers import ForumStoriesSerializer
from users.models import User, Token
from users.utils import TokenUtil
from PIL import Image as PilImage

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
        
        # media_file = request.FILES.get('media_file')
        # content = request.POST.get('content')
    
        # if media_file:
            
        #     media_item = None
        
        #     if media_file.content_type.startswith('image'):
                
        #         media_item = ForumStoriesSerializer(data={'media_file' : media_file,'tag' : 'img'})
                
        #         if media_item.is_valid():
        #             media_instance = media_item.save()
                
                
        #         # Generate and save the thumbnail
        #         # if media_instance.image:
        #             img = PilImage.open(media_instance.media_file.path)
        #             img.thumbnail((100, 100))
        #             thumb_io = BytesIO()
        #             img.save(thumb_io, format='JPEG')

        #             # Generate a unique filename for the thumbnail
        #             timestamp = int(time.time())
        #             random_string = ''.join(random.choices(string.ascii_letters, k=6))
        #             unique_filename = f"{timestamp}_{random_string}_thumbnail.jpg"

        #             thumbnail = InMemoryUploadedFile(thumb_io, None, unique_filename, 'image/jpeg', None, None)
        #             media_instance.thumbnail.save(unique_filename, thumbnail, save=True)
                    
        #     elif media_file.content_type.startswith('video'):
                
        #         video_data = media_file.read()

        #         # Convert the video data into a BytesIO object
        #         video_stream = BytesIO(video_data)
                
        #         img_path, img_thumbnail = get_best_thumbnail(video_stream)
                
        #         with open(img_path, 'rb') as img_file:
        #             orginal_image = img_file.read()
                    
        #         with open(img_thumbnail, 'rb') as img_thumbnail_file:
        #             thumbnail_image = img_thumbnail_file.read()
                    
        
        #         orginal_image_vid = InMemoryUploadedFile(
        #             BytesIO(orginal_image),  # Provide the content as BytesIO
        #             field_name=None,  # Field name (set to None for now)
        #             name='orginal_image.jpg',  # Name of the file
        #             content_type='image/jpeg',
        #             size=len(orginal_image),
        #             charset=None
        #         )
                
        #         thumb_image_vid = InMemoryUploadedFile(
        #             BytesIO(thumbnail_image),  # Provide the content as BytesIO
        #             field_name=None,  # Field name (set to None for now)
        #             name='thumbnail_image.jpg',  # Name of the file
        #             content_type='image/jpeg',
        #             size=len(thumbnail_image),
        #             charset=None
        #         )
        #         # Create the data dictionary for the serializer
        #         data = {
        #             'media_file': orginal_image_vid,  # Pass the file object
        #             'thumbnail': thumb_image_vid,  # Pass the file object
        #             'tag': 'vid'
        #         }
                
        #         media_item = GallerySerializer(data=data)
                
        #         if media_item.is_valid():
        #             # Save the media instance
        #             media_instance = media_item.save()
                    
        #             os.remove(img_path)
        #             os.remove(img_thumbnail)
        #             # Create and save the video item
        #             video_item = VideoSerializer(data={'video_file': media_file, 'fid': media_instance.id})
                    
        #             if video_item.is_valid():
        #                 video_instance = video_item.save()
                        
        #         media_instance.save()
        #         video_instance.save()
                
        #     gallery_files = 'gallery_files'
            
            
        #     files_list = FileStore.objects.values('id', 'media_url', 'thumbnail_url', 'tag', 'upload_time')
            
        #     files_result = GalleryGetSerializer(files_list, many=True)
            
        #     gallery_files_result = files_result.data
            
        #     cache.set(gallery_files, json.dumps(gallery_files_result),timeout=60*60*24*7)
                
        #     return Response(media_item.data, status=201)
        # return Response(media_item.errors, status=400)
        