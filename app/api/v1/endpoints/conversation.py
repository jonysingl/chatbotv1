from fastapi import APIRouter, HTTPException, status, Body
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from tortoise.transactions import in_transaction
import logging
from app.models.orm.chat import Conversation, Message

conversation_router = APIRouter()


# 请求模型
class CreateConversationRequest(BaseModel):
    user_id: int
    title: Optional[str] = None
    model_type: str = "gpt-3.5-turbo"


# 响应模型
class CreateConversationResponse(BaseModel):
    conversation_id: int
    title: Optional[str] = None
    status: str = "success"


# 响应模型
class GetConversationResponse(BaseModel):
    conversation_id: int
    title: Optional[str] = None
    status: str = "success"


# 配置日志
logger = logging.getLogger(__name__)


@conversation_router.post("/create_conversation", response_model=CreateConversationResponse,
                          status_code=status.HTTP_201_CREATED, summary="创建新对话", responses={
        400: {"description": "无效请求参数"},
        500: {"description": "服务器内部错误"}
    })
async def create_conversation(request: CreateConversationRequest):
    """
    创建新的对话会话
    """
    try:
        title = request.title or f"新对话 {datetime.now().strftime('%m-%d %H:%M')}"

        async with in_transaction():
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"创建对话失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="创建对话时发生错误")


@conversation_router.get("/conversations",
                         response_model=list[GetConversationResponse],
                         status_code=status.HTTP_200_OK,
                         summary="获取用户全部对话",
                         responses={
                             400: {"description": "无效请求参数"},
                             404: {"description": "对话不存在"},
                             500: {"description": "服务器内部错误"}
                         })
async def get_all_conversations(user_id: int):
    """
    获取用户全部对话记录
    """
    try:
        conversations = await Conversation.filter(user_id=user_id).values("conversation_id", "title")

        if not conversations:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="该用户没有对话记录")

        return [{
            "conversation_id": conv["conversation_id"],
            "title": conv["title"],
            "status": "success"
        } for conv in conversations]

    except Exception as e:
        logger.error(f"获取对话失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="服务器内部错误")


@conversation_router.patch("/conversations/{conversation_id}/title",
                           response_model=GetConversationResponse,
                           status_code=status.HTTP_200_OK,
                           summary="更新对话标题",
                           responses={
                               400: {"description": "标题不能为空"},
                               404: {"description": "对话不存在"},
                               500: {"description": "服务器内部错误"}
                           })
async def update_conversation_title(
        conversation_id: int,
        title: str = Body(..., embed=True)
):
    """
    更新对话标题
    """
    if not title.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="标题不能为空")

    try:
        async with in_transaction():
            updated_count = await Conversation.filter(
                conversation_id=conversation_id
            ).update(title=title.strip(), updated_at=datetime.now())

            if updated_count == 0:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="对话不存在")

            conversation = await Conversation.get(conversation_id=conversation_id)
            logger.info(f"成功更新对话标题: conversation_id={conversation_id}, new_title='{title}'")

            return {
                "conversation_id": conversation.conversation_id,
                "title": conversation.title,
                "status": "success"
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新对话标题失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="更新对话标题时发生错误")


@conversation_router.delete("/conversations/{conversation_id}",
                            status_code=status.HTTP_204_NO_CONTENT,
                            summary="删除对话及关联消息",
                            responses={
                                404: {"description": "对话不存在"},
                                500: {"description": "服务器内部错误"}
                            })
async def delete_conversation(conversation_id: int):
    """
    删除指定对话及其所有关联消息记录
    """
    try:
        async with in_transaction():
            delete_count = await Message.filter(conversation_id=conversation_id).delete()
            logger.info(f"已删除 {delete_count} 条关联消息记录")

            deleted_count = await Conversation.filter(conversation_id=conversation_id).delete()
            if deleted_count == 0:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="对话不存在")

            logger.info(f"成功删除对话: conversation_id={conversation_id}")
            return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除对话失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="删除对话时发生错误")
