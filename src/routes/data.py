from fastapi import FastAPI, APIRouter, Depends ,UploadFile
from helpers.config import Settings , get_settings

data_router = APIRouter(prefix="/api/v1/data", tags=["api_v1", "data"])

@data_router.post("/upload/{project_id}")
async def upload_data(project_id:str, file:UploadFile, app_settings: Settings = Depends(get_settings)):
