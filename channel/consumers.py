import ujson as json
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import AnonymousUser


class LikeCountConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"like_count_{self.room_name}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        # if not self.scope.get('user') == AnonymousUser():
        #     await self.accept()
        # else:
        #     await self.disconnect(1007)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        return await super().disconnect(code)

    async def receive(self, text_data=None, bytes_data=None):
        pass
        # try:
        #     await self.channel_layer.group_send(
        #     self.room_group_name,
        #         {
        #             "type": "like.count",
        #             "likes": f'{text_data}'
        #         }
        #     )
        # except Exception as e:
        #     print(e)
            # await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
            # return await super().disconnect(1007)


    async def like_count(self, event):
        await self.send(text_data=json.dumps({"likes": event["likes"]}))



# class SimpleConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.accept()
#         await self.send(text_data=json.dumps({"message": "Connected successfully"}))

#     async def disconnect(self, code):
#         print("WebSocket disconnected")

#     async def receive(self, text_data=None, bytes_data=None):
#         await self.send(text_data=json.dumps({"message": text_data or "No message"}))