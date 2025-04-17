from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse,Response
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
            httponly=True,  # 防止前端 JS 访问
            secure=True,  # 仅在 HTTPS 下传输
            max_age=3600,  # Cookie 有效期（秒）
            samesite="Lax"  # 防止 CSRF 攻击
        )
        response.set_cookie(
            key="username",
            value=user_data["username"],
            httponly=True,
            secure=True,
            max_age=3600,
            samesite="Lax"
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


# cookie续期
@router.get("/renew-cookie")
def renew_cookie(request: Request, response: Response):
    # 获取现有的 Cookie 值（如果需要）
    user_id = request.cookies.get("user_id")
    username = request.cookies.get("username")

    # 如果用户已登录，则延长 Cookie 有效期
    if user_id and username:
        response.set_cookie(
            key="user_id",
            value=user_id,
            max_age=30 * 24 * 60 * 60,  # 延长有效期 30 天
            httponly=True,
            secure=True,
            samesite="Lax"
        )
        response.set_cookie(
            key="username",
            value=username,
            max_age=30 * 24 * 60 * 60,  # 延长有效期 30 天
            httponly=True,
            secure=True,
            samesite="Lax"
        )
        return {"message": "Cookie 已续期"}
    else:
        return {"message": "未发现登录信息，Cookie 未续期"}


# 登出
@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/auth/login", status_code=303)
    # 清除认证cookie - 更新以匹配登录时设置的cookie
    response.delete_cookie(key="user_id")
    response.delete_cookie(key="username")
    return response
