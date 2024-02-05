from rest_framework import serializers
from .models import AddForum

class ForumSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddForum
        fields = '__all__'
        
        
class ForumGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddForum
        fields = ['id', 'forum_name','display_name','forum_description','email_id','forum_role_name','image_url','thumbnail_url']
        
class ForumImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddForum
        fields = ['id', 'forum_image']
        
class ForumDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddForum
        fields = ['id', 'forum_name','display_name','forum_description','email_id','forum_role_name']

class ForumRoleNameGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddForum
        fields = ['id', 'forum_name','display_name','forum_role_name']

class ForumListGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddForum
        fields = ['id', 'display_name','forum_role_name','image_url','thumbnail_url']