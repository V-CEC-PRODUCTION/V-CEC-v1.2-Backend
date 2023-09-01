from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from .models import Image
from .serializers import ImageSerializer, ImageGetSerializer
from PIL import Image as PilImage
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import time
import random
import string

@api_view(['POST'])
def create_image(request):
    serializer = ImageSerializer(data=request.data)
    if serializer.is_valid():
        image_instance = serializer.save()

        # Generate and save the thumbnail
        if image_instance.image:
            img = PilImage.open(image_instance.image.path)
            img.thumbnail((100, 100))
            thumb_io = BytesIO()
            img.save(thumb_io, format='JPEG')

            # Generate a unique filename for the thumbnail
            timestamp = int(time.time())
            random_string = ''.join(random.choices(string.ascii_letters, k=6))
            unique_filename = f"{timestamp}_{random_string}_thumbnail.jpg"

            thumbnail = InMemoryUploadedFile(thumb_io, None, unique_filename, 'image/jpeg', None, None)
            image_instance.thumbnail.save(unique_filename, thumbnail, save=True)

        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)



@api_view(['GET'])
def get_all_images(request):
    images = Image.objects.values('id', 'image_url', 'thumbnail_url')
    
    serializer = ImageGetSerializer(images, many=True)
    
    response = {
        "homepage_images": serializer.data,
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
    
    if image.image:
        image.image.delete()
    if image.thumbnail:
        image.thumbnail.delete()
    
    image.delete()
    return Response({"message": "Image and thumbnail deleted successfully."}, status=204)


