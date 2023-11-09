from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import TeamScore
from asgiref.sync import sync_to_async
from django.db import transaction
from django.db.models import F, FloatField
from django.db.models.functions import Cast
from channels.layers import get_channel_layer
from django.dispatch import receiver
from django.db.models.signals import post_save
from asgiref.sync import async_to_sync


class RealTimeConsumer(AsyncWebsocketConsumer):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  
        self.messages = {}
        
    @receiver(post_save, sender=TeamScore)
    def team_score_changed(sender, instance, **kwargs):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "core-realtime-data",
            {
                "type": "update_message",
                "id": instance.id,
                "score": instance.score,
                "team": instance.team,
                
            }
        )

        
    @sync_to_async
    def get_previous_messages(self):
        # Retrieve previous messages from the database
        previous_messages = TeamScore.objects.annotate(score_as_float=Cast(F('score'), FloatField())).order_by('-score_as_float')
        return list(previous_messages.values('id','score', 'team'))
    
    def create_team_score(self, score, team):
        TeamScore.objects.create(score=score, team=team)
        
    def update_team_score(self, message_id, score, team):
        message = TeamScore.objects.get(id=message_id)
        message.score = score
        message.team = team
        message.save()
    
    @sync_to_async   
    def get_channel_name(self):
        print(f"self.channel_name: {self.channel_name}")
        return self.channel_name
    
    async def connect(self):
        try:
            self.room_group_name = 'core-realtime-data'
            
            #self.channel_name = 'team_score_channel'
            print(f"self.channel_name: {self.channel_name}")
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
            
            previous_messages = await self.get_previous_messages()
            for message in previous_messages:
                
                self.messages[message['id']] = message
                
                await self.send(text_data=json.dumps({
                    'id': message['id'],
                    "score": message['score'],
                    "team": message['team'],
                }))
            
        except Exception as e:
            print(f"Error in connect: {e}")

    async def disconnect(self, close_code):
        # Leave room group
        if self.room_group_name:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action')

        if action == 'send_message':
            await self.handle_send_message(text_data_json)
        elif action == 'update_message':
            await self.handle_update_message(text_data_json)
        elif action == 'db_update':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'db_update',
                    'message': text_data_json['text'],
                }
            )
            
    async def update_message(self, event):
        team = event['team']
        score = event['score']
        team_id = event['id']
        
        if team_id in self.messages:
            self.messages[team_id]['score'] = score
        else:
            self.messages[team_id] = {
                'id': team_id,
                'score': score,
                'team': team,
            }
        # Send the received message to the WebSocket
        await self.send(text_data=json.dumps(self.messages[team_id]))
        


    async def send_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'id': message['id'],
            'score': message['score'],
            'team': message['team'],
        }))



