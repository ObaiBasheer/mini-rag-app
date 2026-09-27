from pydantic import BaseModel, Field
from typing import Optional, List
from bson.objectid import ObjectId

class DataChunk(BaseModel):
    _id: Optional[ObjectId]
    chunk_text: str = Field(..., description="Text content of the data chunk", min_length=1)
    chunk_metadata: Optional[dict] = Field(default_factory=dict, description="Metadata associated with the data chunk")
    chunk_order: Optional[int] = Field(gt=0, description="Order of the chunk in the original document")

    chunk_project_id: str = Field(..., description="Identifier for the project to which the data chunk belongs", min_length=1)
    
    class Config:
        arbitrary_types_allowed = True
        # json_encoders = {ObjectId: str}