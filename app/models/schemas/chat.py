from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# 聊天请求模型
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None
    model_type: Optional[str] = "default"

# 聊天响应模型
class ChatResponse(BaseModel):
    success: bool
    conversation_id: int
    message_id: Optional[int] = None
    error: Optional[str] = None

# AI 回复请求模型
class AIResponseRequest(BaseModel):
    message_id: int
    response: str
    tokens_used: Optional[int] = 0

# AI 回复响应模型
class AIResponseResponse(BaseModel):
    success: bool
    message_id: Optional[int] = None
    conversation_id: Optional[int] = None
    tokens_used: Optional[int] = 0
    error: Optional[str] = None

# 会话列表请求模型
class ConversationListRequest(BaseModel):
    skip: Optional[int] = 0
    limit: Optional[int] = 20

# 会话历史请求模型
class ChatHistoryRequest(BaseModel):
    conversation_id: int
    limit: Optional[int] = 50