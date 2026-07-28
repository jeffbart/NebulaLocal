"""Assistente local para configurar e validar o Telegram do Nebula."""

from __future__ import annotations

import getpass
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ENV_FILE = Path(__file__).with_name(".env")
EXAMPLE_FILE = Path(__file__).with_name(".env.example")


def api_call(token: str, method: str, **parameters):
    url = f"https://api.telegram.org/bot{token}/{method}"
    if parameters:
        query = urllib.parse.urlencode(parameters)
        url = f"{url}?{query}"
    try:
        with urllib.request.urlopen(url, timeout=20) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        try:
            detail = json.load(exc)["description"]
        except Exception:
            detail = str(exc)
        raise RuntimeError(detail) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"não foi possível acessar o Telegram: {exc.reason}") from exc
    if not payload.get("ok"):
        raise RuntimeError(payload.get("description", "resposta inválida do Telegram"))
    return payload["result"]


def read_values() -> dict[str, str]:
    if not ENV_FILE.exists():
        return {}
    values = {}
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        if not line or line.lstrip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def write_values(changes: dict[str, str]) -> None:
    if ENV_FILE.exists():
        lines = ENV_FILE.read_text(encoding="utf-8").splitlines()
    else:
        lines = EXAMPLE_FILE.read_text(encoding="utf-8").splitlines()

    pending = dict(changes)
    output = []
    for line in lines:
        if "=" in line and not line.lstrip().startswith("#"):
            key = line.split("=", 1)[0].strip()
            if key in pending:
                line = f"{key}={pending.pop(key)}"
        output.append(line)
    if pending:
        output.extend(["", "# Configuração adicionada pelo assistente"])
        output.extend(f"{key}={value}" for key, value in pending.items())
    ENV_FILE.write_text("\n".join(output) + "\n", encoding="utf-8")


def prompt(label: str, current: str = "", *, secret: bool = False) -> str:
    suffix = " [manter atual]" if current else ""
    reader = getpass.getpass if secret else input
    value = reader(f"{label}{suffix}: ").strip()
    return value or current


def configure() -> int:
    print("=== Configuração Telegram do Nebula Local ===")
    print("Obtenha API_ID/API_HASH em https://my.telegram.org")
    print("Crie o bot oficial em https://t.me/BotFather usando /newbot.\n")

    current = read_values()
    api_id = prompt("API_ID", current.get("API_ID", ""))
    if not api_id.isdigit():
        print("ERRO: API_ID deve conter apenas números.")
        return 1

    api_hash = prompt("API_HASH", current.get("API_HASH", ""), secret=True)
    if not re.fullmatch(r"[0-9a-fA-F]{32}", api_hash):
        print("ERRO: API_HASH deve possuir 32 caracteres hexadecimais.")
        return 1

    old_token = (current.get("BOT_TOKENS") or current.get("BOT_TOKEN") or "").split(",")[0]
    token = prompt("Token fornecido pelo BotFather", old_token, secret=True)
    try:
        bot = api_call(token, "getMe")
    except RuntimeError as exc:
        print(f"ERRO: token recusado: {exc}")
        return 1
    print(f"Bot confirmado: @{bot['username']} (ID {bot['id']})")

    chat_id = prompt("CHAT_ID do canal (incluindo -100)", current.get("CHAT_ID", ""))
    if not re.fullmatch(r"-100\d+", chat_id):
        print("ERRO: CHAT_ID de canal deve começar com -100.")
        return 1
    try:
        chat = api_call(token, "getChat", chat_id=chat_id)
    except RuntimeError as exc:
        print(f"ERRO: canal não acessível pelo bot: {exc}")
        print("Adicione o bot como administrador do canal e tente novamente.")
        return 1

    write_values(
        {
            "API_ID": api_id,
            "API_HASH": api_hash,
            "BOT_TOKENS": token,
            "CHAT_ID": chat_id,
        }
    )
    print(f"Canal confirmado: {chat.get('title', chat_id)}")
    print(f"Configuração salva em: {ENV_FILE.resolve()}")
    return 0


def check() -> int:
    values = read_values()
    missing = [
        key
        for key in ("API_ID", "API_HASH", "BOT_TOKENS", "CHAT_ID")
        if not values.get(key)
    ]
    if missing:
        print("Configuração incompleta: " + ", ".join(missing))
        return 1
    token = values["BOT_TOKENS"].split(",")[0].strip()
    try:
        bot = api_call(token, "getMe")
        chat = api_call(token, "getChat", chat_id=values["CHAT_ID"])
    except RuntimeError as exc:
        print(f"Falha: {exc}")
        return 1
    print(f"OK - Bot: @{bot['username']}")
    print(f"OK - Canal: {chat.get('title', values['CHAT_ID'])} ({chat['id']})")
    print("OK - API_ID e API_HASH estão preenchidos (validação completa ocorre no Pyrogram).")
    return 0


def discover_chat() -> int:
    values = read_values()
    current_token = (
        values.get("BOT_TOKENS") or values.get("BOT_TOKEN") or ""
    ).split(",")[0].strip()
    token = prompt("Token fornecido pelo BotFather", current_token, secret=True)
    if not token:
        print("ERRO: informe o token do bot.")
        return 1

    try:
        bot = api_call(token, "getMe")
        updates = api_call(token, "getUpdates", limit=100)
    except RuntimeError as exc:
        print(f"ERRO: {exc}")
        return 1

    chats = {}
    message_fields = ("channel_post", "edited_channel_post", "message", "edited_message")
    for update in updates:
        for field in message_fields:
            chat = update.get(field, {}).get("chat")
            if chat and chat.get("type") in ("channel", "supergroup"):
                chats[chat["id"]] = chat
        membership_chat = update.get("my_chat_member", {}).get("chat")
        if membership_chat and membership_chat.get("type") in ("channel", "supergroup"):
            chats[membership_chat["id"]] = membership_chat

    print(f"\nBot confirmado: @{bot['username']}")
    if not chats:
        print("Nenhum canal apareceu nas atualizações do bot.")
        print("1. Confirme que o bot é administrador do canal.")
        print("2. Publique AGORA uma mensagem nova no canal.")
        print("3. Execute este arquivo BAT novamente.")
        print("4. Deixe o Nebula desligado durante a descoberta.")
        return 1

    print("\nCanais encontrados:")
    ordered = list(chats.values())
    for index, chat in enumerate(ordered, 1):
        print(f"  {index}. {chat.get('title', 'Sem título')} — CHAT_ID={chat['id']}")

    if len(ordered) == 1:
        selected = ordered[0]
    else:
        choice = input("Escolha o número do canal: ").strip()
        if not choice.isdigit() or not 1 <= int(choice) <= len(ordered):
            print("Seleção inválida.")
            return 1
        selected = ordered[int(choice) - 1]

    write_values({"BOT_TOKENS": token, "CHAT_ID": str(selected["id"])})
    print(f"\nCHAT_ID salvo no .env: {selected['id']}")
    return 0


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(check())
    if "--discover-chat" in sys.argv:
        sys.exit(discover_chat())
    sys.exit(configure())
