from rest_framework import serializers
from .models import forumEvents

class FormSerializer(serializers.ModelSerializer):

    class Meta:
        model=forumEvents
        fields=('id','title','content','poster_image','thumbnail_poster_image','register_button_link','whatsapp_link','status','publish_date','published_by','hashtags','event_date')

class FormUpdateSerializer(serializers.ModelSerializer):
        content = serializers.CharField(required=False)
        title = serializers.CharField(required=False)
        whatsapp_link = serializers.CharField(required=False, allow_blank=True)
        register_button_link = serializers.CharField(required=False)
        class Meta:
            model=forumEvents
            fields=('id','title','content','register_button_link','whatsapp_link')
class FormGetSerializer(serializers.ModelSerializer):

    class Meta:
        model=forumEvents
        fields=('id','title','content','register_button_link','poster_image_url','thumbnail_poster_image_url','whatsapp_link','status','publish_date','published_by','hashtags','event_date')

