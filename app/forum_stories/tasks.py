from celery import shared_task
from datetime import timedelta
from .models import ForumStories, UserCountStories
from django.utils import timezone
import json
import pytz

@shared_task
def checkIfStoriesExpired():
    stories = ForumStories.objects.all()
    
    if stories:
        current_time = timezone.now()
        india_timezone = pytz.timezone('Asia/Kolkata')
        
        for story in stories:
            # Use the story's upload_time directly
            india_time = story.upload_time.astimezone(india_timezone)
            
            if india_time + timedelta(hours=2) < current_time:
                if story.media_file:
                    story.media_file.delete()
        
                if story.thumbnail_media_file:
                    story.thumbnail_media_file.delete()
                    
                user_stories_count = UserCountStories.objects.all()
                
                if user_stories_count:
                    for record in user_stories_count:
                        count_data = record.count
                        count_data = json.loads(count_data)
                        
                        if count_data[story.forum_tag] == 0:
                            continue
                        else:
                            count_data[story.forum_tag] -= 1
                        record.count = json.dumps(count_data)
                        record.save()       
                        
                story.delete()
                
                print("Story expired successfully...")
                
            else:
                print("Story not expired...")
                
    else:
        print("No stories found...")
           
                