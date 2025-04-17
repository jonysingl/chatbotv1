from typing import List, Optional, Dict, Any
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q
from tortoise.functions import Count
from datetime import datetime

from app.models.orm.chat import Conversation, Message
from app.models.orm.chat import Conversation_Pydantic, ConversationIn_Pydantic


async def create_conversation(user_id: int, model_type: str, title: Optional[str] = None) -> Conversation:
    """
    创建新会话

    Args:
        user_id: 用户ID
        model_type: 模型类型
        title: 会话标题，可选

    Returns:
        新创建的会话对象
    """
    now = datetime.now()
    conversation = await Conversation.create(
        user_id=user_id,
        title=title,
        model_type=model_type,
        last_message_at=now
    )
    return conversation


async def get_conversation(conversation_id: int) -> Optional[Conversation]:
    """
    通过ID获取会话

    Args:
        conversation_id: 会话ID

    Returns:
        会话对象，如不存在则返回None
    """
    try:
        return await Conversation.get(conversation_id=conversation_id)
    except DoesNotExist:
        return None


async def get_user_conversations(user_id: int, skip: int = 0, limit: int = 100) -> List[Conversation]:
    """
    获取用户的所有会话，按最后消息时间倒序排列

    Args:
        user_id: 用户ID
        skip: 跳过的记录数
        limit: 返回的最大记录数

    Returns:
        会话对象列表
    """
    return await Conversation.filter(user_id=user_id) \
        .order_by("-last_message_at") \
        .offset(skip) \
        .limit(limit)


async def update_conversation(
        conversation_id: int,
        title: Optional[str] = None,
        model_type: Optional[str] = None
) -> Optional[Conversation]:
    """
    更新会话信息

    Args:
        conversation_id: 会话ID
        title: 新标题，可选
        model_type: 新模型类型，可选

    Returns:
        更新后的会话对象，如不存在则返回None
    """
    conversation = await get_conversation(conversation_id)
    if not conversation:
        return None

    update_fields = []
    if title is not None:
        conversation.title = title
        update_fields.append('title')

    if model_type is not None:
        conversation.model_type = model_type
        update_fields.append('model_type')

    if update_fields:
        await conversation.save(update_fields=update_fields)

    return conversation


async def update_conversation_last_message_time(conversation_id: int) -> Optional[Conversation]:
    """
    更新会话的最后消息时间为当前时间

    Args:
        conversation_id: 会话ID

    Returns:
        更新后的会话对象，如不存在则返回None
    """
    conversation = await get_conversation(conversation_id)
    if not conversation:
        return None

    conversation.last_message_at = datetime.now()
    await conversation.save(update_fields=['last_message_at', 'updated_at'])
    return conversation


async def delete_conversation(conversation_id: int) -> bool:
    """
    删除会话及其所有消息

    Args:
        conversation_id: 会话ID

    Returns:
        True表示删除成功，False表示会话不存在
    """
    conversation = await get_conversation(conversation_id)
    if not conversation:
        return False

    await conversation.delete()
    return True


async def get_conversation_message_count(conversation_id: int) -> int:
    """
    获取会话中的消息总数

    Args:
        conversation_id: 会话ID

    Returns:
        消息数量
    """
    return await Message.filter(conversation_id=conversation_id).count()


async def get_user_conversation_count(user_id: int) -> int:
    """
    获取用户的会话总数

    Args:
        user_id: 用户ID

    Returns:
        会话数量
    """
    return await Conversation.filter(user_id=user_id).count()
