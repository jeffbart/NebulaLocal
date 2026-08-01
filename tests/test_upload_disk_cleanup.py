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
        self.captions = []

    async def send_document(self, **kwargs):
        self.sizes_at_send.append(os.path.getsize(self.local_path))
        self.captions.append(kwargs["caption"])
        part_id = len(self.sizes_at_send)
        return SimpleNamespace(
            id=part_id,
            document=SimpleNamespace(file_id=f"telegram-{part_id}"),
        )


class UploadDiskCleanupTests(unittest.IsolatedAsyncioTestCase):
    def test_display_filename_only_removes_internal_hex_prefix(self):
        self.assertEqual(
            main.display_filename("7e61363d2ef04b099d4d3034c3d50a4f_filme.mkv"),
            "filme.mkv",
        )
        self.assertEqual(
            main.display_filename("backup_2026_filme.mkv"),
            "backup_2026_filme.mkv",
        )

    def test_folder_watcher_ignores_ftp_files_until_direct_queueing(self):
        internal = "1790e6bb482b4a528d09132100e5654c_filme.mp4"
        self.assertFalse(main.is_watcher_candidate(internal))
        self.assertFalse(main.is_watcher_candidate(internal + ".partial"))
        self.assertFalse(main.is_watcher_candidate(internal + ".ftpready"))
        self.assertTrue(main.is_watcher_candidate("arquivo_colocado_manualmente.mp4"))

    async def test_reclaims_each_confirmed_part_and_keeps_metadata_ordered(self):
        with tempfile.TemporaryDirectory() as directory:
            internal_filename = "7e61363d2ef04b099d4d3034c3d50a4f_arquivo.bin"
            local_path = os.path.join(directory, internal_filename)
            with open(local_path, "wb") as stream:
                stream.write(b"0123456789")

            document = {
                "_id": 1,
                "name": internal_filename,
                "parent": "/user",
                "size": 10,
                "parts": [],
            }
            mongo = SimpleNamespace(files=FakeFiles(document))
            bot = FakeBot(local_path)
            await main.UPLOAD_QUEUE.put({
                "path": local_path,
                "filename": internal_filename,
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
            self.assertEqual(
                bot.captions,
                [
                    "Arquivo: arquivo.bin\nParte: 01 de 03\n"
                    "Tamanho total: 10 B\nEnviado: 2 B de 10 B (20.0%)",
                    "Arquivo: arquivo.bin\nParte: 02 de 03\n"
                    "Tamanho total: 10 B\nEnviado: 6 B de 10 B (60.0%)",
                    "Arquivo: arquivo.bin\nParte: 03 de 03\n"
                    "Tamanho total: 10 B\nEnviado: 10 B de 10 B (100.0%)",
                ],
            )
            self.assertFalse(os.path.exists(local_path))
            self.assertEqual(document["status"], "completed")
            self.assertEqual(document["size"], 10)
            self.assertEqual(
                [part["part_id"] for part in document["parts"]],
                [0, 1, 2],
            )


if __name__ == "__main__":
    unittest.main()
