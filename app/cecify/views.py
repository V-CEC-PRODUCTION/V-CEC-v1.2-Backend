from .models import RadioEpisodesDetails, RadioSeasonDetails
from rest_framework.response import Response
from rest_framework import status
from .serializers import RadioSeasonDetailsSerializer, RadioEpisodesDetailsSerializer, RadioEpisodeUpdateSerializer, RadioEpisodesDetailsGetSerializer, RadioSeasonFilterMethodsSerializer
from rest_framework.views import APIView
import os, time, random, string
from azure.storage.blob import BlobServiceClient, ContentSettings
from PIL import Image as PilImage
from io import BytesIO

connection_string = f"DefaultEndpointsProtocol=https;AccountName={os.getenv('AZURE_STORAGE_ACCOUNT_NAME')};AccountKey={os.getenv('AZURE_ACCOUNT_KEY')};EndpointSuffix=core.windows.net"

blob_service_client = BlobServiceClient.from_connection_string(connection_string)

class SeasonFilterMethods(APIView):
    def get(self, request):
        try:
            seasons = RadioSeasonDetails.objects.values('season')
            serializer = RadioSeasonFilterMethodsSerializer(seasons, many=True)
            
            return Response({"season_result":serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                            
class SeasonDetails(APIView):
    def get(self, request):
        try:
            seasons = RadioSeasonDetails.objects.all()
            serializer = RadioSeasonDetailsSerializer(seasons, many=True)
            return Response({"season_result":serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = RadioSeasonDetailsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"result":serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def put(self, request):
        try:
            season = RadioSeasonDetails.objects.get(season=request.data['season'])
            serializer = RadioSeasonDetailsSerializer(season, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def delete(self, request):
        try:
            season = RadioSeasonDetails.objects.get(season=request.data['season'])
            season.delete()
            return Response({"message": "season deleted successfully"},status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class EpisodeDetails(APIView):
    def post(self, request):
        try:
            season_instance = RadioSeasonDetails.objects.get(season=request.data['season'])
            
            if season_instance:
                request.data['season'] = season_instance.id
                request.data['season_number'] = season_instance.season
            else:
                return Response({"error": "Season does not exist"}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = RadioEpisodesDetailsSerializer(data=request.data)
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
                    
                    blob_media_name = f"cecify/radio/episodes/{folder_name}/{unique_filename}"
                
                    blob_client = blob_service_client.get_blob_client(container="media", blob=blob_media_name)
                    blob_client.upload_blob(thumb_io, content_settings=ContentSettings(content_type='image/jpeg'))

                    image_instance.thumbnail = blob_media_name
                    image_instance.save()
                    
                return Response({"result":serializer.data}, status=status.HTTP_201_CREATED)
            return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def get(self, request):
        try:
            episodes = RadioEpisodesDetails.objects.filter(season_number=request.GET.get('season_number'))
            serializer = RadioEpisodesDetailsGetSerializer(episodes, many=True)
            return Response({"episodes_result":serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def put(self, request):
        try:
            # Make a mutable copy of request.data
            mutable_data = request.data.copy()
            
            # Retrieve the season_instance
            season_instance = RadioSeasonDetails.objects.get(season=mutable_data['season'])
            
            # Update the season ID in the mutable_data
            if season_instance:
                mutable_data['season'] = season_instance.id
            else:
                return Response({"error": "Season does not exist"}, status=status.HTTP_400_BAD_REQUEST)
                        
            # Retrieve the episode
            episode = RadioEpisodesDetails.objects.get(season=mutable_data['season'], episode=mutable_data['episode'])
            
            # Serialize and save the episode
            serializer = RadioEpisodeUpdateSerializer(episode, data=mutable_data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "successfully updated"}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def delete(self, request):
        try:
            mutable_data = request.data.copy()
            
            # Retrieve the season_instance
            season_instance = RadioSeasonDetails.objects.get(season=mutable_data['season'])
            
            # Update the season ID in the mutable_data
            if season_instance:
                mutable_data['season'] = season_instance.id
            else:
                return Response({"error": "Season does not exist"}, status=status.HTTP_400_BAD_REQUEST)
                        
            # Retrieve the episode
            
            try:
                episode = RadioEpisodesDetails.objects.get(season=mutable_data['season'], episode=mutable_data['episode'])
                
            except RadioEpisodesDetails.DoesNotExist:
                return Response({"error": "Episode does not exist"}, status=status.HTTP_400_BAD_REQUEST)
                
            try:
                blob_service_client.delete_blob('media', f"{episode.image.name}")
                
            except Exception as e:
                print(f"An error occurred: {e}")
                
            try:
                blob_service_client.delete_blob('media', f"{episode.thumbnail.name}")
                
            except Exception as e:
                print(f"An error occurred: {e}")
                
            if episode.image:
                episode.image.delete()
            
            if episode.thumbnail:
                episode.thumbnail.delete()
                
            episode.delete()
            
            return Response({"message": "Episode deleted successfully"}, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)