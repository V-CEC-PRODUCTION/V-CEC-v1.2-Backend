from rest_framework import serializers
from .models import Image

class ImageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Image
        fields = ['id', 'image', 'thumbnail', 'image_url', 'thumbnail_url']
        
class ImageGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image_url', 'thumbnail_url']