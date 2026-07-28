"""SQLite persistence for Nebula Local.

This module owns the database schema and connection defaults.  Keeping schema
creation here makes startup and future migrations deterministic.
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


DEFAULT_DATABASE_PATH = Path("data") / "nebula.db"
LATEST_SCHEMA_VERSION = 1

MIGRATIONS = {
    1: """
        CREATE TABLE IF NOT EXISTS users (
            login TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            created_at INTEGER NOT NULL
                DEFAULT (CAST(strftime('%s', 'now') AS INTEGER)),
            updated_at INTEGER NOT NULL
                DEFAULT (CAST(strftime('%s', 'now') AS INTEGER)),
            CHECK (length(login) BETWEEN 1 AND 64)
        ) STRICT;

        CREATE TABLE IF NOT EXISTS permissions (
            id INTEGER PRIMARY KEY,
            user_login TEXT NOT NULL
                REFERENCES users(login) ON UPDATE CASCADE ON DELETE CASCADE,
            path TEXT NOT NULL,
            readable INTEGER NOT NULL DEFAULT 0 CHECK (readable IN (0, 1)),
            writable INTEGER NOT NULL DEFAULT 0 CHECK (writable IN (0, 1)),
            UNIQUE (user_login, path),
            CHECK (substr(path, 1, 1) = '/'),
            CHECK (writable = 0 OR readable = 1)
        ) STRICT;

        CREATE TABLE IF NOT EXISTS nodes (
            id INTEGER PRIMARY KEY,
            type TEXT NOT NULL CHECK (type IN ('file', 'dir')),
            name TEXT NOT NULL,
            parent TEXT NOT NULL DEFAULT '/',
            size INTEGER NOT NULL DEFAULT 0 CHECK (size >= 0),
            ctime INTEGER NOT NULL
                DEFAULT (CAST(strftime('%s', 'now') AS INTEGER)),
            mtime INTEGER NOT NULL
                DEFAULT (CAST(strftime('%s', 'now') AS INTEGER)),
            status TEXT CHECK (
                status IS NULL OR status IN ('staging', 'uploading', 'completed', 'failed')
            ),
            local_path TEXT,
            upload_id TEXT,
            uploaded_at INTEGER,
            obfuscated_id TEXT,
            UNIQUE (parent, name),
            CHECK (substr(parent, 1, 1) = '/'),
            CHECK (name <> '')
        ) STRICT;

        CREATE TABLE IF NOT EXISTS file_parts (
            id INTEGER PRIMARY KEY,
            node_id INTEGER NOT NULL
                REFERENCES nodes(id) ON DELETE CASCADE,
            part_id INTEGER NOT NULL CHECK (part_id >= 0),
            tg_file TEXT NOT NULL,
            tg_message INTEGER NOT NULL,
            file_size INTEGER NOT NULL CHECK (file_size >= 0),
            chunk_name TEXT NOT NULL,
            UNIQUE (node_id, part_id)
        ) STRICT;

        CREATE INDEX IF NOT EXISTS idx_permissions_user ON permissions(user_login);
        CREATE INDEX IF NOT EXISTS idx_nodes_parent ON nodes(parent);
        CREATE INDEX IF NOT EXISTS idx_nodes_upload_id
            ON nodes(upload_id) WHERE upload_id IS NOT NULL;
        CREATE INDEX IF NOT EXISTS idx_nodes_uploaded_at
            ON nodes(uploaded_at) WHERE uploaded_at IS NOT NULL;
        CREATE INDEX IF NOT EXISTS idx_nodes_status
            ON nodes(status) WHERE status IS NOT NULL;
        CREATE INDEX IF NOT EXISTS idx_file_parts_node ON file_parts(node_id, part_id);
    """,
}


def database_path(value: str | os.PathLike[str] | None = None) -> Path:
    """Return the configured database path without creating it."""
    configured = value if value is not None else os.environ.get("SQLITE_PATH")
    return Path(configured) if configured else DEFAULT_DATABASE_PATH


def connect(value: str | os.PathLike[str] | None = None) -> sqlite3.Connection:
    """Open a configured connection with Nebula's required SQLite settings."""
    path = database_path(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    connection.execute("PRAGMA synchronous = NORMAL")
    connection.execute("PRAGMA busy_timeout = 30000")
    return connection


def initialize(connection: sqlite3.Connection) -> int:
    """Apply every pending schema migration and return the schema version."""
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            applied_at INTEGER NOT NULL
                DEFAULT (CAST(strftime('%s', 'now') AS INTEGER))
        ) STRICT
        """
    )
    applied = {
        row[0] for row in connection.execute("SELECT version FROM schema_migrations")
    }
    unknown = applied.difference(MIGRATIONS)
    if unknown:
        raise RuntimeError(f"database has unknown migration(s): {sorted(unknown)}")

    for version in sorted(MIGRATIONS):
        if version in applied:
            continue
        with connection:
            connection.executescript(MIGRATIONS[version])
            connection.execute(
                """
                INSERT INTO schema_migrations(version, applied_at)
                VALUES (?, CAST(strftime('%s', 'now') AS INTEGER))
                """,
                (version,),
            )
    return LATEST_SCHEMA_VERSION


@contextmanager
def open_database(
    value: str | os.PathLike[str] | None = None,
) -> Iterator[sqlite3.Connection]:
    """Open, initialize, and reliably close the application database."""
    connection = connect(value)
    try:
        initialize(connection)
        yield connection
    finally:
        connection.close()
