import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from users.models import User, Token
from users.utils import TokenUtil
from .models import TimeTable
import datetime
from channels.layers import get_channel_layer
from django.dispatch import receiver
from django.db.models.signals import post_save
from asgiref.sync import async_to_sync

class TimeTableConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.access_token = None
        self.user_semeseter = None  
        self.user_division = None
        self.current_day_datetime = datetime.date.today().weekday() + 1
        
    @receiver(post_save, sender=TimeTable)
    def cur_subject_and_time_changed(sender, instance, **kwargs):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"timetable_cec",
            {
                "type": "update_message",
                "id": instance.id,
                "current_code": instance.currentcode,
                "current_time": instance.currenttime,
                
            }
        )
        
    async def send_error_message(self, error_message):
        # Send an error message to the client
        await self.send(text_data=json.dumps({
            'error': error_message
        }))
        
    async def connect(self):
        # Extract access token from the query parameters
        query_string = self.scope.get("query_string", b"").decode("utf-8")
        print(query_string)
        query_params = query_string.split("&")

        for param in query_params:
            key, value = param.split("=")
            if key == "access_token":
                self.access_token = value
                
        token_key = await database_sync_to_async(Token.objects.get)(access_token=self.access_token)
        
        if not token_key:
            await self.send_error_message("Invalid access token")
            await self.close()

        payload = await database_sync_to_async(TokenUtil.decode_token)(token_key.access_token)

        # Optionally, you can extract user information or other claims from the payload
        if not payload:
            await self.send_error_message("Invalid access token")
            await self.close()

        # Check if the refresh token is associated with a user (add your logic here)
        user_id = await database_sync_to_async(payload.get)('id')
    
        if not user_id:
            await self.send_error_message("Access Token not associated with any user")
            await self.close()

        user_instance = await database_sync_to_async(User.objects.get)(id=user_id)
        
        if not user_instance:
            await self.send_error_message("User not found")
            await self.close()
        
        self.user_semester = user_instance.semester
        self.user_division = user_instance.division
        
        
        if self.current_day_datetime in [6, 7]:
            self.current_day_datetime = 5
        
        timetable_instance = await database_sync_to_async(TimeTable.objects.get)(semester=self.user_semester[1:], division=self.user_division, day=self.current_day_datetime)
        
        print(timetable_instance.currentcode, timetable_instance.currenttime)
        
        self.room_group_name = f"timetable_cec"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        print("Room Group Name:", self.room_group_name)

        # Accept the connection
        await self.accept()
        
        await self.send(text_data=json.dumps({
            "id": timetable_instance.id,
            "current_code": timetable_instance.currentcode,
            "current_time": timetable_instance.currenttime,
        }))
        
            
    async def update_message(self, event):

        current_realtime_msg = {
            "id": event['id'],
            "current_code": event['current_code'],
            "current_time": event['current_time'],
        }

        # Send the received message to the WebSocket
        await self.send(text_data=json.dumps(current_realtime_msg))
        
    async def disconnect(self, code):
        # Handle disconnect
        pass