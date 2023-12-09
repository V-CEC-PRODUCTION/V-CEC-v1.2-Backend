from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse, FileResponse
from .models import FileStore, VideoStore
from .serializers import GallerySerializer, VideoSerializer, GalleryGetSerializer, VideoGetSerializer
from PIL import Image as PilImage
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from celery import shared_task
from django.core.cache import cache
import time, random, json,string, os, cv2, numpy as np
import redis

@shared_task
def calculate_frame_score(frame):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    score = np.mean(gray_frame)
    return score

@shared_task
def get_best_thumbnail(video_stream):
    
    temp_video_dir = './temporary/video/'
    
    thumbnail_gallery_dir = './media/gallery/cec/thumbnails/'
    
    os.makedirs(temp_video_dir, exist_ok=True)
    os.makedirs(thumbnail_gallery_dir, exist_ok=True)
    
    timestamp_thumb = int(time.time())
    random_string_thumb = ''.join(random.choices(string.ascii_letters, k=6))
    unique_filename_thumbnail = f"{timestamp_thumb}_{random_string_thumb}_thumbnail.jpg"
    
    thumbnail_image_path = os.path.join(thumbnail_gallery_dir, unique_filename_thumbnail)
    temp_video_path = os.path.join(temp_video_dir, 'file.mp4')

    # Read the video data from the BytesIO object
    video_data = video_stream.read()

    # Write the video data to the temporary file
    with open(temp_video_path, 'wb') as temp_video_file:
        temp_video_file.write(video_data)

    # Now you can use the temporary video file path with cv2.VideoCapture()
    cap = cv2.VideoCapture(temp_video_path)
 
    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    best_thumbnail_idx = -1
    best_frame_score = float('-inf')

    for idx in range(num_frames):
        ret, frame = cap.read()
        if not ret:
            break

        frame_score = calculate_frame_score(frame)

        if frame_score > best_frame_score:
            best_frame_score = frame_score
            best_thumbnail_idx = idx

    cap.release()

    # Extract and save the best thumbnail
    cap = cv2.VideoCapture(temp_video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, best_thumbnail_idx)
    ret, best_thumbnail = cap.read()
    
    timestamp = int(time.time())
    random_string = ''.join(random.choices(string.ascii_letters, k=6))
    unique_filename = f"{timestamp}_{random_string}_vid_org.jpg"
    
    orginal_path = f"./media/gallery/cec/images/{unique_filename}"
    
    if ret:
        cv2.imwrite(orginal_path, best_thumbnail)
        print(f"Best thumbnail saved as {unique_filename}")
    else:
        print("Error extracting the best thumbnail.")
        
    cap.release()
    
    os.remove(temp_video_path)
    
    img = PilImage.open(orginal_path)
    img.thumbnail((100, 100))
   
    img.save(thumbnail_image_path, format='JPEG')
    
    
    return orginal_path , thumbnail_image_path


@shared_task
@api_view(['DELETE'])
def delete_file(request, pk):
    try:
        image = FileStore.objects.get(pk=pk)
    except FileStore.DoesNotExist:
        return Response({"error": "FileStore not found."}, status=404)
    
    if image.tag == 'vid':
        try:
            video = VideoStore.objects.get(fid=pk)
            print("video")
        except VideoStore.DoesNotExist:
            return Response({"error": "VideoStore not found."}, status=404)
        
        if video.video_file:
            video.video_file.delete()
        video.delete()
        
    if image.media_file:
        print("media file deleted")
        image.media_file.delete()
    if image.thumbnail:
        print("thumbnail deleted")
        image.thumbnail.delete()
    
    image.delete()
    
    
    gallery_files = 'gallery_files'
        
    files_list = FileStore.objects.values('id', 'media_url', 'thumbnail_url', 'tag', 'upload_time')
    
    files_result = GalleryGetSerializer(files_list, many=True)
    
    gallery_files_result = files_result.data
    
    cache.set(gallery_files, json.dumps(gallery_files_result),timeout=60*60*24*7)
    
    
    return Response({"message": "FileStore and thumbnail deleted successfully."}, status=status.HTTP_200_OK)




@api_view(['POST'])
def post_file(request):
    
    media_file = request.FILES.get('media_file')
    
    if media_file:
        
        media_item = None
       
        if media_file.content_type.startswith('image'):
            
            media_item = GallerySerializer(data={'media_file' : media_file,'tag' : 'img'})
            
            if media_item.is_valid():
                media_instance = media_item.save()
            
            
            # Generate and save the thumbnail
            # if media_instance.image:
                img = PilImage.open(media_instance.media_file.path)
                img.thumbnail((100, 100))
                thumb_io = BytesIO()
                img.save(thumb_io, format='JPEG')

                # Generate a unique filename for the thumbnail
                timestamp = int(time.time())
                random_string = ''.join(random.choices(string.ascii_letters, k=6))
                unique_filename = f"{timestamp}_{random_string}_thumbnail.jpg"

                thumbnail = InMemoryUploadedFile(thumb_io, None, unique_filename, 'image/jpeg', None, None)
                media_instance.thumbnail.save(unique_filename, thumbnail, save=True)
                
        elif media_file.content_type.startswith('video'):
            
            video_data = media_file.read()

            # Convert the video data into a BytesIO object
            video_stream = BytesIO(video_data)
            
            img_path, img_thumbnail = get_best_thumbnail(video_stream)
            
            with open(img_path, 'rb') as img_file:
                orginal_image = img_file.read()
                
            with open(img_thumbnail, 'rb') as img_thumbnail_file:
                thumbnail_image = img_thumbnail_file.read()
                
      
            orginal_image_vid = InMemoryUploadedFile(
                BytesIO(orginal_image),  # Provide the content as BytesIO
                field_name=None,  # Field name (set to None for now)
                name='orginal_image.jpg',  # Name of the file
                content_type='image/jpeg',
                size=len(orginal_image),
                charset=None
            )
            
            thumb_image_vid = InMemoryUploadedFile(
                BytesIO(thumbnail_image),  # Provide the content as BytesIO
                field_name=None,  # Field name (set to None for now)
                name='thumbnail_image.jpg',  # Name of the file
                content_type='image/jpeg',
                size=len(thumbnail_image),
                charset=None
            )
            # Create the data dictionary for the serializer
            data = {
                'media_file': orginal_image_vid,  # Pass the file object
                'thumbnail': thumb_image_vid,  # Pass the file object
                'tag': 'vid'
            }
            
            media_item = GallerySerializer(data=data)
            
            if media_item.is_valid():
                # Save the media instance
                media_instance = media_item.save()
                
                os.remove(img_path)
                os.remove(img_thumbnail)
                # Create and save the video item
                video_item = VideoSerializer(data={'video_file': media_file, 'fid': media_instance.id})
                
                if video_item.is_valid():
                    video_instance = video_item.save()
                    
            video_instance.save()
            if media_instance.tag == 'vid':
                media_instance.video_url=video_instance.video_url
            media_instance.save()
            
        gallery_files = 'gallery_files'
        
        
        files_list = FileStore.objects.values('id', 'media_url', 'thumbnail_url', 'tag', 'upload_time')
        
        files_result = GalleryGetSerializer(files_list, many=True)
        
        gallery_files_result = files_result.data
        
        cache.set(gallery_files, json.dumps(gallery_files_result),timeout=60*60*24*7)
            
        return Response(media_item.data, status=201)
    return Response(media_item.errors, status=400)

@api_view(['GET'])
def stream_video(request, pk):
    try:
        video_instance = VideoStore.objects.get(id=pk)
        video_path = video_instance.video_file.path
    except VideoStore.DoesNotExist:
        return HttpResponse(status=404)  # Video not found
    
    # Open the video file in binary mode
    video_file = open(video_path, 'rb')

    # Create a FileResponse instance for streaming
    response = FileResponse(video_file, content_type='video/mp4')
    
    # Set the Content-Disposition header to inline to show video in the browser
    response['Content-Disposition'] = f'inline; filename="{os.path.basename(video_path)}"'
    
    return response

@api_view(['GET'])
def get_all_files(request):
    
    gallery_files = 'gallery_files'
    
    # gallery_files_result = cache.get(gallery_files)
    gallery_files_result = None    
    if gallery_files_result is None:
        
        print("Data from database")
        
        images = FileStore.objects.values('id', 'media_url', 'thumbnail_url', 'tag', 'upload_time','video_url')
        serializer = GalleryGetSerializer(images, many=True)
        
        gallery_files_result = serializer.data
        
        cache.set(gallery_files, json.dumps(gallery_files_result),timeout=60*60*24*7)
        
    else:
        print("Data from cache")
        gallery_files_result = json.loads(gallery_files_result)
        
    
    response = {
        "gallery_files": gallery_files_result,
    }
    
    return Response(response)


@api_view(['GET'])
def media_file(request, pk):
    try:
        media_instance = FileStore.objects.get(pk=pk)
    except FileStore.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if media_instance.media_file:
        image_path = media_instance.media_file.path
        with open(image_path, "rb") as image_file:
            response = HttpResponse(image_file.read(), content_type="image/jpeg")
            response["Content-Disposition"] = f"inline; filename={media_instance.media_file.name}"
            return response

    return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def thumbnail_file(request, pk):
    try:
        media_instance = FileStore.objects.get(pk=pk)
    except FileStore.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if media_instance.thumbnail:
        thumbnail_path = media_instance.thumbnail.path
        with open(thumbnail_path, "rb") as thumbnail_file:
            response = HttpResponse(thumbnail_file.read(), content_type="image/jpeg")
            response["Content-Disposition"] = f"inline; filename={media_instance.thumbnail.name}"
            return response

    return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_detail_video(request, pk):
    
    try:
        file = VideoStore.objects.get(fid=pk)
        
        gallery_videos = str(pk)+'gallery_videos'
        
        gallery_videos_result = cache.get(gallery_videos)
        
        if gallery_videos_result is None:
            
            print("Data from database")
            
            serializer = VideoGetSerializer(file)
            
            gallery_videos_result = serializer.data
            
            cache.set(gallery_videos, json.dumps(gallery_videos_result),timeout=60*60)
            
        else:
            
            print("Data from cache")
            gallery_videos_result = json.loads(gallery_videos_result)
            
        if gallery_videos_result['video_url']:
            return Response(gallery_videos_result,status=200)
        else:
            return Response({"Not found in the database"},status=404)
            
    except FileStore.DoesNotExist:
        return Response({"Not found in the database"},status=404)
    
    

   

@api_view(['GET'])
def get_file_detail(request, pk):
    try:
        file = FileStore.objects.get(pk=pk)
    except FileStore.DoesNotExist:
        return Response(status=404)
    
    serializer = GallerySerializer(file)
    return Response(serializer.data)


