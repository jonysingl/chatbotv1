from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from app.config.settings import TORTOISE_ORM
import uvicorn
from app.api.v1.endpoints import conversation_router, chat_router, router, message_router,llm_router
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="E:/chatbotv1/app/static"), name="static")
register_tortoise(app=app,
                  config=TORTOISE_ORM)  # generate_schemas=True,add_exception_handlers=True # 生成数据库表 # 添加异常处理 不开

app.include_router(router, prefix="/auth", tags=["注册登录模块"])
app.include_router(chat_router, prefix="/chat", tags=["大预言模型聊天模块"])

app.include_router(conversation_router, prefix="/conversation", tags=["会话模块"])

app.include_router(message_router, prefix= "/message", tags = ["消息模块"])

app.include_router(llm_router, prefix="/llm", tags=["LLM模型模块"])


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
