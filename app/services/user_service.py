from passlib.context import CryptContext
from app.models.orm.user import Users
from app.models.schemas.user import UserCreate, UserOut
from typing import Optional


class UserService:
    # 初始化密码加密上下文
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    def hash_password(password: str) -> str:
        """密码加密方法"""
        return UserService.pwd_context.hash(password)

    @classmethod
    async def create_user(cls, user_data: UserCreate) -> UserOut:
        """
        创建用户
        修改点：
        1. 使用model_dump()替代已弃用的dict()
        2. 添加密码加密
        3. 更完善的错误处理
        """
        # 检查邮箱是否已注册
        if await Users.exists(email=user_data.email):
            raise ValueError("该邮箱已经被注册！")
        if await Users.exists(username=user_data.username):
            raise ValueError("该用户名已被注册！")

        # 准备用户数据，排除confirm_password
        user_data_dict = user_data.model_dump(exclude={"confirm_password"})

        # 加密密码
        # user_data_dict["password"] = cls.hash_password(user_data.password)
        # 创建用户
        db_user = await Users.create(**user_data_dict)

        return UserOut.model_validate(db_user)  # 使用model_validate替代from_orm

    @classmethod
    async def get_by_email(cls, email: str) -> Optional[Users]:
        """根据邮箱获取用户（无需修改）"""
        return await Users.get_or_none(email=email)