# import requests
#
# url = "https://dseek.aikeji.vip/v1/chat/completions"
# headers = {
#     "Content-Type": "application/json",
#     "Authorization": "Bearer sk-lKAsCm3FPhOzSQiBXNYBGfAmrLbRGPoBdJ6z9g7nBJYrWWfi"
# }
# data = {
#     "model": "deepseek-v3",
#     "messages": [{"role": "user", "content": "你好"}]
# }
#
# response = requests.post(url, json=data, headers=headers)
# print(response.status_code)
# print(response.text)

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# 修正配置（关键修改）
chat = ChatOpenAI(
    api_key="sk-lKAsCm3FPhOzSQiBXNYBGfAmrLbRGPoBdJ6z9g7nBJYrWWfi",
    base_url="https://dseek.aikeji.vip/v1",  # 必须包含/v1
    model="deepseek-v3",
    temperature=0,
    streaming=False  # 先关闭流式传输
)

# 测试调用
messages = [HumanMessage(content="你好")]
response = chat.invoke(messages)
print(response.content)