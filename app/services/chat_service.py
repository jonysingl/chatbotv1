from typing import List, Dict, Any, Optional
from datetime import datetime

from app.models.orm.chat import Conversation, Message
from app.models.orm.chat import Conversation_Pydantic, Message_Pydantic
from app.services.conversation_service import create_conversation, get_conversation, \
    update_conversation_last_message_time
from app.services.message_service import create_message_question, update_message_answer, get_conversation_messages


async def process_chat_message(
        user_id: int,
        message_text: str,
        conversation_id: Optional[int] = None,
        model_type: str = "default"
) -> Dict[str, Any]:
    """
    处理聊天消息的综合函数，包括创建会话、保存消息、记录回复

    Args:
        user_id: 用户ID
        message_text: 用户消息文本
        conversation_id: 会话ID，如果是None则创建新会话
        model_type: 使用的模型类型

    Returns:
        包含处理结果的字典
    """
    # 1. 处理会话
    if conversation_id is None:
        # 创建新会话，使用消息内容前50个字符作为标题
        title = message_text[:50] + "..." if len(message_text) > 50 else message_text
        conversation = await create_conversation(user_id, model_type, title)
        conversation_id = conversation.conversation_id
    else:
        # 验证会话是否存在
        conversation = await get_conversation(conversation_id)
        if not conversation or conversation.user_id != user_id:
            return {
                "success": False,
                "error": "Conversation not found or access denied"
            }

    # 2. 保存用户消息
    message = await create_message_question(conversation_id, message_text)

    # 3. 这里将来会调用AI接口，现在仅返回操作成功的信息
    # 注意: 实际应用中，这里应该是调用AI API获取回复

    return {
        "success": True,
        "conversation_id": conversation_id,
        "message_id": message.message_id,
        "user_id": user_id,
        "needs_ai_response": True  # 标记需要AI响应
    }


async def save_ai_response(
        message_id: int,
        ai_response: str,
        tokens_used: int = 0
) -> Dict[str, Any]:
    """
    保存AI回复内容

    Args:
        message_id: 消息ID
        ai_response: AI回复内容
        tokens_used: 使用的tokens数量

    Returns:
        包含操作结果的字典
    """
    # 更新消息，添加AI回答
    updated_message = await update_message_answer(message_id, ai_response, tokens_used)

    if not updated_message:
        return {
            "success": False,
            "error": "Message not found"
        }

    return {
        "success": True,
        "message_id": updated_message.message_id,
        "conversation_id": updated_message.conversation_id,
        "tokens_used": tokens_used
    }


async def get_chat_history(
        user_id: int,
        conversation_id: int,
        limit: int = 50
) -> Dict[str, Any]:
    """
    获取特定会话的聊天历史记录

    Args:
        user_id: 用户ID
        conversation_id: 会话ID
        limit: 返回的最大消息数

    Returns:
        包含会话信息和消息列表的字典
    """
    # 验证会话是否存在且属于当前用户
    conversation = await get_conversation(conversation_id)
    if not conversation or conversation.user_id != user_id:
        return {
            "success": False,
            "error": "Conversation not found or access denied"
        }

    # 获取会话中的消息
    messages = await get_conversation_messages(conversation_id, limit=limit)

    # 序列化数据
    conversation_data = await Conversation_Pydantic.from_tortoise_orm(conversation)
    messages_data = await Message_Pydantic.from_queryset(
        Message.filter(conversation_id=conversation_id).order_by("created_at").limit(limit))

    return {
        "success": True,
        "conversation": conversation_data.dict(),
        "messages": [msg.dict() for msg in messages_data]
    }