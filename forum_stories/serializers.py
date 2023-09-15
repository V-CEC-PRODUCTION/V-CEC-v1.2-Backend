from rest_framework import serializers
from .models import ForumStories


class ForumStoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForumStories
        fields = '__all__'