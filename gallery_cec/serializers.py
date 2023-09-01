from rest_framework import serializers
from .models import FileStore, VideoStore


class GallerySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FileStore
        fields = ('id', 'media_file', 'thumbnail', 'media_url', 'thumbnail_url', 'tag', 'upload_time')
        
class VideoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = VideoStore
        fields = ['id', 'video_file', 'fid', 'video_url']
        
        
class GalleryGetSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FileStore
        fields = ('id', 'media_url', 'thumbnail_url', 'tag', 'upload_time')
        
class VideoGetSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = VideoStore
        fields = ['id', 'fid', 'video_url']