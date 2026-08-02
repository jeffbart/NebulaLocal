"""Gera uma arvore do acervo virtual armazenado no SQLite do Nebula Local."""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path, PurePosixPath


DEFAULT_DATABASE = Path(os.environ.get("SQLITE_PATH", "data/nebula.db"))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def format_size(size_bytes: int) -> str:
    size = float(size_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.2f}".rstrip("0").rstrip(".") + f" {unit}"
        size /= 1024
    return f"{size_bytes} B"


def node_path(parent: str, name: str) -> str:
    return str(PurePosixPath(parent) / name)


def read_nodes(database: Path) -> list[dict]:
    if not database.is_file():
        raise FileNotFoundError(f"Banco SQLite nao encontrado: {database}")

    uri = database.resolve().as_uri() + "?mode=ro"
    connection = sqlite3.connect(uri, uri=True, timeout=30)
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute(
            """
            SELECT id, type, name, parent, size, status
            FROM nodes
            ORDER BY name COLLATE NOCASE, id
            """
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def render_collection(nodes: list[dict]) -> str:
    children = defaultdict(list)
    directories = {"/"}
    for node in nodes:
        children[node["parent"]].append(node)
        if node["type"] == "dir":
            directories.add(node_path(node["parent"], node["name"]))

    for entries in children.values():
        entries.sort(
            key=lambda item: (item["type"] != "file", item["name"].casefold(), item["id"])
        )

    lines = ["ACERVO DO NEBULA LOCAL", "=" * 23]
    visited = set()

    def walk(parent: str, depth: int) -> None:
        for node in children.get(parent, []):
            if node["id"] in visited:
                continue
            visited.add(node["id"])
            indent = "    " * depth
            if node["type"] == "dir":
                lines.append(f"{indent}{node['name']}/")
                walk(node_path(node["parent"], node["name"]), depth + 1)
            else:
                status = node.get("status") or "sem status"
                lines.append(
                    f"{indent}{node['name']} — {format_size(node['size'])} — {status}"
                )

    walk("/", 0)

    unreachable = [node for node in nodes if node["id"] not in visited]
    if unreachable:
        lines.extend(("", "ITENS FORA DA ARVORE", "=" * 20))
        for node in unreachable:
            kind = "pasta" if node["type"] == "dir" else "arquivo"
            lines.append(
                f"[{kind}] {node_path(node['parent'], node['name'])} "
                f"(pai registrado: {node['parent']})"
            )

    files = [node for node in nodes if node["type"] == "file"]
    folders = [node for node in nodes if node["type"] == "dir"]
    lines.extend(
        (
            "",
            "RESUMO",
            "=" * 6,
            f"Pastas: {len(folders)}",
            f"Arquivos: {len(files)}",
            f"Tamanho virtual total: {format_size(sum(node['size'] for node in files))}",
            f"Itens fora da arvore: {len(unreachable)}",
        )
    )
    return "\n".join(lines) + "\n"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--banco",
        type=Path,
        default=DEFAULT_DATABASE,
        help="caminho do banco SQLite (padrao: data/nebula.db)",
    )
    parser.add_argument(
        "--saida",
        type=Path,
        help="salva uma copia UTF-8 do relatorio neste arquivo",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    try:
        report = render_collection(read_nodes(args.banco))
    except (FileNotFoundError, sqlite3.Error) as exc:
        print(f"ERRO: {exc}")
        return 1

    print(report, end="")
    if args.saida:
        args.saida.parent.mkdir(parents=True, exist_ok=True)
        args.saida.write_text(report, encoding="utf-8-sig")
        print(f"\nRelatorio salvo em: {args.saida.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
