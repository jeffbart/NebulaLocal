import asyncio
import ftplib
import tempfile
import unittest
from pathlib import Path

import main
from ftp import MongoDBPathIO, MongoDBUserManager, Server
from sqlite_backend import SQLiteDatabase, SQLiteUserStore


class FTPSQLiteIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.path = Path(self.temporary_directory.name) / "ftp.db"
        store = SQLiteUserStore(self.path)
        store.insert_one(
            {"login": "alice", "password": "secret", "permissions": []}
        )
        store.connection.close()

        self.database = SQLiteDatabase(self.path)
        MongoDBPathIO.db = self.database
        self.server = Server(MongoDBUserManager(self.database), MongoDBPathIO)
        main.enable_utf8_ftp_commands(self.server)
        await self.server.start("127.0.0.1", 0)

    async def asyncTearDown(self):
        await self.server.close()
        self.database.close()
        self.temporary_directory.cleanup()

    async def test_login_uses_user_stored_in_sqlite(self):
        port = self.server.server_port

        def login():
            client = ftplib.FTP()
            welcome = client.connect("127.0.0.1", port, timeout=5)
            response = client.login("alice", "secret")
            current_directory = client.pwd()
            client.quit()
            return welcome, response, current_directory

        welcome, response, current_directory = await asyncio.to_thread(login)
        self.assertTrue(welcome.startswith("220"))
        self.assertTrue(response.startswith("230"))
        self.assertEqual(current_directory, "/alice")

    async def test_server_advertises_and_accepts_utf8(self):
        port = self.server.server_port

        def negotiate_utf8():
            client = ftplib.FTP()
            client.connect("127.0.0.1", port, timeout=5)
            features = client.sendcmd("FEAT")
            response = client.sendcmd("OPTS UTF8 ON")
            client.quit()
            return features, response

        features, response = await asyncio.to_thread(negotiate_utf8)
        self.assertIn("UTF8", features)
        self.assertTrue(response.startswith("200"))


if __name__ == "__main__":
    unittest.main()
