import sqlite3
import tempfile
import unittest
from pathlib import Path

from database import LATEST_SCHEMA_VERSION, connect, initialize


class DatabaseSchemaTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.path = Path(self.temporary_directory.name) / "nebula.db"
        self.connection = connect(self.path)

    def tearDown(self):
        self.connection.close()
        self.temporary_directory.cleanup()

    def test_initialization_is_idempotent(self):
        self.assertEqual(initialize(self.connection), LATEST_SCHEMA_VERSION)
        self.assertEqual(initialize(self.connection), LATEST_SCHEMA_VERSION)
        version = self.connection.execute(
            "SELECT MAX(version) FROM schema_migrations"
        ).fetchone()[0]
        self.assertEqual(version, LATEST_SCHEMA_VERSION)

    def test_user_permissions_are_deleted_with_user(self):
        initialize(self.connection)
        with self.connection:
            self.connection.execute(
                "INSERT INTO users(login, password) VALUES (?, ?)", ("alice", "secret")
            )
            self.connection.execute(
                """
                INSERT INTO permissions(user_login, path, readable, writable)
                VALUES (?, ?, ?, ?)
                """,
                ("alice", "/alice", 1, 1),
            )
            self.connection.execute("DELETE FROM users WHERE login = ?", ("alice",))
        count = self.connection.execute(
            "SELECT COUNT(*) FROM permissions"
        ).fetchone()[0]
        self.assertEqual(count, 0)

    def test_file_parts_are_ordered_and_cascade_on_delete(self):
        initialize(self.connection)
        with self.connection:
            cursor = self.connection.execute(
                "INSERT INTO nodes(type, name, parent) VALUES ('file', 'a.bin', '/')"
            )
            node_id = cursor.lastrowid
            self.connection.executemany(
                """
                INSERT INTO file_parts(
                    node_id, part_id, tg_file, tg_message, file_size, chunk_name
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (node_id, 1, "file-b", 12, 5, "part-1"),
                    (node_id, 0, "file-a", 11, 5, "part-0"),
                ],
            )
        parts = self.connection.execute(
            "SELECT part_id FROM file_parts WHERE node_id = ? ORDER BY part_id",
            (node_id,),
        ).fetchall()
        self.assertEqual([row["part_id"] for row in parts], [0, 1])
        with self.connection:
            self.connection.execute("DELETE FROM nodes WHERE id = ?", (node_id,))
        self.assertEqual(
            self.connection.execute("SELECT COUNT(*) FROM file_parts").fetchone()[0],
            0,
        )

    def test_rejects_duplicate_virtual_paths(self):
        initialize(self.connection)
        with self.connection:
            self.connection.execute(
                "INSERT INTO nodes(type, name, parent) VALUES ('dir', 'media', '/')"
            )
        with self.assertRaises(sqlite3.IntegrityError):
            with self.connection:
                self.connection.execute(
                    "INSERT INTO nodes(type, name, parent) VALUES ('dir', 'media', '/')"
                )


if __name__ == "__main__":
    unittest.main()
