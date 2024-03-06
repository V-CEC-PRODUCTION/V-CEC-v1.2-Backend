from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from .models import Image
from .serializers import ImageSerializer, ImageGetSerializer
from PIL import Image as PilImage
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.cache import cache
import time, random, string , json, os
from vcec_bk.pagination import CustomPageNumberPagination
from azure.storage.blob import BlobServiceClient, BlobClient, ContentSettings

connection_string = f"DefaultEndpointsProtocol=https;AccountName={os.getenv('AZURE_STORAGE_ACCOUNT_NAME')};AccountKey={os.getenv('AZURE_ACCOUNT_KEY')};EndpointSuffix=core.windows.net"

blob_service_client = BlobServiceClient.from_connection_string(connection_string)

@api_view(['POST'])
def create_image(request):
    try:
        serializer = ImageSerializer(data=request.data)
        if serializer.is_valid():
            image_instance = serializer.save()
            
            # Generate and save the thumbnail
            if image_instance.image:
                img = PilImage.open(BytesIO(image_instance.image.read()))
                img.thumbnail((100, 100))
                thumb_io = BytesIO()
                img.save(thumb_io, format='JPEG')
                thumb_io.seek(0)

                # Generate a unique filename for the thumbnail
                timestamp = int(time.time())
                random_string = ''.join(random.choices(string.ascii_letters, k=6))
                unique_filename = f"{timestamp}_{random_string}_thumbnail.jpg"

                folder_name = "thumbnails"
                
                blob_media_name = f"homepage_images/{folder_name}/{unique_filename}"
               
                blob_client = blob_service_client.get_blob_client(container="media", blob=blob_media_name)
                blob_client.upload_blob(thumb_io, content_settings=ContentSettings(content_type='image/jpeg'))

                image_instance.thumbnail = blob_media_name
                image_instance.save()

                homepage_images = 'homepage_images*'
                cache.delete_pattern(homepage_images)
                
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    except Exception as e:
        print(e)
        return Response({"message": f"{e}"}, status= status.HTTP_500_INTERNAL_SERVER_ERROR)
class get_all_images(APIView,CustomPageNumberPagination):
    def get(self,request):
        
                 
        homepage_images = f"homepage_images"
        
        # home_img_result = cache.get(homepage_images)
        
        home_img_result = None
        
        if home_img_result is None:
            print("Data from database")
            images = Image.objects.values('id', 'image_url', 'thumbnail_url').order_by('-id')
            
            serializer = ImageGetSerializer(images, many=True)
            
            home_img_result = serializer.data
            
            cache.set(homepage_images, json.dumps(home_img_result),timeout=60*60*24*7)
            
        else:
            print("Data from cache")
            home_img_result = json.loads(home_img_result)
        
        response = {
            "homepage_images": home_img_result,
        }
        return Response(response)


@api_view(['GET'])
def image_file(request, pk):
    try:
        image_instance = Image.objects.get(pk=pk)
    except Image.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if image_instance.image:
        image_path = image_instance.image.path
        with open(image_path, "rb") as image_file:
            response = HttpResponse(image_file.read(), content_type="image/jpeg")
            response["Content-Disposition"] = f"inline; filename={image_instance.image.name}"
            return response

    return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def thumbnail_file(request, pk):
    try:
        image_instance = Image.objects.get(pk=pk)
    except Image.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if image_instance.thumbnail:
        thumbnail_path = image_instance.thumbnail.path
        with open(thumbnail_path, "rb") as thumbnail_file:
            response = HttpResponse(thumbnail_file.read(), content_type="image/jpeg")
            response["Content-Disposition"] = f"inline; filename={image_instance.thumbnail.name}"
            return response

    return Response(status=status.HTTP_404_NOT_FOUND)



@api_view(['GET'])
def get_image_detail(request, pk):
    try:
        image = Image.objects.get(pk=pk)
    except Image.DoesNotExist:
        return Response(status=404)
    
    serializer = ImageSerializer(image)
    return Response(serializer.data)

@api_view(['DELETE'])
def delete_image(request, pk):
    try:
        image = Image.objects.get(pk=pk)
    except Image.DoesNotExist:
        return Response({"error": "Image not found."}, status=404)

    try:
        blob_service_client.delete_blob('media', f"{image.image.name}")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        
    try:
        blob_service_client.delete_blob('media', f"{image.thumbnail.name}")
        
    except Exception as e:
        print(f"An error occurred: {e}")
           
    if image.image:
        image.image.delete()
    if image.thumbnail:
        image.thumbnail.delete()
    
    homepage_images = 'homepage_images'
    
    image.delete()
    
    homepage_images = 'homepage_images*'
    cache.delete_pattern(homepage_images)
    

    return Response({"message": "Image and thumbnail deleted successfully."}, status=204)


