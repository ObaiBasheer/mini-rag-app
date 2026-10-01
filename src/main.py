from fastapi import  FastAPI
from routes import base , data
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from contextlib import asynccontextmanager






@asynccontextmanager
async def startup_db_client(app: FastAPI):
    settings = get_settings()
    app.mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
    app.mongodb = app.mongodb_client[settings.MONGODB_DATABASE]
    
    yield  #  app runs and processes requests here
    
    
    # Shutdown: Close the Motor client connection pool safely
    app.mongodb_client.close()


app = FastAPI(lifespan=startup_db_client)
app.include_router(base.base_router)
app.include_router(data.data_router)
