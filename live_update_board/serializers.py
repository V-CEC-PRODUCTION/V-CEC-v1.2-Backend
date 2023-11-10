from rest_framework import serializers
from .models import TeamScore

class TeamScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamScore
        fields = ('score', 'team')