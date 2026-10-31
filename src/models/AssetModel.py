
from motor.motor_asyncio import AsyncIOMotorDatabase

from .db_schemes import Asset

from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnum import DataBaseEnum


class AssetModel(BaseDataModel):
    def __init__(self, db_client: AsyncIOMotorDatabase):
        super().__init__(db_client)
        
        # Set the collection name and collection object for assets
        self.collection_name = DataBaseEnum.COLLECTION_ASSET_NAME.value
        self.collection = self.db_client[self.collection_name]

    @classmethod
    async def create_instance(cls, db_client: AsyncIOMotorDatabase):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    
    async def init_collection(self):

            indexes = Asset.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"]
                )  # Create indexes for the collection
                
                
    async def create_asset(self, asset_data: Asset):
        asset_dict = asset_data.model_dump(by_alias=True, exclude_none=True)
        result = await self.collection.insert_one(asset_dict)
        asset_data.id = result.inserted_id  # Set the id of the asset_data object
        return asset_data  # Return the asset_data object with the assigned id
    
    async def get_all_project_assets(self, asset_project_id: str, page: int = 1, page_size: int = 10):
        skip_count = (page - 1) * page_size
        cursor = self.collection.find({"asset_project_id": asset_project_id}).skip(skip_count).limit(page_size)
        assets = await cursor.to_list(length=page_size)
        return [Asset(**asset) for asset in assets]
