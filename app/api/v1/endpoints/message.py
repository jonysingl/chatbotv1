from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
from tortoise.transactions import in_transaction
from typing import Optional
import logging
from app.models.orm.chat import Conversation,Message

message_router = APIRouter()


# 请求模型
class CreateMessageRequest(BaseModel):
    conversation_id: int
    question: str
    answer: Optional[str] = None
    tokens_used: Optional[int] = 0


# 响应模型
class MessageResponse(BaseModel):
    message_id: int
    conversation_id: int
    status: str = "success"


logger = logging.getLogger(__name__)


@message_router.post("/", response_model=MessageResponse)
async def create_message(request: CreateMessageRequest):
    """
    创建新消息

    参数:
    - conversation_id: 必须，所属对话ID
    - question: 必须，用户问题
    - answer: 可选，AI回复内容
    - tokens_used: 可选，消耗的token数

    返回:
    - message_id: 新创建的消息ID
    - status: 操作状态
    """
    try:
        async with in_transaction():
            # 1. 验证对话是否存在
            conversation = await Conversation.filter(
                conversation_id=request.conversation_id
            ).first()

            if not conversation:
                raise HTTPException(
                    status_code=404,
                    detail=f"对话 {request.conversation_id} 不存在"
                )

            # 2. 创建消息记录
            message = await Message.create(
                conversation_id=request.conversation_id,
                question=request.question,
                answer=request.answer,
                tokens_used=request.tokens_used or 0
            )

            # 3. 更新对话的最后活动时间
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

            return {
                "message_id": message.message_id,
                "conversation_id": message.conversation_id,
                "status": "success"
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"消息创建失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="消息创建时发生错误"
        )