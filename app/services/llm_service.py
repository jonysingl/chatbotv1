from typing import List, Optional
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# 必须先加载环境变量！
load_dotenv()  # 默认加载项目根目录的.env文件
class LLMService:
    def __init__(self, temperature: float = 0.7):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("未找到DEEPSEEK_API_KEY环境变量，请检查.env文件")

        self.llm = ChatOpenAI(
            api_key=api_key,
            base_url="https://dseek.aikeji.vip/v1",
            model="deepseek-v3",
            temperature=temperature,
            max_retries=3
        )

    def chat(self,query: str,history: Optional[List[dict]] = None,system_prompt: str = "你是一个有帮助的AI助手") -> str:
        messages = [SystemMessage(content=system_prompt)]

        if history:
            for msg in history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))

        messages.append(HumanMessage(content=query))

        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            return f"API调用失败: {str(e)}"


# if __name__ == "__main__":
#     # 测试代码
#     try:
#         chatbot = LLMService()
#         print(chatbot.chat("你好"))
#     except ValueError as e:
#         print(f"初始化失败: {e}")
#     except Exception as e:
#         print(f"运行时错误: {e}")