from fastapi import  FastAPI
from routes import base , data
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from contextlib import asynccontextmanager

from models.ProjectModel import ProjectModel






@asynccontextmanager
async def startup_db_client(app: FastAPI):
    settings = get_settings()
    mongodb_client = AsyncIOMotorClient(settings.MONGODB_URI)
    app.state.mongodb_client = mongodb_client
    app.state.mongodb = mongodb_client[settings.MONGODB_DATABASE]

    try:
        # Initialize indexes once during startup
        project_model = ProjectModel(app.state.mongodb)
        await project_model.init_collection()

        yield  # app runs and processes requests here
    finally:
        # Close the Motor client connection pool safely
        mongodb_client.close()


app = FastAPI(lifespan=startup_db_client)
app.include_router(base.base_router)
app.include_router(data.data_router)
