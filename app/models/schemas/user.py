from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict, ValidationInfo
from pydantic.types import constr



# 基础模型
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=32, examples=["john_doe"])
    email: EmailStr = Field(..., examples=["user@example.com"])


# 请求模型
class UserCreate(UserBase):
    password: constr(min_length=6, max_length=32) = Field(..., description="6-32位密码", examples=["Password123"])
    confirm_password: str = Field(..., description="确认密码", examples=["Password123"])
    @field_validator("username")
    def username_alphanumeric(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("用户名只能包含字母和数字")
        return v

    @field_validator("confirm_password")
    def password_match(cls, v: str, info: ValidationInfo) -> str:
        if 'password' in info.data and v != info.data['password']:
            raise ValueError("两次输入的密码不一致")
        return v


# 用户响应模型
class UserOut(UserBase):
    user_id: int
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)  # 替代 orm_mode=True


class UserLogin(BaseModel):
    username: str
    password: str

    @field_validator('username')
    def username_must_be_valid(cls, v):
        if not v or len(v) < 1:
            raise ValueError("请输入用户名")
        return v

    @field_validator('password')
    def password_must_be_valid(cls, v):
        if not v or len(v) < 1:
            raise ValueError("请输入密码")
        return v


# 登录响应模型
class UserLoginResponse(UserOut):
    access_token: str
    token_type: str


# 重置密码请求模型
class UserResetRequest(BaseModel):
    email: EmailStr


# 重置密码响应模型
class UserResetResponse(BaseModel):
    token: str = Field(..., min_length=32, max_length=100)
    new_password: str = Field(..., min_length=6, max_length=32)


# 管理员视图模型
class UserAdminView(UserOut):
    reset_token: Optional[str] = None
    reset_token_expires: Optional[datetime] = None

    model_config = ConfigDict(
        json_schema_extra={
            "fields": {
                "reset_token": {"exclude": True}
            }
        }
    )
