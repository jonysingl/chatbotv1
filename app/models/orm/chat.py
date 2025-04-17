from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from datetime import datetime


class Conversation(models.Model):
    """会话模型"""
    conversation_id = fields.BigIntField(pk=True, autoincrement=True)
    user_id = fields.IntField(index=True)
    title = fields.CharField(max_length=255, null=True)
    model_type = fields.CharField(max_length=50)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    last_message_at = fields.DatetimeField(null=True)

    class Meta:
        table = "conversations"

    def __str__(self):
        return f"Conversation {self.conversation_id}: {self.title}"


class Message(models.Model):
    """消息模型"""
    message_id = fields.BigIntField(pk=True, autoincrement=True)
    conversation = fields.ForeignKeyField(
        'models.Conversation',
        related_name='messages',
        on_delete=fields.CASCADE
    )
    question = fields.TextField(null=True)
    answer = fields.TextField(null=True)
    tokens_used = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True, index=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "messages"

    def __str__(self):
        return f"Message {self.message_id} in conversation {self.conversation_id}"


# 创建 Pydantic 模型用于 API 响应
Conversation_Pydantic = pydantic_model_creator(Conversation, name="Conversation")
ConversationIn_Pydantic = pydantic_model_creator(
    Conversation, name="ConversationIn", exclude_readonly=True
)

Message_Pydantic = pydantic_model_creator(Message, name="Message")
MessageIn_Pydantic = pydantic_model_creator(
    Message, name="MessageIn", exclude_readonly=True
)