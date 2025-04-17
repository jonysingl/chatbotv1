from typing import List, Optional, Dict, Any
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q
from datetime import datetime

from app.models.orm.chat import Message, Conversation
from app.models.orm.chat import Message_Pydantic, MessageIn_Pydantic
from app.services.conversation_service import update_conversation_last_message_time


async def create_message_question(conversation_id: int, question: str) -> Message:
    """
    创建新消息，仅包含用户问题

    Args:
        conversation_id: 会话ID
        question: 用户问题内容

    Returns:
        新创建的消息对象
    """
    message = await Message.create(
        conversation_id=conversation_id,
        question=question
    )

    # 更新会话最后消息时间
    await update_conversation_last_message_time(conversation_id)

    return message


async def update_message_answer(message_id: int, answer: str, tokens_used: int = 0) -> Optional[Message]:
    """
    更新消息，添加AI回答和使用的tokens数量

    Args:
        message_id: 消息ID
        answer: AI回答内容
        tokens_used: 使用的tokens数量

    Returns:
        更新后的消息对象，如不存在则返回None
    """
    try:
        message = await Message.get(message_id=message_id)
        message.answer = answer
        message.tokens_used = tokens_used
        await message.save(update_fields=['answer', 'tokens_used', 'updated_at'])

        # 更新会话最后消息时间
        await update_conversation_last_message_time(message.conversation_id)

        return message
    except DoesNotExist:
        return None


async def get_message(message_id: int) -> Optional[Message]:
    """
    通过ID获取消息

    Args:
        message_id: 消息ID

    Returns:
        消息对象，如不存在则返回None
    """
    try:
        return await Message.get(message_id=message_id)
    except DoesNotExist:
        return None


async def get_conversation_messages(
        conversation_id: int,
        skip: int = 0,
        limit: int = 100
) -> List[Message]:
    """
    获取会话中的所有消息，按创建时间正序排列

    Args:
        conversation_id: 会话ID
        skip: 跳过的记录数
        limit: 返回的最大记录数

    Returns:
        消息对象列表
    """
    return await Message.filter(conversation_id=conversation_id) \
        .order_by("created_at") \
        .offset(skip) \
        .limit(limit)


async def create_complete_message(
        conversation_id: int,
        question: str,
        answer: str,
        tokens_used: int = 0
) -> Message:
    """
    创建包含问题和回答的完整消息

    Args:
        conversation_id: 会话ID
        question: 用户问题内容
        answer: AI回答内容
        tokens_used: 使用的tokens数量

    Returns:
        新创建的消息对象
    """
    message = await Message.create(
        conversation_id=conversation_id,
        question=question,
        answer=answer,
        tokens_used=tokens_used
    )

    # 更新会话最后消息时间
    await update_conversation_last_message_time(conversation_id)

    return message


async def delete_message(message_id: int) -> bool:
    """
    删除单条消息

    Args:
        message_id: 消息ID

    Returns:
        True表示删除成功，False表示消息不存在
    """
    try:
        message = await Message.get(message_id=message_id)
        await message.delete()
        return True
    except DoesNotExist:
        return False


async def get_recent_messages_for_context(conversation_id: int, limit: int = 10) -> List[Message]:
    """
    获取会话中最近的N条消息用于上下文

    Args:
        conversation_id: 会话ID
        limit: 返回的最大记录数

    Returns:
        最近的消息对象列表，按时间正序
    """
    messages = await Message.filter(conversation_id=conversation_id) \
        .order_by("-created_at") \
        .limit(limit)

    # 反转顺序，使其按时间正序
    return list(reversed(messages))


async def count_conversation_tokens(conversation_id: int) -> int:
    """
    统计会话中所有消息消耗的tokens总数

    Args:
        conversation_id: 会话ID

    Returns:
        tokens总数
    """
    messages = await Message.filter(conversation_id=conversation_id)
    return sum(message.tokens_used or 0 for message in messages)