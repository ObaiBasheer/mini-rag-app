from motor.motor_asyncio import AsyncIOMotorDatabase

from helpers.config import get_settings, Settings


class BaseDataModel:
    
    def __init__(self, db_client: AsyncIOMotorDatabase):
        self.db_client = db_client
        self.app_settings: Settings = get_settings()
