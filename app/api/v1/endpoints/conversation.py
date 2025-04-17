from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from tortoise.transactions import in_transaction
import logging
from app.models.orm.chat import Conversation

conversation_router = APIRouter()

# 请求模型
class CreateConversationRequest(BaseModel):
    user_id: int
    title: Optional[str] = None
    model_type: str = "gpt-3.5-turbo"
# 响应模型
class CreateConversationResponse(BaseModel):
    conversation_id: int
    status: str = "success"
# 配置日志
logger = logging.getLogger(__name__)
@conversation_router.post("/create_conversation",response_model=CreateConversationResponse,status_code=status.HTTP_201_CREATED,summary="创建新对话",responses={
        400: {"description": "无效请求参数"},
        500: {"description": "服务器内部错误"}
    }
)
async def create_conversation(request: CreateConversationRequest):
    """
    创建新的对话会话

    参数:
    - user_id: 必须，用户ID
    - title: 可选，对话标题（为空时自动生成）
    - model_type: 可选，模型类型（默认gpt-3.5-turbo）

    返回:
    - conversation_id: 新创建的对话ID
    - status: 操作状态
    """
    try:
        # 生成标题（如果未提供）
        title = request.title or f"新对话 {datetime.now().strftime('%m-%d %H:%M')}"

        async with in_transaction():  # 使用事务保证数据一致性
            # 创建对话记录
            conversation = await Conversation.create(
                user_id=request.user_id,
                title=title,
                model_type=request.model_type,
                last_message_at=datetime.now()
            )

            logger.info(f"成功创建对话: user_id={request.user_id}, conversation_id={conversation.conversation_id}")

            return {
                "conversation_id": conversation.conversation_id,
                "status": "success"
            }

    except ValueError as e:
        logger.warning(f"无效参数: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"创建对话失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建对话时发生错误"
        )