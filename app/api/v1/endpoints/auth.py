from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.services.user_service import UserService
from app.models.schemas.user import UserCreate, UserLogin
from pydantic import ValidationError

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

        # 直接使用类方法，不需要实例化
        await UserService.create_user(user_data)

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


# 登录页面渲染
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    # 检查URL参数
    register_success = request.query_params.get("registerSuccess") == "true"
    error = request.query_params.get("error")

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "register_success": register_success,
            "error": error
        }
    )


# 处理登录表单提交
@router.post("/login")
async def login_form(
        request: Request,
        username: str = Form(...),
        password: str = Form(...)
):
    # 准备上下文，包含用户名以便回显
    context = {
        "request": request,
        "username": username
    }

    try:
        # 使用UserLogin模式验证数据
        user_login = UserLogin(
            username=username,
            password=password
        )

        # 验证用户 - 使用类方法而不是依赖注入
        user_data = await UserService.verify_user(user_login)

        # 创建响应重定向到chatbot页面
        response = RedirectResponse(url="/chat/chatbot", status_code=303)

        # 设置cookie或会话数据
        response.set_cookie(
            key="user_id",
            value=str(user_data["id"]),
            httponly=True
        )
        response.set_cookie(
            key="username",
            value=user_data["username"],
            httponly=True
        )

        return response

    except ValidationError as e:
        # 处理验证错误
        errors = e.errors()
        error_msg = errors[0]['msg'] if errors else "输入数据无效"
        context["error"] = error_msg
        return templates.TemplateResponse("login.html", context)
    except ValueError as e:
        # 显示登录错误
        context["error"] = str(e)
        return templates.TemplateResponse("login.html", context)
    except Exception as e:
        # 处理其他未预期的错误
        context["error"] = f"登录过程中发生错误: {str(e)}"
        return templates.TemplateResponse("login.html", context)


# 登出
@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/auth/login", status_code=303)
    # 清除认证cookie - 更新以匹配登录时设置的cookie
    response.delete_cookie(key="user_id")
    response.delete_cookie(key="username")
    return response