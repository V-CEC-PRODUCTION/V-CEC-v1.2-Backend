from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse 
from PIL import Image as PilImage
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from .serializers import FormSerializer,FormGetSerializer
import time,random ,string
from .models import create_tables,forumEvents,create_dynamic_models
from django.db import connection


@api_view(['POST'])
def create_event(request):
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

@api_view(['GET'])
def get_events(request):
    try:
        if request.query_params.get('status') == 'Upcoming':
            forms = forumEvents.objects.filter(status='Upcoming').order_by('-publish_date')
        elif request.query_params.get('status') == 'Ended':
            forms = forumEvents.objects.filter(status='Ended').order_by('-publish_date')
        else:
            return Response({"status": "Invalid status value"}, status=status.HTTP_400_BAD_REQUEST)

        
        serializer = FormGetSerializer(forms, many=True)

       
        return Response(serializer.data, status=status.HTTP_200_OK)
    except forumEvents.DoesNotExist:
        return Response({"status": "Forms not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def delete_event(request,pk):
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

        try:
            cursor= connection.cursor()
            for table_name in tables:
                cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        
        except forumEvents.DoesNotExist:
            return Response( "Event not found.")
        except Exception as e:
            return Response( f"An error occurred: {str(e)}")
    else:
        cursor=connection.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {tables[0]}")

    ob.delete()
    connection.close()
    return Response({"status":"Event deleted successfully"},status=status.HTTP_200_OK)
            
                
                
            
    

                         
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
