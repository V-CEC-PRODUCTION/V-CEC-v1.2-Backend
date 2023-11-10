from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import TeamScore
from .serializers import TeamScoreSerializer
from django.shortcuts import render

class TeamScoreList(APIView):
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