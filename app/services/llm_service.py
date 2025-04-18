from typing import List, Optional, Dict, Any
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from pydantic import BaseModel

# 加载环境变量
load_dotenv()


class ChatHistoryItem(BaseModel):
    content: str
    role: str = "user"  # 默认角色为 user


class LLMService:
    def __init__(self, temperature: float = 0.7):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("未找到 OPENAI_API_KEY 环境变量，请检查 .env 文件")

        self.llm = ChatOpenAI(
            api_key=api_key,
            base_url="https://dseek.aikeji.vip/v1",
            model="deepseek-v3",
            temperature=temperature,
            max_retries=3
        )

    def chat(self,
             query: str,
             history: Optional[List[Dict[str, Any]]] = None,
             system_prompt: str = "你是一个有帮助的 AI 助手") -> str:
        """
        与 LLM 交互的聊天方法

        参数:
            query: 用户当前问题 (必填)
            history: 可选的历史对话记录，格式为 [{"content": "...", "role": "user/assistant"}]
            system_prompt: 系统提示词 (默认值)
        """
        try:
            # 如果未提供历史记录，初始化为空列表
            history = history or []

            # 构建消息列表
            messages = [SystemMessage(content=system_prompt)]

            # 处理历史消息
            for msg in history:
                role = msg.get("role", "user")  # 默认角色为 "user"
                if role == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))

            # 添加当前问题
            messages.append(HumanMessage(content=query))

            # 调用 LLM
            response = self.llm.invoke(messages)
            return response.content

        except KeyError as e:
            return f"消息格式错误: 缺少必要字段 {str(e)}"
        except Exception as e:
            return f"API 调用失败: {str(e)}"


# 测试用例
# if __name__ == "__main__":
#     try:
#         # 初始化服务
#         chatbot = LLMService()
#
#         # 测试用例1: 无历史记录
#         print("测试1:", chatbot.chat("你好"))
#
#         # 测试用例2: 有历史记录但无 role
#         history_no_role = [{"content": "上一个问题"}, {"content": "上一个回答"}]
#         print("测试2:", chatbot.chat("继续", history=history_no_role))
#
#         # 测试用例3: 完整历史记录
#         full_history = [
#             {"content": "你好", "role": "user"},
#             {"content": "你好！", "role": "assistant"}
#         ]
#         print("测试3:", chatbot.chat("Python怎么学？", history=full_history))
#
#     except ValueError as e:
#         print(f"初始化失败: {e}")
#     except Exception as e:
#         print(f"运行时错误: {e}")