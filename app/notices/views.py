from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.cache import cache
from .tasks import ktu_web_scrap_announcement
import json

# get scraped data
@api_view(['GET'])
def ktu_announcements_scrap(request):
    try:
        ktu_result = "ktu_web_scrap"
        
        web_scrap_result = cache.get(ktu_result)
        
        # web_scrap_result = None
        
        if web_scrap_result is None:
            print("Data from web")
            web_scrap_result = ktu_web_scrap_announcement()
            cache.set(ktu_result, json.dumps(web_scrap_result),timeout=60*60*24*7)
        else:
            print("Data from cache")
            web_scrap_result = json.loads(web_scrap_result)
       
        return Response({'notices_result': web_scrap_result})
    except Exception as e:
        return Response({'error': str(e)}, status=500)