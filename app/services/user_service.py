from passlib.context import CryptContext
from app.models.orm.user import Users
from app.models.schemas.user import UserCreate, UserOut
from typing import Optional


class UserService:
    # 保留加密上下文初始化（已注释）
    # pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def hash_password(cls, password: str) -> str:
        """密码加密方法（已注释）"""
        # return cls.pwd_context.hash(password)
        return password  # 直接返回明文密码

    @classmethod
    async def create_user(cls, user_data: UserCreate) -> UserOut:
        """
        创建用户（不加密密码版本）
        """
        # 检查邮箱是否已注册
        if await Users.exists(email=user_data.email):
            raise ValueError("该邮箱已经被注册！")
        if await Users.exists(username=user_data.username):
            raise ValueError("该用户名已被注册！")

        # 准备用户数据，排除confirm_password
        user_data_dict = user_data.model_dump(exclude={"confirm_password"})

        # 密码处理（加密逻辑已注释）
        # user_data_dict["password"] = cls.hash_password(user_data.password)
        user_data_dict["password"] = user_data.password  # 直接存储明文密码

        # 创建用户
        db_user = await Users.create(**user_data_dict)

        return UserOut.model_validate(db_user)

    @classmethod
    async def verify_user(cls, username: str, password: str):
        """验证用户凭据（明文比对版本）"""
        # 查找用户
        user = await Users.get_or_none(username=username)

        # 如果用户不存在
        if not user:
            raise ValueError("用户名或密码不正确")

        # 密码验证（加密验证已注释）
        # if not cls.pwd_context.verify(password, user.password):
        if password != user.password:  # 直接比对明文密码
            raise ValueError("用户名或密码不正确")

        # 返回用户信息（不包含密码）
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }

    @classmethod
    async def get_by_email(cls, email: str) -> Optional[Users]:
        """根据邮箱获取用户"""
        return await Users.get_or_none(email=email)
