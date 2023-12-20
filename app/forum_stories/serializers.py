from rest_framework import serializers
from .models import ForumStories


class ForumStoriesSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ForumStories
        fields = '__all__'
        
        
class ForumStoriesGetSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ForumStories
        fields = ['id', 'forum_id', 'content', 'media_url', 'thumbnail_media_url', 'forum_tag', 'file_tag', 'upload_time']