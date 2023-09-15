from rest_framework import serializers
from .models import TimeTable

class TimeTableSerializer(serializers.ModelSerializer):

    class Meta:
        model=TimeTable
        fields='__all__'

class TimeTableAdminSerializer(serializers.ModelSerializer):

    class Meta:
        model=TimeTable
        fields=['firstcode','secondcode','thirdcode','fourthcode','fifthcode','sixthcode','day','semester','division']

class TimeTableClientSerializer(serializers.ModelSerializer):

    class Meta:
        model=TimeTable
        fields=['firstcode','secondcode','thirdcode','fourthcode','fifthcode','sixthcode','firsttime','secondtime','thirdtime','fourthtime','fifthtime','sixthtime']

class TimeTableCurrentSerializer(serializers.ModelSerializer):

    class Meta:
        model=TimeTable
        fields=['currentcode', 'currenttime']
