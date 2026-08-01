import asyncio
import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import main


class FakeFiles:
    def __init__(self, document):
        self.document = document
        self.updates = []

    async def find_one(self, query):
        return self.document

    async def update_one(self, query, update):
        self.updates.append(update)
        self.document.update(update.get("$set", {}))
        for key in update.get("$unset", {}):
            self.document.pop(key, None)


class FakeBot:
    def __init__(self, local_path):
        self.local_path = local_path
        self.sizes_at_send = []

    async def send_document(self, **kwargs):
        self.sizes_at_send.append(os.path.getsize(self.local_path))
        part_id = len(self.sizes_at_send)
        return SimpleNamespace(
            id=part_id,
            document=SimpleNamespace(file_id=f"telegram-{part_id}"),
        )


class UploadDiskCleanupTests(unittest.IsolatedAsyncioTestCase):
    async def test_reclaims_each_confirmed_part_and_keeps_metadata_ordered(self):
        with tempfile.TemporaryDirectory() as directory:
            local_path = os.path.join(directory, "arquivo.bin")
            with open(local_path, "wb") as stream:
                stream.write(b"0123456789")

            document = {
                "_id": 1,
                "name": "arquivo.bin",
                "parent": "/user",
                "size": 10,
                "parts": [],
            }
            mongo = SimpleNamespace(files=FakeFiles(document))
            bot = FakeBot(local_path)
            await main.UPLOAD_QUEUE.put({
                "path": local_path,
                "filename": "arquivo.bin",
                "parent": "/user",
                "size": 10,
            })

            with (
                patch.object(main, "CHUNK_SIZE", 4),
                patch.object(main, "MAX_RETRIES", 1),
                patch.object(main.logger, "disabled", True),
            ):
                worker = asyncio.create_task(main.upload_worker(bot, 123, mongo, 1))
                await asyncio.wait_for(main.UPLOAD_QUEUE.join(), timeout=2)
                worker.cancel()
                with self.assertRaises(asyncio.CancelledError):
                    await worker

            self.assertEqual(bot.sizes_at_send, [10, 8, 4])
            self.assertFalse(os.path.exists(local_path))
            self.assertEqual(document["status"], "completed")
            self.assertEqual(document["size"], 10)
            self.assertEqual(
                [part["part_id"] for part in document["parts"]],
                [0, 1, 2],
            )


if __name__ == "__main__":
    unittest.main()
