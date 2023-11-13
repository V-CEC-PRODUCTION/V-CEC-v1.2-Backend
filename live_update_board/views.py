from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import TeamScore, TeamItems
from .serializers import TeamScoreSerializer, TeamItemSerializer
from django.shortcuts import render
from live_update_board.tasks import RealTimeTask
class TeamScoreList(APIView):
    def get(self, request):
        RealTimeTask.delay()
        team_scores = TeamScore.objects.all()
        serializer = TeamScoreSerializer(team_scores, many=True)
        return Response({"team_score_result":serializer.data}, status=status.HTTP_200_OK)
    
    def put(self, request):
        
        try:
            team_instance = TeamScore.objects.get(id=request.data['id'])
            team_instance.score = request.data['score']
            team_instance.team = request.data['team']
            team_instance.save()
            

            return Response({"message": "Updated successfully"}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            print(f"Error in put: {e}")
            return Response({"message": "Error in put"}, status=status.HTTP_400_BAD_REQUEST)

class TeamItemList(APIView):
    def get(self, request):
        RealTimeTask.delay()
        team_name = request.query_params.get('team_name')
        
        team_name = team_name.upper()
        
        team_items = TeamItems.objects.filter(team=team_name).all()
        
        serializer = TeamItemSerializer(team_items, many=True)
        
        return Response({"team_item_result":serializer.data}, status=status.HTTP_200_OK)
        
        
    
    def put(self, request):
        
        try:
            team_instance = TeamScore.objects.get(id=request.data['id'])
            team_instance.score = request.data['score']
            team_instance.team = request.data['team']
            team_instance.save()
            

            return Response({"message": "Updated successfully"}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            print(f"Error in put: {e}")
            return Response({"message": "Error in put"}, status=status.HTTP_400_BAD_REQUEST)
        
def scores(request):
    return render(request, 'scores.html')

def pusher_front(request):
    return render(request, 'index.html')