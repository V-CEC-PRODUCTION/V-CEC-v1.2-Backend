from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse, FileResponse
from PIL import Image as PilImage
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from .serializers import FormSerializer
import time,random ,string
from .models import create_tables

@api_view(['POST'])
def create_forms(request):
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

        thumbnail = InMemoryUploadedFile(thumb_io, None, unique_filename, 'image/jpeg', None, None)
        serializer_instance.thumbnail_poster_image.save(unique_filename, thumbnail, save=True)
        create_tables("forum_events",serializer_instance.id)
        return Response(serializer.data,status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)



