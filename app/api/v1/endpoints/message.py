from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from tortoise.transactions import in_transaction
from typing import Optional, List
import logging
from app.models.orm.chat import Conversation, Message

message_router = APIRouter()


# 请求模型
class CreateMessageRequest(BaseModel):
    conversation_id: int
    question: str
    answer: Optional[str] = None
    tokens_used: Optional[int] = 0


# 响应模型
class MessageResponse(BaseModel):
    message_id: int  # 直接使用数据库字段名
    conversation_id: int
    question: str
    answer: Optional[str] = None
    status: str = "success"
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


logger = logging.getLogger(__name__)


@message_router.post("/save_message", response_model=MessageResponse)
async def create_message(request: CreateMessageRequest):
    """
    创建新消息
    """
    try:
        async with in_transaction():
            # 检查对话是否存在
            conv_exists = await Conversation.filter(
                conversation_id=request.conversation_id
            ).exists()

            if not conv_exists:
                raise HTTPException(
                    status_code=404,
                    detail=f"对话 {request.conversation_id} 不存在"
                )

            # 创建消息
            message = await Message.create(
                conversation_id=request.conversation_id,
                question=request.question,
                answer=request.answer,
                tokens_used=request.tokens_used or 0
            )

            # 更新对话最后活动时间
            await Conversation.filter(
                conversation_id=request.conversation_id
            ).update(
                last_message_at=datetime.now(),
                updated_at=datetime.now()
            )

            logger.info(
                f"消息创建成功: conversation_id={request.conversation_id}, "
                f"message_id={message.message_id}"
            )

            return MessageResponse(
                message_id=message.message_id,
                conversation_id=message.conversation_id,
                question=message.question,
                answer=message.answer,
                created_at=message.created_at,
                updated_at=message.updated_at
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"消息创建失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="消息创建时发生错误"
        )


@message_router.get("/get_messages/{conversation_id}", response_model=List[MessageResponse])
async def get_messages(conversation_id: int):
    """
    获取对话的所有消息
    """
    try:
        # 检查对话是否存在
        conv_exists = await Conversation.filter(
            conversation_id=conversation_id
        ).exists()

        if not conv_exists:
            raise HTTPException(
                status_code=404,
                detail=f"对话 {conversation_id} 不存在"
            )

        # 获取消息列表
        messages = await Message.filter(
            conversation_id=conversation_id
        ).order_by("created_at")

        if not messages:
            return []

        return [
            MessageResponse(
                message_id=msg.message_id,
                conversation_id=msg.conversation_id,
                question=msg.question,
                answer=msg.answer,
                created_at=msg.created_at,
                updated_at=msg.updated_at
            )
            for msg in messages
        ]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取消息失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="获取消息时发生错误"
        )