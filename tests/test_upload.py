import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from bson import ObjectId
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pymongo.results import InsertOneResult

from helpers.config import get_settings
from models.AssetModel import AssetModel
from models.ProjectModel import ProjectModel
from models.db_schemes import Asset, Project
from models.enums.DataBaseEnum import DataBaseEnum
from routes.data import data_router


class UploadTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        settings_patch = patch("models.BaseDataModel.get_settings", return_value=None)
        settings_patch.start()
        self.addCleanup(settings_patch.stop)

    async def test_asset_insert_handles_unset_null_and_explicit_ids(self):
        for fields in ({}, {"_id": None}, {"_id": ObjectId()}):
            with self.subTest(fields=fields):
                collection = MagicMock()
                inserted_id = fields.get("_id") or ObjectId()
                collection.insert_one = AsyncMock(
                    return_value=InsertOneResult(inserted_id, True)
                )
                database = MagicMock()
                database.__getitem__.return_value = collection
                asset = Asset(
                    asset_project_id=str(ObjectId()),
                    asset_type="file",
                    asset_name="example.txt",
                    **fields,
                )

                result = await AssetModel(database).create_asset(asset)

                document = collection.insert_one.await_args.args[0]
                if fields.get("_id") is None:
                    self.assertNotIn("_id", document)
                else:
                    self.assertEqual(document["_id"], fields["_id"])
                self.assertNotIn("id", document)
                self.assertIn("asset_pushed_at", document)
                self.assertEqual(document["asset_size"], 0)
                self.assertIs(result, asset)
                self.assertEqual(asset.id, inserted_id)

    async def test_new_project_receives_its_database_id(self):
        for fields in ({}, {"_id": None}, {"_id": ObjectId()}):
            with self.subTest(fields=fields):
                collection = MagicMock()
                inserted_id = fields.get("_id") or ObjectId()
                collection.insert_one = AsyncMock(
                    return_value=InsertOneResult(inserted_id, True)
                )
                database = MagicMock()
                database.__getitem__.return_value = collection
                project = Project(project_id="demo", **fields)

                result = await ProjectModel(database).create_project(project)

                document = collection.insert_one.await_args.args[0]
                if fields.get("_id") is None:
                    self.assertNotIn("_id", document)
                else:
                    self.assertEqual(document["_id"], fields["_id"])
                self.assertNotIn("id", document)
                self.assertEqual(project.id, inserted_id)
                self.assertEqual(result, str(inserted_id))

    async def test_repeated_uploads_return_saved_filenames_and_link_to_project(self):
        project_id = ObjectId()
        asset_ids = [ObjectId(), ObjectId()]
        projects = MagicMock()
        projects.create_index = AsyncMock()
        projects.find_one = AsyncMock(
            side_effect=[None, {"_id": project_id, "project_id": "demo"}]
        )
        projects.insert_one = AsyncMock(
            return_value=InsertOneResult(project_id, True)
        )
        assets = MagicMock()
        assets.create_index = AsyncMock()
        assets.insert_one = AsyncMock(
            side_effect=[InsertOneResult(value, True) for value in asset_ids]
        )
        collections = {
            DataBaseEnum.COLLECTION_PROJECT_NAME.value: projects,
            DataBaseEnum.COLLECTION_ASSET_NAME.value: assets,
        }
        database = MagicMock()
        database.__getitem__.side_effect = collections.__getitem__

        with tempfile.TemporaryDirectory() as upload_dir:
            settings = SimpleNamespace(
                FILE_ALLOWED_TYPES=["text/plain"],
                FILE_MAX_SIZE_MB=1,
                FILE_UPLOAD_DIR=upload_dir,
                FILE_DEFAULT_CHUNK_SIZE=4,
            )
            app = FastAPI()
            app.state.mongodb = database
            app.include_router(data_router)
            app.dependency_overrides[get_settings] = lambda: settings

            with patch("controllers.BaseController.get_settings", return_value=settings):
                async with AsyncClient(
                    transport=ASGITransport(app=app), base_url="http://test"
                ) as client:
                    filenames = []
                    for index in range(2):
                        content = f"Upload {index}".encode()
                        response = await client.post(
                            "/api/v1/data/upload/demo",
                            files={"file": ("example.txt", content, "text/plain")},
                        )
                        self.assertEqual(response.status_code, 200, response.text)
                        filename = response.json()["file_id"]
                        filenames.append(filename)
                        self.assertEqual(
                            (Path(upload_dir) / "demo" / filename).read_bytes(), content
                        )

            self.assertEqual(len(set(filenames)), 2)
            projects.insert_one.assert_awaited_once()
            self.assertEqual(assets.insert_one.await_count, 2)
            for call, filename in zip(assets.insert_one.await_args_list, filenames):
                document = call.args[0]
                self.assertNotIn("_id", document)
                self.assertEqual(document["asset_project_id"], str(project_id))
                self.assertEqual(document["asset_name"], filename)


if __name__ == "__main__":
    unittest.main()
