
from .BaseController import BaseController
from .projectController import ProjectController
import os
from models  import ProcessingSignal
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter



class ProcessController(BaseController):
    def __init__(self, project_id:str):
        super().__init__()
        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id)
        
        
    def get_file_extension(self, file_id: str) -> str:
        # Extract the file extension from the filename
        return os.path.splitext(file_id)[1]  # Returns the extension including the dot (e.g., '.txt')
    
    def get_file_loader(self, file_id:str ):
        
        file_ext = self.get_file_extension(file_id)
        file_path = os.path.join(self.project_path, file_id)
        
        if file_ext == ProcessingSignal.TXT.value:
            return TextLoader(file_path, encoding="utf-8")
        
        elif file_ext == ProcessingSignal.PDF.value:
            return PyMuPDFLoader(file_path)
        
        return None
    
    def get_file_content(self, file_id:str):
        loader = self.get_file_loader(file_id)
        if loader:
            return loader.load()
        else:
            return None
        
    def process_file_content(self, file_id:str, chunk_size:int=100, chunk_overlap:int=20, file_content:list=None):
        if file_content is None:
            content = self.get_file_content(file_id)
        else:
            content = file_content

        if content:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len
            )
            
            # # Extract text and metadata from the loaded content
            # file_content_texts = [
            #     rec.page_content 
            #     for rec in content
            # ]
            
            # file_content_metadata = [

            #     rec.metadata 
            #     for rec in content
            # ]
            
            # # Split the documents into chunks using the text splitter
            
            # chunks = text_splitter.split_documents(
            #     file_content_texts, 
            #     file_content_metadata
            # )
            
            chunks = text_splitter.split_documents(content)
            return chunks
        else:
            return None