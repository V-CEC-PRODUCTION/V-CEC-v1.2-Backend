from rest_framework import serializers
from .models import forumAnnouncements

class FormSerializer(serializers.ModelSerializer):

    class Meta:
        model=forumAnnouncements
        fields=('id','title','content','poster_image','thumbnail_poster_image','whatsapp_link','publish_date','published_by','hashtags','button_link','button_name')

class FormGetSerializer(serializers.ModelSerializer):

    class Meta:
        model=forumAnnouncements
        fields=('id','title','content','poster_image_url','thumbnail_poster_image_url','whatsapp_link','publish_date','published_by','hashtags','button_link','button_name')

