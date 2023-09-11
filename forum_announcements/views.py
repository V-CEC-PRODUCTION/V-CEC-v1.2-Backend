import time,random ,string
from django.shortcuts import render
from rest_framework.decorators import api_view
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

@api_view(['POST'])
def create_announcement(request):
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
        
        model_name ="forum_announcements" + '_'+str(serializer_instance.id)+'_likes'
        if create_dynamic_model(model_name,serializer_instance.id):
            return Response(serializer.data,status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

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

        cur.close()
        connection.close()
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

@api_view(['GET'])
def get_announcements(request):
    try:
        
        announcements = forumAnnouncements.objects.all().order_by('-publish_date')
        serializer = FormGetSerializer(announcements, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    except forumAnnouncements.DoesNotExist:
        return Response({"status": "Records not found"}, status=status.HTTP_404_NOT_FOUND)