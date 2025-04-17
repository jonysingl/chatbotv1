from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.services.llm_service import LLMService
from fastapi.responses import HTMLResponse
from fastapi import Request
from fastapi.templating import Jinja2Templates

chat_router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@chat_router.get("/chatbot")
async def chatbot(request: Request):
    user_id = request.cookies.get("user_id")
    username = request.cookies.get("username")

    if not user_id or not username:
        raise HTTPException(status_code=401, detail="未登录，请先登录")

    return templates.TemplateResponse("chatbot.html", {
        "request": request,
        "user_id": user_id,
        "username": username
    })


# 依赖注入：获取LLM服务实例
async def get_llm_service():
    return LLMService()


@chat_router.websocket("/chat")
async def websocket_chat_endpoint(websocket: WebSocket, llm_service: LLMService = Depends(get_llm_service)):
    """
    WebSocket 聊天接口：接收用户请求并通过WebSocket以流式方式返回大模型的响应
    """
    await websocket.accept()  # 接受 WebSocket 连接
    try:
        while True:
            # 接收前端发送的消息
            data = await websocket.receive_json()

            # 确保消息不为空
            if not data.get("message"):
                await websocket.send_json({"error": "输入不能为空"})
                continue

            user_message = data["message"]

            # 调用大模型服务获取流式回答
            try:
                async for chunk in llm_service.chat_completion(
                        messages=[{"role": "user", "content": user_message}],
                        temperature=0.7,
                        stream=True
                ):
                    # 逐步发送生成的内容
                    await websocket.send_json({"response": chunk})

                # 流结束标记（可选）
                await websocket.send_json({"is_final": True})
            except Exception as e:
                await websocket.send_json({"error": f"模型调用失败: {str(e)}"})

    except WebSocketDisconnect:
        print("WebSocket 连接已断开")
