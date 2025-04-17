from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from app.config.settings import TORTOISE_ORM
import uvicorn
from app.api.v1.endpoints.auth import router
from app.api.v1.endpoints.chat import chat_router
from fastapi.staticfiles import StaticFiles
app = FastAPI()
app.mount("/static", StaticFiles(directory="E:/chatbotv1/app/static"), name="static")
register_tortoise(app=app,config=TORTOISE_ORM)  # generate_schemas=True,add_exception_handlers=True # 生成数据库表 # 添加异常处理 不开

app.include_router(router, prefix="/auth")
app.include_router(chat_router, prefix="/chat")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
