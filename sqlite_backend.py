"""Async compatibility layer backed by Nebula's SQLite schema.

The FTP implementation historically talks to Motor collections.  These small
collection objects preserve that internal protocol while all durable data is
stored relationally in SQLite.
"""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from threading import RLock
from typing import Any, AsyncIterator

from database import connect, database_path, initialize


@dataclass
class InsertOneResult:
    inserted_id: int | str


class AsyncCursor(AsyncIterator[dict[str, Any]]):
    def __init__(self, rows: list[dict[str, Any]]):
        self._rows = iter(rows)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self._rows)
        except StopIteration as exc:
            raise StopAsyncIteration from exc


class SQLiteUsersCollection:
    def __init__(self, connection: sqlite3.Connection, lock: RLock):
        self.connection = connection
        self.lock = lock

    def _document(self, login: str) -> dict[str, Any] | None:
        row = self.connection.execute(
            "SELECT login, password FROM users WHERE login = ?", (login,)
        ).fetchone()
        if row is None:
            return None
        permissions = self.connection.execute(
            """
            SELECT path, readable, writable
            FROM permissions WHERE user_login = ? ORDER BY id
            """,
            (login,),
        ).fetchall()
        return {
            "_id": row["login"],
            "login": row["login"],
            "password": row["password"],
            "permissions": [
                {
                    "path": permission["path"],
                    "readable": bool(permission["readable"]),
                    "writable": bool(permission["writable"]),
                }
                for permission in permissions
            ],
        }

    async def find_one(self, query: dict[str, Any]) -> dict[str, Any] | None:
        with self.lock:
            if query.get("login"):
                return self._document(str(query["login"]))
            row = self.connection.execute(
                "SELECT login FROM users ORDER BY login LIMIT 1"
            ).fetchone()
            return self._document(row["login"]) if row else None

    async def create_index(self, *args, **kwargs):
        return None


class SQLiteFilesCollection:
    def __init__(self, connection: sqlite3.Connection, lock: RLock):
        self.connection = connection
        self.lock = lock

    def _parts(self, node_id: int) -> list[dict[str, Any]]:
        rows = self.connection.execute(
            """
            SELECT part_id, tg_file, tg_message, file_size, chunk_name
            FROM file_parts WHERE node_id = ? ORDER BY part_id
            """,
            (node_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def _document(self, row: sqlite3.Row | None) -> dict[str, Any] | None:
        if row is None:
            return None
        document = dict(row)
        document["_id"] = document.pop("id")
        document["parts"] = self._parts(document["_id"])
        return {key: value for key, value in document.items() if value is not None}

    def _find_row(self, query: dict[str, Any]) -> sqlite3.Row | None:
        if "_id" in query:
            return self.connection.execute(
                "SELECT * FROM nodes WHERE id = ?", (query["_id"],)
            ).fetchone()
        if "name" in query and "parent" in query:
            return self.connection.execute(
                "SELECT * FROM nodes WHERE name = ? AND parent = ?",
                (query["name"], query["parent"]),
            ).fetchone()
        raise ValueError(f"consulta SQLite não suportada: {query!r}")

    async def find_one(self, query: dict[str, Any]) -> dict[str, Any] | None:
        with self.lock:
            return self._document(self._find_row(query))

    def find(self, query: dict[str, Any]) -> AsyncCursor:
        with self.lock:
            if set(query) == {"status"}:
                status_filter = query["status"]
                statuses = status_filter.get("$in", []) if isinstance(status_filter, dict) else [status_filter]
                if not statuses:
                    rows = []
                else:
                    placeholders = ", ".join("?" for _ in statuses)
                    rows = self.connection.execute(
                        f"SELECT * FROM nodes WHERE status IN ({placeholders}) ORDER BY mtime, name COLLATE NOCASE",
                        list(statuses),
                    ).fetchall()
            elif set(query).issubset({"parent", "name"}) and "parent" in query:
                sql = "SELECT * FROM nodes WHERE parent = ?"
                parameters: list[Any] = [query["parent"]]
                name_filter = query.get("name")
                if isinstance(name_filter, dict) and "$not" in name_filter:
                    pattern = name_filter["$not"].get("$regex")
                    if pattern == r"\.partial$":
                        sql += " AND name NOT LIKE ?"
                        parameters.append("%.partial")
                sql += " ORDER BY name COLLATE NOCASE"
                rows = self.connection.execute(sql, parameters).fetchall()
            else:
                raise ValueError(f"consulta SQLite não suportada: {query!r}")
            return AsyncCursor([self._document(row) for row in rows])

    def _store_parts(self, node_id: int, parts: list[dict[str, Any]]) -> None:
        self.connection.execute("DELETE FROM file_parts WHERE node_id = ?", (node_id,))
        self.connection.executemany(
            """
            INSERT INTO file_parts(
                node_id, part_id, tg_file, tg_message, file_size, chunk_name
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    node_id,
                    part["part_id"],
                    part["tg_file"],
                    part["tg_message"],
                    part["file_size"],
                    part["chunk_name"],
                )
                for part in parts
            ],
        )

    def _write_document(self, document: dict[str, Any], *, replace: bool) -> int:
        values = dict(document)
        values.pop("_id", None)
        parts = values.pop("parts", None)
        columns = (
            "type",
            "name",
            "parent",
            "size",
            "ctime",
            "mtime",
            "status",
            "local_path",
            "upload_id",
            "uploaded_at",
            "upload_started_at",
            "obfuscated_id",
        )
        aliases = {"uploadId": "upload_id"}
        normalized = {aliases.get(key, key): value for key, value in values.items()}
        existing = self.connection.execute(
            "SELECT id FROM nodes WHERE name = ? AND parent = ?",
            (normalized["name"], normalized["parent"]),
        ).fetchone()

        if existing and replace:
            assignments = ", ".join(f"{column} = ?" for column in columns)
            data = [normalized.get(column) for column in columns]
            self.connection.execute(
                f"UPDATE nodes SET {assignments} WHERE id = ?",
                (*data, existing["id"]),
            )
            node_id = existing["id"]
        elif existing:
            raise sqlite3.IntegrityError("virtual path already exists")
        else:
            present = [column for column in columns if column in normalized]
            placeholders = ", ".join("?" for _ in present)
            cursor = self.connection.execute(
                f"INSERT INTO nodes({', '.join(present)}) VALUES ({placeholders})",
                [normalized[column] for column in present],
            )
            node_id = int(cursor.lastrowid)
        if parts is not None:
            self._store_parts(node_id, parts)
        return node_id

    async def insert_one(self, document: dict[str, Any]) -> InsertOneResult:
        with self.lock, self.connection:
            return InsertOneResult(self._write_document(document, replace=False))

    async def replace_one(
        self, query: dict[str, Any], document: dict[str, Any], upsert: bool = False
    ):
        with self.lock, self.connection:
            existing = self._find_row(query)
            if existing is None and not upsert:
                return None
            return self._write_document(document, replace=existing is not None)

    async def update_one(
        self,
        query: dict[str, Any],
        update: dict[str, Any],
        upsert: bool = False,
    ):
        with self.lock, self.connection:
            row = self._find_row(query)
            if row is None:
                if not upsert:
                    return None
                document = dict(query)
                document.update(update.get("$setOnInsert", {}))
                document.update(update.get("$set", {}))
                return self._write_document(document, replace=False)

            document = self._document(row)
            assert document is not None
            document.update(update.get("$set", {}))
            for key in update.get("$unset", {}):
                document.pop(key, None)
                document.pop({"uploadId": "upload_id"}.get(key, key), None)
            return self._write_document(document, replace=True)

    async def delete_one(self, query: dict[str, Any]):
        with self.lock, self.connection:
            row = self._find_row(query)
            if row:
                self.connection.execute("DELETE FROM nodes WHERE id = ?", (row["id"],))

    async def delete_many(self, query: dict[str, Any]):
        parent = query.get("parent")
        if not isinstance(parent, dict) or "$regex" not in parent:
            raise ValueError(f"remoção SQLite não suportada: {query!r}")
        prefix = re.sub(r"^\^", "", parent["$regex"])
        with self.lock, self.connection:
            self.connection.execute(
                "DELETE FROM nodes WHERE parent = ? OR parent LIKE ?",
                (prefix, f"{prefix}/%"),
            )

    async def create_index(self, *args, **kwargs):
        return None

    async def stats(self) -> dict[str, int]:
        """Aggregate counts for the /resume report: queue size, folder/file
        totals and bytes already archived on Telegram."""
        with self.lock:
            row = self.connection.execute(
                """
                SELECT
                    SUM(CASE WHEN status IN ('staging', 'uploading') THEN 1 ELSE 0 END)
                        AS queued_files,
                    SUM(CASE WHEN type = 'dir' THEN 1 ELSE 0 END) AS folders,
                    SUM(CASE WHEN type = 'file' AND status = 'completed' THEN 1 ELSE 0 END)
                        AS files,
                    SUM(CASE WHEN type = 'file' AND status = 'completed' THEN size ELSE 0 END)
                        AS total_size
                FROM nodes
                """
            ).fetchone()
        return {key: row[key] or 0 for key in row.keys()}


class SQLiteDatabase:
    def __init__(self, path: str | Path | None = None):
        self.connection = connect(path)
        initialize(self.connection)
        self.lock = RLock()
        self.users = SQLiteUsersCollection(self.connection, self.lock)
        self.files = SQLiteFilesCollection(self.connection, self.lock)

    def close(self):
        self.connection.close()


class SQLiteUserStore:
    """Synchronous user collection used by accounts_manager.py."""

    def __init__(self, path: str | Path | None = None):
        self.connection = connect(path)
        initialize(self.connection)
        self.collection = SQLiteUsersCollection(self.connection, RLock())

    def _document(self, login: str):
        return self.collection._document(login)

    def find(self, query: dict[str, Any]):
        if query.get("login"):
            document = self._document(str(query["login"]))
            return [document] if document else []
        rows = self.connection.execute("SELECT login FROM users ORDER BY login").fetchall()
        return [self._document(row["login"]) for row in rows]

    def insert_one(self, document: dict[str, Any]):
        with self.connection:
            self.connection.execute(
                "INSERT INTO users(login, password) VALUES (?, ?)",
                (document["login"], document["password"]),
            )
            self._replace_permissions(document["login"], document.get("permissions", []))
        return InsertOneResult(document["login"])

    def _replace_permissions(self, login: str, permissions: list[dict[str, Any]]):
        self.connection.execute(
            "DELETE FROM permissions WHERE user_login = ?", (login,)
        )
        self.connection.executemany(
            """
            INSERT INTO permissions(user_login, path, readable, writable)
            VALUES (?, ?, ?, ?)
            """,
            [
                (
                    login,
                    permission["path"],
                    int(bool(permission.get("readable") or permission.get("writable"))),
                    int(bool(permission.get("writable"))),
                )
                for permission in permissions
            ],
        )

    def update_one(self, query: dict[str, Any], update: dict[str, Any]):
        login = str(query["login"])
        document = self._document(login)
        if document is None:
            return None
        changed = update.get("$set", {})
        if "password" in changed:
            document["password"] = changed["password"]
        for key, value in changed.items():
            match = re.fullmatch(r"permissions\.(\d+)\.(readable|writable)", key)
            if match:
                index, field = int(match.group(1)), match.group(2)
                document["permissions"][index][field] = bool(value)
                if field == "writable" and value:
                    document["permissions"][index]["readable"] = True
        if "$push" in update:
            document["permissions"].append(update["$push"]["permissions"])
        if "$pull" in update:
            path = update["$pull"]["permissions"]["path"]
            document["permissions"] = [
                permission
                for permission in document["permissions"]
                if permission["path"] != path
            ]
        with self.connection:
            self.connection.execute(
                """
                UPDATE users
                SET password = ?,
                    updated_at = CAST(strftime('%s', 'now') AS INTEGER)
                WHERE login = ?
                """,
                (document["password"], login),
            )
            self._replace_permissions(login, document["permissions"])

    def delete_one(self, query: dict[str, Any]):
        with self.connection:
            self.connection.execute(
                "DELETE FROM users WHERE login = ?", (query["login"],)
            )


class AsyncIOMotorClient:
    """Drop-in constructor used by the legacy bootstrap code."""

    def __init__(self, *args, **kwargs):
        self.ftp = SQLiteDatabase(database_path())

    def close(self):
        self.ftp.close()
