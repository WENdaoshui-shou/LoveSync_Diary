from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .ot import transform_operations


class CollaborationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            await self.accept()
            self.room_name = self.scope['url_route']['kwargs'].get('document_id', 'new')
            await self.channel_layer.group_add(
                self.room_name,
                self.channel_name
            )
            print("WebSocket 握手成功")
        except Exception as e:
            print(f"连接失败：{str(e)}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )
        print(f"连接关闭，代码：{close_code}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            print("还原后的汉字:", data.get('text'))  # 应输出 "好"
            user_id = data.get('user_id')
            if not user_id:
                print("客户端消息缺少 user_id，忽略处理")
                return

            server_ops = []
            transformed_ops = transform_operations([data], server_ops)
            if transformed_ops:
                data = transformed_ops[0]
                data['user_id'] = user_id
                await self.channel_layer.group_send(
                    self.room_name,
                    {
                        'type': 'operation.message',
                        'data': data
                    }
                )
        except Exception as e:
            print(f"处理消息出错：{str(e)}")

    async def operation_message(self, event):
        data = event['data']
        # 打印要发送的内容和目标房间
        print(f"准备发送消息到房间 {self.room_name}: {data}")
        try:
            await self.send(text_data=json.dumps(data))
            print("消息发送成功")  # 确认发送操作完成
        except Exception as e:
            print(f"消息发送失败: {str(e)}")  # 捕获发送时的错误
