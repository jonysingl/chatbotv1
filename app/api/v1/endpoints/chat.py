from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse  # 添加缺少的导入

chat_router = APIRouter()
templates = Jinja2Templates(directory=r"E:\chatbotv1\app\templates")



# 渲染聊天页面
@chat_router.get("/chatbot", response_class=HTMLResponse)  # 修正：使用chat_router而不是app
async def chatbot_page(request: Request):
    # 从cookie获取用户数据
    user_id = request.cookies.get("user_id", "")
    username = request.cookies.get("username", "游客")

    return templates.TemplateResponse(
        "chatbot.html",
        {
            "request": request,
            "user_id": user_id,
            "username": username
        }
    )