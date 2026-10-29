from pydantic import BaseModel , Field , field_validator
from typing import Optional
from bson import ObjectId
from datetime import datetime


class Asset(BaseModel):
    id: Optional[ObjectId] = Field(
        default=None,
        alias="_id"
    )
    
    asset_project_id:str = Field(..., description="ID of the project to which the asset belongs")
    asset_type:str = Field(..., description="Type of the asset", min_length=1)
    asset_name:str = Field(..., description="Unique identifier for the asset", min_length=1)
    asset_size:int = Field(ge=0,default=None, description="Size of the asset in bytes")
    asset_config: Optional[dict] = Field(default=None, description="Configuration details for the asset")
    asset_pushed_at: datetime = Field(default=datetime.utcnow, description="Timestamp when the asset was pushed")
    
    
    class Config:
        arbitrary_types_allowed = True
        # json_encoders = {ObjectId: str}

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [
                    ("asset_project_id", 1)
                    ],
                
                "unique": False,
                "name": "unique_asset_project_id_index_1"
            },
             {
                            "key": [
                                ("asset_project_id", 1)
                                ],
                            
                            "unique": False,
                            "name": "unique_asset_project_id_index_1"
             }
        ]