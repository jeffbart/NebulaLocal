import asyncio
import tempfile
import unittest
from pathlib import Path

from sqlite_backend import SQLiteDatabase, SQLiteUserStore


class SQLiteBackendTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.path = Path(self.temporary_directory.name) / "backend.db"

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_user_store_and_async_user_lookup_share_schema(self):
        store = SQLiteUserStore(self.path)
        store.insert_one(
            {
                "login": "alice",
                "password": "secret",
                "permissions": [
                    {"path": "/media", "readable": True, "writable": False}
                ],
            }
        )
        database = SQLiteDatabase(self.path)
        user = asyncio.run(database.users.find_one({"login": "alice"}))
        self.assertEqual(user["password"], "secret")
        self.assertEqual(user["permissions"][0]["path"], "/media")
        database.close()
        store.connection.close()

    def test_file_parts_round_trip(self):
        database = SQLiteDatabase(self.path)

        async def scenario():
            inserted = await database.files.insert_one(
                {
                    "type": "file",
                    "name": "movie.bin",
                    "parent": "/alice",
                    "size": 10,
                    "ctime": 100,
                    "mtime": 100,
                    "parts": [],
                    "uploadId": "pending",
                }
            )
            await database.files.update_one(
                {"_id": inserted.inserted_id},
                {
                    "$set": {
                        "status": "completed",
                        "parts": [
                            {
                                "part_id": 0,
                                "tg_file": "telegram-file",
                                "tg_message": 99,
                                "file_size": 10,
                                "chunk_name": "part-000",
                            }
                        ],
                    },
                    "$unset": {"uploadId": 1},
                },
            )
            return await database.files.find_one({"_id": inserted.inserted_id})

        document = asyncio.run(scenario())
        self.assertEqual(document["status"], "completed")
        self.assertNotIn("upload_id", document)
        self.assertEqual(document["parts"][0]["tg_file"], "telegram-file")
        database.close()

    def test_virtual_directory_listing_hides_partial_files(self):
        database = SQLiteDatabase(self.path)

        async def scenario():
            for name in ("ready.txt", "upload.partial"):
                await database.files.insert_one(
                    {
                        "type": "file",
                        "name": name,
                        "parent": "/alice",
                        "size": 0,
                        "parts": [],
                    }
                )
            return [
                document["name"]
                async for document in database.files.find(
                    {
                        "parent": "/alice",
                        "name": {"$not": {"$regex": r"\.partial$"}},
                    }
                )
            ]

        self.assertEqual(asyncio.run(scenario()), ["ready.txt"])
        database.close()


if __name__ == "__main__":
    unittest.main()
