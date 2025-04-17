from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.services.user_service import UserService
from app.models.schemas.user import UserCreate
from app.models.orm.user import  Users  # 确保导入Users模型

router = APIRouter()
templates = Jinja2Templates(directory=r"E:\chatbotv1\app\templates")


# 渲染注册页面
@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# 处理表单提交
@router.post("/register")
async def register_form(
        request: Request,
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        confirm_password: str = Form(..., alias="confirm-password")
):
    # 准备上下文，包含用户输入的值以便回显
    context = {
        "request": request,
        "username": username,
        "email": email
    }

    try:
        # 创建用户
        user_data = UserCreate(
            username=username,
            email=email,
            password=password,
            confirm_password=confirm_password
        )
        service = UserService()

        # 检查用户名是否已存在
        if await Users.exists(username=username):
            context["error"] = "该用户名已被注册，请使用其他用户名"
            return templates.TemplateResponse("register.html", context)

        # 检查邮箱是否已存在 (假设这个检查在service中)
        await service.create_user(user_data)

        # 重定向到登录页面
        return RedirectResponse(
            url="/auth/login?registerSuccess=true",
            status_code=303
        )
    except ValueError as e:
        # 显示具体错误信息
        context["error"] = str(e)
        return templates.TemplateResponse("register.html", context)
    except Exception as e:
        # 处理其他未预期的错误
        context["error"] = f"注册过程中发生错误: {str(e)}"
        return templates.TemplateResponse("register.html", context)


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

#
# @router.post("/register", response_model=UserOut)
# async def register(user_data: UserCreate,service: UserService = Depends()):
#     """
#     用户注册接口
#     - **username**: 3-32位字母数字
#     - **email**: 有效邮箱格式
#     - **password**: 至少6位，含字母和数字
#     """
#     try:
#         return await service.create_user(user_data)
#     except ValueError as e:
#         raise HTTPException(400, detail=str(e))
