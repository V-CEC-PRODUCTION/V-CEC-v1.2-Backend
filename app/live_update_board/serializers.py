from rest_framework import serializers
from .models import TeamScore, TeamItems

class TeamScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamScore
        fields = ('id','score', 'team')
        
class TeamItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamItems
        fields = ('item_id','item', 'points')