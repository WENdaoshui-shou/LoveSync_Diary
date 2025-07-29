# -*- coding: utf-8 -*-
# @Time        :2025/7/29 10:41
# @Author      :文刀水寿
# @File        : consumers.py.py
"""
 @Description :
"""
import json
import threading
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .ot import Operation, transform, transform_operations
from .models import CollaborativeDocument, DocumentOperation


class CollaborationConsumer(AsyncWebsocketConsumer):
    document_locks = {}  # 文档锁，用于并发控制
    document_operations = {}  # 文档操作缓存

    async def connect(self):
        self.document_id = self.scope['url_route']['kwargs']['document_id']
        self.group_name = f'document_{self.document_id}'

        if self.document_id not in self.document_locks:
            self.document_locks[self.document_id] = threading.Lock()

        # 加入群组
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # 离开群组
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        user_id = self.scope["user"].id
        operation = Operation(
            op_type=data['op_type'],
            position=data['position'],
            text=data.get('text', '')
        )
        client_revision = data.get('revision', 0)

        # 原子操作：处理操作并保存到数据库
        async with sync_to_async(self.document_locks[self.document_id].acquire)():
            try:
                # 获取文档和最新操作
                document = await sync_to_async(CollaborativeDocument.objects.get)(id=self.document_id)
                server_operations = await sync_to_async(list)(
                    DocumentOperation.objects.filter(
                        document=document,
                        revision__gt=client_revision
                    ).order_by('timestamp')
                )

                # 应用操作转换
                transformed_ops = transform_operations([operation], [op.to_operation() for op in server_operations])
                if not transformed_ops:
                    return  # 操作被完全转换掉，无需执行

                # 应用操作到文档
                transformed_op = transformed_ops[0]
                new_content = apply_operation(document.content, transformed_op)

                # 保存操作到数据库
                new_revision = document.documentoperation_set.count() + 1
                await sync_to_async(DocumentOperation.objects.create)(
                    document=document,
                    user_id=user_id,
                    operation_type=transformed_op.op_type,
                    position=transformed_op.position,
                    text=transformed_op.text,
                    revision=new_revision
                )

                # 更新文档内容
                document.content = new_content
                await sync_to_async(document.save)()

                # 广播到所有客户端
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'document_operation',
                        'operation': {
                            'user_id': user_id,
                            'op_type': transformed_op.op_type,
                            'position': transformed_op.position,
                            'text': transformed_op.text,
                            'revision': new_revision
                        }
                    }
                )
            finally:
                self.document_locks[self.document_id].release()

    async def document_operation(self, event):
        """处理接收到的操作并更新编辑器"""
        await self.send(text_data=json.dumps(event['operation']))


def apply_operation(content, operation):
    """将操作应用到文档内容"""
    if operation.op_type == 'insert':
        return content[:operation.position] + operation.text + content[operation.position:]
    elif operation.op_type == 'delete':
        return content[:operation.position] + content[operation.position + len(operation.text):]
    return content
