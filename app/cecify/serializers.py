from .models import RadioEpisodesDetails, RadioSeasonDetails
from rest_framework import serializers

class RadioSeasonDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RadioSeasonDetails
        fields = '__all__'

class RadioSeasonFilterMethodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RadioSeasonDetails
        fields = ['season']
        
class RadioEpisodeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RadioEpisodesDetails
        fields = ['id', 'season', 'season_number','episode', 'content','spotify_url', 'youtube_url', 'google_podcast_url']
        
class RadioEpisodesDetailsGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = RadioEpisodesDetails
        fields = ['id', 'season_number','episode', 'content', 'image_url', 'thumbnail_url', 'upload_time', 'spotify_url', 'youtube_url', 'google_podcast_url']     
class RadioEpisodesDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RadioEpisodesDetails
        fields = ['id', 'season', 'season_number','episode', 'content', 'image', 'thumbnail', 'image_url', 'thumbnail_url', 'upload_time', 'spotify_url', 'youtube_url', 'google_podcast_url']