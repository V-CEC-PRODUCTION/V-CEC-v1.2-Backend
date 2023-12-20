from rest_framework import serializers
from .models import HighlightImage

class ImageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = HighlightImage
        fields = ['id','content', 'image', 'thumbnail', 'image_url', 'thumbnail_url', 'upload_time', 'tag']
        
class ImageGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = HighlightImage
        fields = ['id','content', 'image_url', 'thumbnail_url', 'upload_time', 'tag']
        
