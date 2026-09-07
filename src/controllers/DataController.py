from .BaseController import BaseController 
from controllers.projectController import ProjectController
from fastapi import UploadFile
from models import ResponseSignal
import os
import re

class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.file_size_mb =  1024 * 1024
        
    async def validate_and_upload_data(self,  file: UploadFile):
        # Check if the file extension is allowed
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, {"error": ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value}

        # Check if the file size exceeds the maximum limit
        if file.size > self.app_settings.FILE_MAX_SIZE_MB * self.file_size_mb:
            return False, {"error": ResponseSignal.FILE_SIZE_EXCEEDED.value}
        
        return True, {"message": ResponseSignal.FILE_VALIDATION_SUCCESS.value}
    
    def generate_unique_filename(self, original_filename: str, project_id: str) -> str:
        # Generate a unique filename by appending a random string to the original filename
        random_string = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_id)
        
        # clean the original filename to avoid issues with special characters
        cleaned_filename = self.get_cleaned_filename(original_filename)
        new_file_path = os.path.join(project_path, random_string + "_" + cleaned_filename)
        
        while os.path.exists(new_file_path):
            random_string = self.generate_random_string()
            new_file_path = os.path.join(project_path, random_string + "_" + cleaned_filename)
        
        return new_file_path, random_string + "_" + cleaned_filename
    
    def get_cleaned_filename(self, original_filename: str) -> str:
        # remove any special characters , except underscores and .
        cleaned_filename = re.sub(r'[^a-zA-Z0-9_.]', '', original_filename)
        return cleaned_filename