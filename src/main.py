from fastapi import  FastAPI
from routes import base , data
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from contextlib import asynccontextmanager




app = FastAPI()

@asynccontextmanager
async def startup_db_client():
    settings = get_settings()
    app.mongodb_client = AsyncIOMotorClient(settings.MONGO_URI)
    app.mongodb = app.mongodb_client[settings.MONGO_DB_NAME]
    
    yield  #  app runs and processes requests here
    
    # Shutdown: Close the Motor client connection pool safely
    app.mongodb_client.close()

app.include_router(base.base_router)
app.include_router(data.data_router)
