"""Portable entry point for Nebula Local."""

from __future__ import annotations

import asyncio
import logging
import os
import signal
import sys

# Windows terminals commonly default to CP1252, which cannot render the
# Unicode status messages used by Nebula.
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

import main as nebula
from configurar_telegram import api_call


class _SafeConsoleStream:
    def __init__(self, stream):
        self.stream = stream

    def write(self, value):
        encoding = getattr(self.stream, "encoding", None) or "utf-8"
        safe_value = value.encode(encoding, errors="replace").decode(encoding)
        return self.stream.write(safe_value)

    def flush(self):
        return self.stream.flush()


class _RepairTextFilter(logging.Filter):
    def filter(self, record):
        if isinstance(record.msg, str):
            try:
                record.msg = record.msg.encode("latin-1").decode("utf-8")
            except (UnicodeEncodeError, UnicodeDecodeError):
                pass
        return True


nebula.console_handler.setStream(_SafeConsoleStream(sys.stderr))
nebula.console_handler.addFilter(_RepairTextFilter())
nebula.log_handler.addFilter(_RepairTextFilter())
nebula.logger.propagate = False


async def _resolve_channel(bot):
    """Resolve a private Bot API channel into Pyrogram's MTProto peer cache."""
    raw_chat = os.environ.get("CHAT_ID", "")
    target_chat = int(raw_chat) if raw_chat.lstrip("-").isdigit() else raw_chat
    logger = logging.getLogger("NebulaFTP")

    try:
        chat = await bot.get_chat(target_chat)
    except (KeyError, ValueError):
        token = (os.environ.get("BOT_TOKENS") or os.environ.get("BOT_TOKEN") or "")
        token = token.split(",")[0].strip()
        if not token:
            logger.critical("Token do Telegram ausente.")
            return None

        logger.info("Registrando o canal privado na sessão do Telegram...")
        try:
            await asyncio.to_thread(
                api_call,
                token,
                "sendMessage",
                chat_id=raw_chat,
                text="Nebula Local conectado ao canal.",
                disable_notification="true",
            )
        except RuntimeError as exc:
            logger.critical("Não foi possível acessar o canal: %s", exc)
            return None

        chat = None
        for _ in range(10):
            await asyncio.sleep(1)
            try:
                chat = await bot.get_chat(target_chat)
                break
            except (KeyError, ValueError):
                continue
        if chat is None:
            logger.critical(
                "O canal respondeu pela Bot API, mas não foi resolvido pelo Pyrogram."
            )
            return None
    except Exception as exc:
        logger.critical("Canal inválido %r: %s", raw_chat, exc)
        return None

    logger.info("Canal confirmado: %s (ID: %s)", chat.title, chat.id)
    return chat.id


def _enable_windows_signal_handlers(loop: asyncio.AbstractEventLoop) -> None:
    if sys.platform != "win32":
        return

    def add_signal_handler(sig, callback, *args):
        signal.signal(
            sig,
            lambda *_: loop.call_soon_threadsafe(callback, *args),
        )

    loop.add_signal_handler = add_signal_handler


def run() -> None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    _enable_windows_signal_handlers(loop)
    nebula.resolve_channel = _resolve_channel
    try:
        loop.run_until_complete(nebula.main())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()


if __name__ == "__main__":
    run()
