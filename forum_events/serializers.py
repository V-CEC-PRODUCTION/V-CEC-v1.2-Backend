from rest_framework import serializers
from .models import forumEvents

class FormSerializer(serializers.ModelSerializer):

    class Meta:
        model=forumEvents
        fields=('id','title','content','poster_image','thumbnail_poster_image','register_button_link','whatsapp_link','status','publish_date','published_by','hashtags')




