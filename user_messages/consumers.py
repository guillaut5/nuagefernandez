import json
from channels.generic.websocket import AsyncWebsocketConsumer


class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("messages_group", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("messages_group", self.channel_name)

    async def receive(self, text_data):
        # (Pas utilisé ici)
        pass

    async def new_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))
