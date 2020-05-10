from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

class Tuisong(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'push'
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
 
    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
 
    # 主动推送
    def push_song(self, event):
        ggg = event['msg']
        self.send(text_data= json.dumps({
            'msg': ggg
        }))