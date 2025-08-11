from channels.generic.websocket import AsyncWebsocketConsumer
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
            data = eval(text_data)
            # 模拟服务器操作序列，实际应从数据库获取
            server_ops = []
            # 转换客户端操作
            transformed_ops = transform_operations([data], server_ops)
            if transformed_ops:
                data = transformed_ops[0]
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
        await self.send(text_data=str(data))
