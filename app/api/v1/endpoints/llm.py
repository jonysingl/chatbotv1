from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from typing import List, Optional
from app.services.llm_service import LLMService  # 替换为实际路径

llm_router = APIRouter()

# 初始化LLM服务（单例模式）
llm_service = LLMService(temperature=0)

# 嵌套模型用于验证历史记录
class ChatHistoryItem(BaseModel):
    content: str
    role: str = "user"  # 默认角色为 "user"

    @field_validator("role", mode="before")
    def validate_or_default_role(cls, value):
        if value not in ["user", "assistant"]:
            return "user"  # 如果角色无效，强制设置为 "user"
        return value

# 请求/响应模型
class ChatRequest(BaseModel):
    query: str
    history: Optional[List[ChatHistoryItem]] = None  # 可选历史记录
    system_prompt: Optional[str] = "你是一个有帮助的AI助手"  # 可选系统提示词

class ChatResponse(BaseModel):
    response: str
    status: str = "success"

@llm_router.post("/query", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    """
    调用大模型聊天服务
    - query: 用户输入的问题
    - history: 可选，对话历史格式 [{"role": "user", "content": "你好"}, {"role": "assistant", "content": "你好！"}]
    - system_prompt: 可选，系统提示词
    """
    try:
        # 将 Pydantic 模型实例转换为字典
        history = [item.dict() for item in request.history] if request.history else []

        # 调用 LLM 服务
        response = llm_service.chat(
            query=request.query,
            history=history,  # 传递处理后的字典列表
            system_prompt=request.system_prompt
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"LLM 服务调用失败: {str(e)}"
        )