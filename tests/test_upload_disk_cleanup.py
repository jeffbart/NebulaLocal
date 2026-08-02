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

    def test_display_destination_hides_ftp_login_root(self):
        self.assertEqual(main.display_destination("/jeffbart/Filmes/1960S"), "/Filmes/1960S/")
        self.assertEqual(main.display_destination("/jeffbart"), "/")
        self.assertEqual(main.display_destination("/"), "/")

    def test_folder_watcher_ignores_ftp_files_until_direct_queueing(self):
        internal = "1790e6bb482b4a528d09132100e5654c_filme.mp4"
        self.assertFalse(main.is_watcher_candidate(internal))
        self.assertFalse(main.is_watcher_candidate(internal + ".partial"))
        self.assertFalse(main.is_watcher_candidate(internal + ".ftpready"))
        self.assertTrue(main.is_watcher_candidate("arquivo_colocado_manualmente.mp4"))

    def test_garbage_collector_protects_waiting_queue_paths(self):
        queue = asyncio.Queue()
        queue.put_nowait({"path": os.path.join("staging", "aguardando.mkv")})
        protected = main.protected_upload_paths(queue)
        expected = os.path.normcase(os.path.abspath(os.path.join("staging", "aguardando.mkv")))
        self.assertIn(expected, protected)

    def test_queue_report_uses_telegram_progress_layout(self):
        report = main.format_queue_report(
            [],
            [{
                "name": "0123456789abcdef0123456789abcdef_filme.mkv",
                "size": 10 * 1024 ** 3,
                "parts": [{"file_size": 4 * 1024 ** 3}],
            }],
            [],
            [],
        )
        self.assertIn("📋 Fila do NebulaFTP", report)
        self.assertIn("📤 Em processamento (1)", report)
        self.assertIn("1. filme.mkv\n— 4 GB de 10 GB", report)
        self.assertNotIn("Aguardando", report)
        self.assertNotIn("Com falha", report)

    def test_queue_report_lists_every_nonempty_state(self):
        document = {"name": "arquivo.mkv", "size": 1024, "parts": []}
        report = main.format_queue_report(
            [document], [document], [document], [document]
        )
        self.assertIn("📥 Na fila (1)", report)
        self.assertIn("📤 Em processamento (1)", report)
        self.assertIn("⏳ Aguardando (1)", report)
        self.assertIn("❌ Com falha (1)", report)

    async def test_restores_pending_uploads_after_restart(self):
        class Cursor:
            def __init__(self, documents):
                self.documents = iter(documents)
            def __aiter__(self):
                return self
            async def __anext__(self):
                try:
                    return next(self.documents)
                except StopIteration:
                    raise StopAsyncIteration

        class Files:
            def __init__(self, documents):
                self.documents = documents
                self.updates = []
            def find(self, query):
                statuses = query["status"]["$in"]
                return Cursor([d for d in self.documents if d["status"] in statuses])
            async def update_one(self, query, update):
                self.updates.append((query, update))

        with tempfile.TemporaryDirectory() as directory:
            existing = os.path.join(directory, "arquivo.mkv")
            with open(existing, "wb") as stream:
                stream.write(b"conteudo")
            documents = [
                {"_id": 1, "name": "arquivo.mkv", "parent": "/user", "size": 8, "status": "staging", "local_path": existing},
                {"_id": 2, "name": "ausente.mkv", "parent": "/user", "size": 10, "status": "uploading", "local_path": os.path.join(directory, "ausente.mkv")},
            ]
            files = Files(documents)
            queue = asyncio.Queue()

            restored, missing = await main.restore_pending_uploads(
                SimpleNamespace(files=files), queue
            )

            self.assertEqual((restored, missing), (1, 1))
            self.assertEqual((await queue.get())["filename"], "arquivo.mkv")
            self.assertEqual(files.updates[0][1]["$set"]["status"], "failed")

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
                    "Pasta: /\nArquivo: arquivo.bin\nParte: 01 de 03\n"
                    "Enviado: 2 B de 10 B (20.0%)",
                    "Pasta: /\nArquivo: arquivo.bin\nParte: 02 de 03\n"
                    "Enviado: 6 B de 10 B (60.0%)",
                    "Pasta: /\nArquivo: arquivo.bin\nParte: 03 de 03\n"
                    "Enviado: 10 B de 10 B (100.0%)",
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
