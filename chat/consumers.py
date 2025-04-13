from chat.models import Chat, Room
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async, async_to_sync


"""MESSAGE DB ENTRY"""
@sync_to_async
def create_new_message(me, friend, message, room_id):
    try:
        get_room = Room.objects.filter(room_id=room_id)
        if not get_room.exists():
            print(f"Room with ID {room_id} not found")
            return False
            
        get_room = get_room[0]
        author_user = User.objects.get(username=me)
        friend_user = User.objects.get(username=friend)
        
        new_chat = Chat.objects.create(
            author=author_user,
            friend=friend_user,
            room_id=get_room,
            text=message)
        return True
    except Exception as e:
        print(f"Error creating message: {str(e)}")
        return False
        

class ChatRoomConsumer(AsyncWebsocketConsumer):

    """Connect"""
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    """Disconnect"""
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    """Receive"""
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            username = text_data_json['username']
            user_image = text_data_json['user_image']

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chatroom_message',
                    'message': message,
                    'username': username,
                    'user_image': user_image,
                }
            )
        except Exception as e:
            print(f"Error processing message: {str(e)}")


    """Messages"""
    async def chatroom_message(self, event):
        try:
            message = event['message']
            username = event['username']
            user_image = event['user_image']

            try:
                await create_new_message(me=self.scope["user"], friend=username, message=message, room_id=self.room_name)
            except Exception as db_error:
                print(f"Database error: {str(db_error)}")
            
            await self.send(text_data=json.dumps({
                'message': message,
                'username': username,
                'user_image': user_image,
            }))
        except Exception as e:
            print(f"Error sending message: {str(e)}")

