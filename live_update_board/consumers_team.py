from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import TeamScore, TeamItems
from asgiref.sync import sync_to_async
from django.db import transaction
from django.db.models import F, FloatField
from django.db.models.functions import Cast
from channels.layers import get_channel_layer
from .consumers import RealTimeConsumer
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from asgiref.sync import async_to_sync



class TeamRealTimeConsumer(AsyncWebsocketConsumer):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  
        self.messages = {}
    
    @receiver(post_save, sender=TeamItems)
    def team_score_changed(sender, instance, **kwargs):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"{str.lower(instance.team)}-score-realtime-data",
            {
                "type": "update_message",
                "item": instance.item,
                "points": instance.points,
                "team": instance.team,
                "item_id": instance.item_id,
                
            }
        )
        
    @receiver(post_delete, sender=TeamItems)
    def team_score_changed_delete(self,sender, instance, **kwargs):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "update_message",
                "item": instance.item,
                "points": instance.points,
                "team": instance.team,
                "item_id": instance.item_id,
            }
        )     
    @sync_to_async
    def get_previous_messages(self):
        # Retrieve previous messages from the database
        previous_messages = TeamItems.objects.filter(team=str.upper(self.team_color)).order_by('-uploaded_at')
        return list(previous_messages.values('id','team', 'item', 'points','item_id'))
    

    
    @sync_to_async
    def create_team_items(self, item,points):
        TeamItems.objects.create( team=str.upper(self.team_color),item=item,points=points)
        
    @sync_to_async   
    def update_team_score(self, message_id, points, items):
        message = TeamItems.objects.get(id=message_id)
        message.points = points
        message.items = items
        message.save()
        
    @sync_to_async   
    def update_realtime_team_score_board(self, points):
        team_score = TeamScore.objects.get(team=str.upper(self.team_color))
        
        total_score = int(team_score.score) + int(points)
        team_score.score = total_score
        team_score.save()
        
        self.send_update_team_score(str.upper(self.team_color))
     
    async def connect(self):
        try:
            self.team_color = self.scope['url_route']['kwargs']['color']  
            self.room_group_name = f'{self.team_color}-score-realtime-data'

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
            
            previous_messages = await self.get_previous_messages()
            for message in previous_messages:
                self.messages[message['item_id']] = message
                
                await self.send(text_data=json.dumps({
                    "item": message['item'],
                    "points": message['points'],
                    "item_id": message['item_id'],   
                }))
            
        except Exception as e:
            print(f"Error in connect: {e}")


    async def disconnect(self, close_code):
        if self.room_group_name:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

            messages = getattr(self, 'messages', [])
            if messages:
                await self.create_team_items(messages[0]['item'], messages[0]['points'])
                
    async def update_message(self, event):
        points = event['points']
        item = event['item']
        item_id = event['item_id']
        

        self.messages[item_id] = {
            "item": item,
            "points": points,
            "item_id": item_id,
        }
        # Send the received message to the WebSocket
        await self.send(text_data=json.dumps(self.messages[item_id]))
        
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        item = text_data_json.get('item')
        points = text_data_json.get('points')
        item_id = text_data_json.get('item_id')
        
        
        self.messages.append({
            "item": item,
            "points": points,
            "item_id": item_id,
        })

        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "sendMessage",
                "item": item,
                "points": points,
                "item_id": item_id,
            })

    async def sendMessage(self, event):
        item = event.get('item')
        points = event.get('points')
        item_id = event.get('item_id')
        
        await self.update_realtime_team_score_board(points)
        
        await self.send(text_data=json.dumps({
            "item": item,
            "points": points,
            "item_id": item_id,
        }))
        
        

    