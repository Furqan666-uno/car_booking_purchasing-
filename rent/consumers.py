import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Conversation, Message
from django.utils import timezone
from django.contrib.auth import get_user_model

User= get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name= self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name= f'chat_{self.room_name}'

        conversation= await self.get_conversation()
        user= self.scope["user"] # basically, request.user
        if not user.is_authenticated:
            await self.close()
            return
        if conversation is None:
            await self.close()
            return
        if conversation.buyer != user and conversation.seller != user:
            await self.close()
            return
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept() # to accept connection after authentication
        await self.set_online(user.id)
        await self.mark_read(self.room_name, user.id)
        await self.channel_layer.group_send(self.room_group_name, {'type':'user_online', 'username':user.username})
        await self.channel_layer.group_send(self.room_group_name, {'type':'message_seen', 'username':user.username})
        # group_send() actually sends the event to redis, then it delivers to every connected websocket in that room.

    async def receive(self, text_data):
        user= self.scope['user']
        data= json.loads(text_data) # converts entire sent data to json
        message= data['message'] # extract only message part from json data
        if not message:
            return
        saved_message= await self.save_message(conversation_id=self.room_name, sender_id=user.id, text=message)
        await self.channel_layer.group_send(self.room_group_name, {'type':'chat_message', 'message_id':saved_message['id'], 'sender':saved_message['sender'], 'created_at':saved_message['created_at'], 'text':saved_message['text'], 'image':saved_message['image'], 'file':saved_message['file']})
        

    async def disconnect(self, close_code):
        user= self.scope['user']
        if user.is_authenticated:
            await self.set_offline(user.id)
            await self.channel_layer.group_send(self.room_group_name, {'type':'user_offline', 'username':user.username})
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name) # remove connection
    
    # these will show required json data on screen 
    async def user_online(self, event):
        await self.send(text_data=json.dumps({'type':'online', 'username':event['username']}))

    async def user_offline(self, event):
        await self.send(text_data=json.dumps({'type':'offline', 'username':event['username']}))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({'type':'message', 'message':event['message'], 'sender':event['sender'], 'created_at':event['created_at'], 'text':event['text'], 'image':event['image'], 'file':event['file']}))

    async def message_seen(self, event):
        await self.send(text_data=json.dumps({'type':'seen', 'username':event['username']})) 

    # operations like getting id's can't be done directly in websocket, so we have to do it sepeartely here.
    @database_sync_to_async
    def save_message(self, text, conversation_id, sender_id):
        conversation= Conversation.objects.get(id=conversation_id)
        sender= User.objects.get(id=sender_id)
        message= Message.objects.create(sender=sender, text=text, conversation=conversation)
        return ({'id':str(message.id), 'sender':sender.username, 'text':message.text, 'created_at':message.created_at.isoformat(), 'image': message.image.url if message.image else None, 'file': message.file.url if message.file else None})

    @database_sync_to_async
    def mark_read(self, conversation_id, user_id):
        Message.objects.filter(conversation_id=conversation_id).exclude(sender_id=user_id).update(is_read=True)

    @database_sync_to_async
    def set_online(self, user_id):
        User.objects.filter(id=user_id).update(is_online=True)

    @database_sync_to_async
    def set_offline(self, user_id):
        User.objects.filter(id=user_id).update(is_online=False)

    @database_sync_to_async
    def get_conversation(self):
        conversation_id= self.scope['url_route']['kwargs']['conversation_id']
        try:
            return Conversation.objects.get(id=conversation_id)  
        except Conversation.DoesNotExist:
            return None