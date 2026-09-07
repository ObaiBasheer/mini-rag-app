import os
import aiofiles
from fastapi import FastAPI, APIRouter, Depends ,UploadFile, status
from fastapi.responses import JSONResponse
from helpers.config import Settings , get_settings
from controllers import DataController , ProjectController , ProcessController
from models.enums import ResponseSignal
import logging
from .schemas.data import ProcessRequest

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(prefix="/api/v1/data", tags=["api_v1", "data"])



####  

@data_router.post("/upload/{project_id}")
async def upload_data(project_id:str, file:UploadFile, app_settings: Settings = Depends(get_settings)):
    ## DataController_instance = DataController()
    
    
    is_valid, response = await DataController().validate_and_upload_data(file)
    if not is_valid:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=response)
    
    project_dir_path = ProjectController().get_project_path(project_id)
    file_path, file_id = DataController().generate_unique_filename(file.filename, project_id)
    
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await out_file.write(chunk)
                
    except Exception as e:
        logger.error(f"Error occurred while uploading file: {e}")
        
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": ResponseSignal.FILE_UPLOAD_FAILED.value})
            
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": ResponseSignal.FILE_UPLOAD_SUCCESS.value , "file_id": file_id })


####

@data_router.post("/process/{project_id}")
async def process_data(project_id:str, request: ProcessRequest):
    # Implement the logic to process the data based on the provided parameters
    file_content = ProcessController().get_file_content(request.file_id)
    
    file_chunks = ProcessController().process_file_content(
        file_id=request.file_id,
        chunk_size=request.chunk_size,
        chunk_overlap=request.overlap_size,
        file_content=file_content
    )
    
    if file_chunks:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": ResponseSignal.FILE_PROCESS_SUCCESS.value, "chunks": file_chunks})
    else:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": ResponseSignal.FILE_PROCESS_FAILED.value})