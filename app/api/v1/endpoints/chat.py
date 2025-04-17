from fastapi import APIRouter

chat_router = APIRouter()
templates = Jinja2Templates(directory=r"E:\chatbotv1\app\templates")


# 渲染聊天页面
@router.get("/chatbot", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("chatbot.html", {"request": request})
