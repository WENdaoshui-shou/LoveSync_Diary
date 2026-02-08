import os
import json
import uuid
import logging
from django.http import JsonResponse
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.utils import timezone
from openai import OpenAI, APIError, AuthenticationError, RateLimitError
import time
from .PROMPT import *
from .models import *
import configparser

# 阿里云百炼API配置
DASHSCOPE_API_KEY = os.environ.get('DASHSCOPE_API_KEY')
DASHSCOPE_BASE_URL = os.environ.get('DASHSCOPE_BASE_URL')
DASHSCOPE_MODEL = os.environ.get('DASHSCOPE_MODEL') 

# 会话配置
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 3600

# 日志配置
logger = logging.getLogger(__name__)

# 初始化客户端
try:
    client = OpenAI(
        api_key=DASHSCOPE_API_KEY,
        base_url=DASHSCOPE_BASE_URL,
    )
except Exception as e:
    logger.error(f"初始化智能体客户端失败: {str(e)}")
    client = None

# 社区智能体系统提示
SYSTEM_PROMPT = PROMPT


def lovesync_index(request):
    return render(request, 'lovesync-AI.html')


@csrf_exempt
def ChatInitView(request):
    """初始化社区智能体会话"""
    # 分支1：非POST请求 → 明确返回
    if request.method != 'POST':
        return JsonResponse({
            "success": False,
            "error": "仅支持POST方法"
        }, status=405)

    # 分支2：client未初始化 → 明确返回
    if not client:
        logger.error("初始化失败：智能体客户端未初始化")
        return JsonResponse({
            "success": False,
            "error": "智能体客户端未初始化"
        }, status=500)

    # 主逻辑：用try-except完全包裹，确保任何异常都有返回
    try:
        # 生成会话ID
        session_id = str(uuid.uuid4())
        logger.info(f"生成会话ID成功：{session_id}")

        # 初始化消息列表
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        logger.info(f"初始化消息列表成功，系统提示：{SYSTEM_PROMPT[:50]}...")

        # 调用AI响应（加固：即使内部抛异常，也强制返回None并捕获）
        try:
            initial_response = get_ai_response(messages)  
            logger.info(f"AI响应结果：{initial_response if initial_response else 'None'}")
        except Exception as ai_e:
            # 捕获get_ai_response内部的所有异常
            logger.error(f"调用AI失败：{str(ai_e)}")
            initial_response = None

        # 分支3：AI响应为空 → 明确返回
        if not initial_response:
            logger.error("初始化失败：AI返回空响应")
            return JsonResponse({
                "success": False,
                "error": "智能体初始化失败"
            }, status=500)

        # 数据库操作（单独捕获数据库异常）
        try:
            # 保存会话到数据库
            chat_session = ChatSession.objects.create(
                id=session_id,
                completed=False
            )
            # 保存系统提示
            ChatMessage.objects.create(
                session=chat_session,
                role="system",
                content=SYSTEM_PROMPT
            )
            # 保存初始回复
            ChatMessage.objects.create(
                session=chat_session,
                role="assistant",
                content=initial_response
            )
            logger.info("数据库保存成功")
        except Exception as db_e:
            logger.error(f"数据库保存失败：{str(db_e)}")
            # 数据库失败也返回明确的错误响应
            return JsonResponse({
                "success": False,
                "error": "数据库保存失败"
            }, status=500)

        # 缓存操作（单独捕获缓存异常）
        try:
            cache_key = f"community_chat_{session_id}"
            cache_data = {
                "messages": messages + [{"role": "assistant", "content": initial_response}], 
                "completed": False
            }
            cache.set(cache_key, cache_data, 3600)
            # 验证缓存
            if not cache.get(cache_key):
                raise Exception("缓存写入后读取为空")
            logger.info("缓存写入成功")
        except Exception as cache_e:
            logger.error(f"缓存保存失败：{str(cache_e)}")
            # 缓存失败仍返回成功（降级处理），或根据需求返回错误
            return JsonResponse({
                "success": True,
                "session_id": session_id,
                "response": initial_response,
                "completed": False,
                "warning": "缓存保存失败，会话仅在数据库中生效"
            })

        # 分支4：所有操作成功 → 明确返回
        logger.info(f"会话初始化成功，session_id={session_id}")
        return JsonResponse({
            "success": True,
            "session_id": session_id,
            "response": initial_response,
            "completed": False
        })

    # 分支5：主逻辑所有未捕获的异常 → 明确返回
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"社区智能体初始化失败: {str(e)}\n堆栈: {error_trace}")
        return JsonResponse({
            "success": False,
            "error": "初始化会话失败"
        }, status=500)

@csrf_exempt
def ChatMessageView(request):
    """处理社区智能体的聊天消息"""
    if request.method != 'POST':
        return JsonResponse({"success": False, "error": "仅支持POST方法"}, status=405)

    if not client:
        return JsonResponse({"success": False, "error": "智能体客户端未初始化"}, status=500)

    try:
        data = json.loads(request.body)
        if not data or "session_id" not in data or "message" not in data:
            return JsonResponse({"success": False, "error": "缺少必要参数"}, status=400)

        session_id = data["session_id"]
        user_message = data["message"]
        session_key = f"community_chat_{session_id}"
        session_data = cache.get(session_key)

        # 检查会话是否存在
        try:
            chat_session = ChatSession.objects.get(id=session_id)
        except ChatSession.DoesNotExist:
            return JsonResponse({"success": False, "error": "会话已过期"}, status=404)

        if not session_data:
            # 缓存失效时从数据库恢复
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            for msg in chat_session.messages.exclude(role="system"):
                messages.append({"role": msg.role, "content": msg.content})
            session_data = {"messages": messages, "completed": chat_session.completed}

        # 添加用户消息并保存到数据库
        session_data["messages"].append({"role": "user", "content": user_message})
        ChatMessage.objects.create(
            session=chat_session,
            role="user",
            content=user_message
        )

        # 获取智能体响应（调用正确的响应函数）
        assistant_response = get_ai_response(session_data["messages"])  # 修正：调用get_ai_response
        if not assistant_response:
            return JsonResponse({"success": False, "error": "智能体响应失败"}, status=500)

        # 添加智能体响应并保存
        session_data["messages"].append({"role": "assistant", "content": assistant_response})
        ChatMessage.objects.create(
            session=chat_session,
            role="assistant",
            content=assistant_response
        )

        # 更新缓存和数据库状态（修正时间工具）
        cache.set(session_key, session_data, 3600)
        chat_session.updated_at = timezone.now()  # 修正：使用django.utils.timezone
        chat_session.save()

        return JsonResponse({
            "success": True,
            "response": assistant_response,
            "completed": False
        })

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的JSON格式"}, status=400)
    except Exception as e:
        logger.error(f"社区消息处理失败: {str(e)}")
        return JsonResponse({
            "success": False,
            "error": "处理消息失败"
        }, status=500)


def get_ai_response(messages, max_retries=2):
    if not client:
        logger.error("客户端未初始化，无法调用智能体")
        return None

    retry_count = 0
    while retry_count < max_retries:
        try:
            completion = client.chat.completions.create(
                model=DASHSCOPE_MODEL,  # 已修正模型名称
                messages=messages,
                timeout=10
            )
            return completion.choices[0].message.content
        except AuthenticationError:
            logger.error("API密钥验证失败")
            return None
        except RateLimitError:
            logger.warning("触发速率限制，将重试")
            retry_count += 1
            if retry_count < max_retries:
                time.sleep(1 * retry_count)
            else:
                logger.error("达到最大重试次数")
                return None
        except APIError as e:
            logger.error(f"API调用错误: {str(e)}")
            retry_count += 1
            if retry_count < max_retries:
                time.sleep(1 * retry_count)
            else:
                return None
        except Exception as e:
            logger.error(f"调用智能体时发生意外错误: {str(e)}")
            return None
