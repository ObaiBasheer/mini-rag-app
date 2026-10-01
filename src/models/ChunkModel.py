from .BaseDataModel import BaseDataModel
from .db_schemes import DataChunk
from .enums.DataBaseEnum import DataBaseEnum
from bson.objectid import ObjectId
from pymongo import InsertOne


class ChunkModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client)
        
        # Set the collection name and collection object for chunks
        self.collection_name = DataBaseEnum.COLLECTION_CHUNK_NAME.value
        self.collection = self.db_client[self.collection_name]
    
    # Create a new chunk in the database    
    async def create_chunk(self, chunk_data: DataChunk):
        chunk_dict = chunk_data.model_dump(exclude_unset=True)  # Convert Pydantic model to dictionary, excluding unset fields
        result = await self.collection.insert_one(chunk_dict)
        return str(result.inserted_id)
    
    # Retrieve chunks by project_id with pagination
    async def get_chunks_by_project_id(self, project_id: str, page: int = 1, page_size: int = 10):
        
        # Calculate the number of documents to skip based on the page and page_size
        total_documents = await self.collection.count_documents({"project_id": project_id})
        
        # calculate number of pages based on total documents and page size
        total_pages = (total_documents + page_size - 1) // page_size
        
        
        skip = (page - 1) * page_size
        cursor = self.collection.find({"project_id": project_id}).skip(skip).limit(page_size)
        
        chunks = []
        async for doc in cursor:
            chunks.append(doc)
        return chunks, total_pages
    
    
    async def get_chunk(self, chunk_id:str):
        # Retrieve a single chunk by its ObjectId
        chunk = await self.collection.find_one({"_id": ObjectId(chunk_id)})
        if chunk:
            return DataChunk(**chunk)  # Return the chunk as a Pydantic model
        return None
    
    async def insert_chunks_bulk(self, chunks: list, batch_size: int = 100):
        # Insert multiple chunks in bulk
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            operations = [InsertOne(chunk.model_dump(exclude_unset=True)) for chunk in batch]
            await self.collection.bulk_write(operations)
            
        return {"message": f"Inserted {len(chunks)} chunks in batches of {batch_size}."}
    
    async def delete_chunks_by_project_id(self, project_id: str):
        # Delete all chunks associated with a specific project_id
        result = await self.collection.delete_many({"chunk_project_id": project_id})
        return {"message": f"Deleted {result.deleted_count} chunks for project_id: {project_id}."}