import aiosmtplib

from tortoise.models import Model
from tortoise import fields

from pydantic import field_validator


class Users(Model):
    user_id = fields.IntField(pk=True)
    # 基础字段
    username = fields.CharField(max_length=32, unique=True, description="用户名")
    email = fields.CharField(max_length=64, unique=True, description="邮箱")
    password = fields.CharField(max_length=32, description="密码")
    # 时间记录
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
    last_login = fields.DatetimeField(description="最后登录时间")
    # token块
    reset_token = fields.CharField(max_length=100, null=True, description="重置密码token")
    reset_token_expires = fields.DatetimeField(null=True, description="重置密码token过期时间")


class Meta:  # ORM元数据
    table = "users"
    indexes = [
        ("reset_token",),  # 对应idx_reset_token索引
    ]

def __str__(self):  # 重写__str__方法
    return f"User {self.user_id}: {self.username}"  # 返回用户信息


