import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ProjectBoardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.room_group_name = f'project_board_{self.project_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        # Send update to all members of group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'board_update_broadcast',
                'data': text_data_json
            }
        )

    async def board_update_broadcast(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event['data']))

    # Handlers for views broadcasting events:
    async def board_update(self, event):
        await self.send(text_data=json.dumps(event))

    async def task_created(self, event):
        await self.send(text_data=json.dumps(event))

    async def task_updated(self, event):
        await self.send(text_data=json.dumps(event))

    async def task_deleted(self, event):
        await self.send(text_data=json.dumps(event))


class TaskCommentsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.task_id = self.scope['url_route']['kwargs']['task_id']
        self.room_group_name = f'task_comments_{self.task_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        pass # Comments are handled via HTTP POST and broadcast from views.py

    async def new_comment(self, event):
        await self.send(text_data=json.dumps(event))


class UserNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_authenticated:
            self.user_id = self.scope["user"].id
            self.room_group_name = f'user_notifications_{self.user_id}'

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event))
