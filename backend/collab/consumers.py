import json
import uuid
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from core.models import User, Profile
from .models import CollaborativeDocument, DocumentOperation
from .ot_engine import OTEngine, Insert, Delete

# 配置项（集中管理，便于修改）
MAX_MESSAGE_SIZE = 1024 * 10  # 10KB
HEARTBEAT_INTERVAL = 30
SUPPORTED_OP_TYPES = ['insert', 'delete']


class DiarySyncConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """建立WebSocket连接（适配CollaborativeDocument模型）"""
        self.user = self.scope['user']
        self.room_name = None
        self.document = None  # 协作文档对象
        self.heartbeat_timer = None

        # 1. 校验用户登录状态
        if not self.user.is_authenticated:
            await self.close(code=4001)  # 未认证
            return

        try:
            # 2. 获取用户情侣信息 + 协作文档
            @database_sync_to_async
            def get_couple_and_document():
                """获取情侣ID和对应的协作文档"""
                try:
                    # 获取用户profile和情侣ID
                    user_profile = Profile.objects.get(user=self.user)
                    if not user_profile.couple:
                        return None, None

                    couple_profile = user_profile.couple
                    couple_user = couple_profile.user

                    # 生成唯一房间名（排序确保情侣双方房间名一致）
                    user_ids = sorted([self.user.id, couple_user.id])
                    room_name = f'diary_{user_ids[0]}_{user_ids[1]}'

                    # 每次连接都创建新的协作文档，确保每次都是新的日记
                    # 逻辑：情侣双方共享一个新文档，owner为创建者
                    document = CollaborativeDocument.objects.create(
                        title=f'情侣日记_{user_ids[0]}_{user_ids[1]}_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                        content='',
                        owner=self.user,
                        couple=user_profile
                    )
                    return room_name, document

                except ObjectDoesNotExist as e:
                    print(f'未找到用户/profile: {e}')
                    return None, None
                except Exception as e:
                    print(f'获取情侣/文档失败: {e}')
                    return None, None

            # 执行数据库操作
            self.room_name, self.document = await get_couple_and_document()
            if not self.room_name or not self.document:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'code': 4002,
                    'message': '未找到情侣关系或无法创建协作文档'
                }))
                await self.close(code=4002)
                return

            # 3. 初始化核心状态（从数据库加载）
            self.document_content = self.document.content
            # 获取最新版本号（取操作历史的最大revision，无则为0）
            self.current_revision = await self._get_latest_revision()
            self.collaborative_status = False

            # 4. 接受连接（校验通过后）
            await self.accept()

            # 5. 加入房间
            await self.channel_layer.group_add(self.room_name, self.channel_name)

            # 6. 启动心跳检测
            await self._start_heartbeat()

            # 7. 发送连接成功消息
            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'message': '协作连接已建立',
                'user_id': self.user.id,
                'document_id': self.document.id,
                'revision': self.current_revision,
                'content': self.document_content,
                'title': self.document.title,
                'room_name': self.room_name
            }))

        except Exception as e:
            error_msg = f'连接失败: {str(e)}'
            print(error_msg)
            await self.send(text_data=json.dumps({
                'type': 'error',
                'code': 5001,
                'message': error_msg
            }))
            await self.close(code=5001)

    async def disconnect(self, close_code):
        """断开连接（清理资源+持久化）"""
        # 1. 停止心跳
        if self.heartbeat_timer:
            self.heartbeat_timer.cancel()

        # 2. 退出房间
        if self.room_name:
            try:
                await self.channel_layer.group_discard(self.room_name, self.channel_name)
            except Exception as e:
                print(f'退出房间失败: {e}')

        # 3. 持久化最终文档内容
        if self.document:
            await self._persist_document_content()

        print(f'用户 {self.user.id} 断开连接 | 文档ID: {self.document.id if self.document else "None"} | 关闭码: {close_code}')

    async def receive(self, text_data):
        """处理客户端消息（适配模型+增强校验）"""
        # 1. 消息大小限制
        if len(text_data) > MAX_MESSAGE_SIZE:
            await self._send_error(4003, '消息大小超出限制（最大10KB）')
            return

        try:
            # 2. 解析JSON
            data = json.loads(text_data)
            msg_type = data.get('type')

            # 3. 处理不同类型消息
            handlers = {
                'heartbeat': self._handle_heartbeat,
                'collaborative_status': self._handle_collaborative_status,
                'ot_operation': self._handle_ot_operation,
                'document_sync': self._handle_document_sync,
                'update_title': self._handle_update_title  # 新增：更新标题
            }

            if msg_type in handlers:
                await handlers[msg_type](data)
            else:
                await self._send_error(4004, f'不支持的消息类型: {msg_type}')

        except json.JSONDecodeError:
            await self._send_error(4005, '无效的JSON格式')
        except Exception as e:
            await self._send_error(5002, f'消息处理失败: {str(e)}')

    # ========== 消息处理子方法 ==========
    async def _handle_heartbeat(self, data):
        """处理心跳检测"""
        await self.send(text_data=json.dumps({
            'type': 'heartbeat',
            'timestamp': datetime.now().timestamp(),
            'revision': self.current_revision
        }))

    async def _handle_collaborative_status(self, data):
        """处理协作状态同步"""
        self.collaborative_status = data.get('status', False)
        # 广播状态给情侣
        await self.channel_layer.group_send(self.room_name, {
            'type': 'broadcast_collaborative_status',
            'status': self.collaborative_status,
            'user_id': self.user.id,
            'timestamp': datetime.now().timestamp()
        })

    async def _handle_document_sync(self, data):
        """处理全量文档同步请求"""
        # 重新从数据库加载最新内容（防止内存状态不一致）
        await self._refresh_document_from_db()
        await self.send(text_data=json.dumps({
            'type': 'document_sync_response',
            'document_id': self.document.id,
            'title': self.document.title,
            'content': self.document_content,
            'revision': self.current_revision,
            'last_updated': self.document.last_updated.timestamp()
        }))

    async def _handle_update_title(self, data):
        """处理标题更新"""
        new_title = data.get('title', '').strip()
        if not new_title:
            await self._send_error(4008, '标题不能为空')
            return

        # 更新数据库
        @database_sync_to_async
        def update_title():
            self.document.title = new_title
            self.document.save()
            return new_title

        try:
            updated_title = await update_title()
            # 广播标题更新
            await self.channel_layer.group_send(self.room_name, {
                'type': 'broadcast_title_update',
                'document_id': self.document.id,
                'title': updated_title,
                'user_id': self.user.id
            })
            # 响应客户端
            await self.send(text_data=json.dumps({
                'type': 'title_updated',
                'status': 'success',
                'title': updated_title
            }))
        except Exception as e:
            await self._send_error(5003, f'更新标题失败: {str(e)}')

    async def _handle_ot_operation(self, data):
        """处理OT操作（核心：关联DocumentOperation模型）"""
        # 1. 提取参数
        op_data = data.get('operation', {})
        client_revision = int(data.get('revision', 0))
        op_id = data.get('operation_id', str(uuid.uuid4()))

        # 2. 校验版本一致性
        if client_revision != self.current_revision:
            await self._send_error(
                4006,
                f'版本冲突！当前最新版本: {self.current_revision}，客户端版本: {client_revision}',
                {'current_revision': self.current_revision, 'current_content': self.document_content}
            )
            return

        # 3. 校验操作类型
        op_type = op_data.get('type')
        if op_type not in SUPPORTED_OP_TYPES:
            await self._send_error(4007, f'不支持的操作类型: {op_type}（仅支持insert/delete）')
            return

        # 4. 构建OT操作对象
        try:
            if op_type == 'insert':
                position = int(op_data.get('position', 0))
                text = str(op_data.get('text', '')).strip()
                if not text:
                    raise ValidationError('插入文本不能为空')
                ot_operation = Insert(
                    position=position,
                    text=text
                )
            else:  # delete
                position = int(op_data.get('position', 0))
                length = int(op_data.get('length', 1))
                if length <= 0:
                    raise ValidationError('删除长度必须大于0')
                ot_operation = Delete(
                    position=position,
                    length=length
                )
        except (ValueError, TypeError, ValidationError) as e:
            await self._send_error(4009, f'操作参数非法: {str(e)}')
            return

        # 5. 应用操作到内存文档
        self.document_content = OTEngine.apply(
            ot_operation, self.document_content
        )

        # 6. 保存操作到数据库（DocumentOperation）
        new_revision = self.current_revision + 1
        op_saved = await self._save_operation_to_db(ot_operation, new_revision, op_id)
        if not op_saved:
            await self._send_error(5004, '保存操作历史失败')
            return

        # 7. 更新文档内容到数据库
        await self._persist_document_content()

        # 8. 更新内存状态
        self.current_revision = new_revision

        # 9. 广播操作给情侣
        await self.channel_layer.group_send(self.room_name, {
            'type': 'broadcast_ot_operation',
            'document_id': self.document.id,
            'operation': {
                'type': op_type,
                'position': ot_operation.position,
                'text': getattr(ot_operation, 'text', ''),
                'length': getattr(ot_operation, 'length', 0)
            },
            'user_id': self.user.id,
            'revision': new_revision,
            'operation_id': op_id
        })

        # 10. 响应客户端操作成功
        await self.send(text_data=json.dumps({
            'type': 'ot_operation_ack',
            'status': 'success',
            'operation_id': op_id,
            'new_revision': new_revision
        }))

    # ========== 数据库操作辅助方法 ==========
    @database_sync_to_async
    def _get_latest_revision(self):
        """获取文档的最新版本号"""
        try:
            latest_op = DocumentOperation.objects.filter(
                document=self.document
            ).order_by('-revision').first()
            return latest_op.revision if latest_op else 0
        except Exception:
            return 0

    @database_sync_to_async
    def _save_operation_to_db(self, ot_operation, revision, op_id):
        """保存操作到DocumentOperation模型"""
        try:
            # 确定操作类型
            operation_type = 'insert' if isinstance(ot_operation, Insert) else 'delete'
            
            DocumentOperation.objects.create(
                document=self.document,
                user=self.user,
                operation_type=operation_type,
                position=ot_operation.position,
                text=getattr(ot_operation, 'text', ''),
                revision=revision,
                # 可额外存储op_id用于幂等性
            )
            return True
        except Exception as e:
            print(f'保存操作失败: {e}')
            return False

    @database_sync_to_async
    def _persist_document_content(self):
        """持久化文档内容到数据库"""
        try:
            self.document.content = self.document_content
            self.document.save(update_fields=['content', 'last_updated'])
            return True
        except Exception as e:
            print(f'持久化文档失败: {e}')
            return False

    async def _refresh_document_from_db(self):
        """从数据库刷新文档状态（防止内存与数据库不一致）"""
        try:
            @database_sync_to_async
            def get_fresh_doc():
                return CollaborativeDocument.objects.get(id=self.document.id)
            
            fresh_doc = await get_fresh_doc()
            self.document = fresh_doc
            self.document_content = fresh_doc.content
            # 重新获取最新版本号
            self.current_revision = await self._get_latest_revision()
        except Exception as e:
            print(f'刷新文档失败: {e}')

    # ========== 工具方法 ==========
    async def _start_heartbeat(self):
        """启动心跳检测"""
        try:
            await self.send(text_data=json.dumps({
                'type': 'heartbeat',
                'timestamp': datetime.now().timestamp(),
                'revision': self.current_revision
            }))
            import asyncio
            loop = asyncio.get_event_loop()
            self.heartbeat_timer = loop.call_later(
                HEARTBEAT_INTERVAL,
                lambda: loop.create_task(self._start_heartbeat())
            )
        except Exception as e:
            print(f'心跳发送失败: {e}')

    async def _send_error(self, code, message, extra_data=None):
        """统一发送错误消息"""
        error_data = {
            'type': 'error',
            'code': code,
            'message': message
        }
        if extra_data:
            error_data.update(extra_data)
        await self.send(text_data=json.dumps(error_data))

    # ========== 房间广播处理方法 ==========
    async def broadcast_ot_operation(self, event):
        """转发OT操作给客户端（排除发送者）"""
        if event.get('user_id') == self.user.id:
            return
        await self.send(text_data=json.dumps({
            'type': 'ot_operation',
            'document_id': event['document_id'],
            'operation': event['operation'],
            'user_id': event['user_id'],
            'revision': event['revision'],
            'operation_id': event.get('operation_id')
        }))

    async def broadcast_collaborative_status(self, event):
        """转发协作状态（仅转发给对方用户）"""
        if event.get('user_id') == self.user.id:
            return
        await self.send(text_data=json.dumps({
            'type': 'collaborative_status',
            'status': event['status'],
            'user_id': event['user_id'],
            'timestamp': event['timestamp']
        }))

    async def broadcast_title_update(self, event):
        """转发标题更新"""
        await self.send(text_data=json.dumps({
            'type': 'title_updated',
            'document_id': event['document_id'],
            'title': event['title'],
            'user_id': event['user_id']
        }))