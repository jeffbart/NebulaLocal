"""Create or upgrade the Nebula Local SQLite database."""

from database import database_path, open_database


def main() -> None:
    path = database_path().resolve()
    with open_database(path) as connection:
        version = connection.execute(
            "SELECT MAX(version) FROM schema_migrations"
        ).fetchone()[0]
    print(f"SQLite pronto: {path} (schema v{version})")


if __name__ == "__main__":
    main()
