from __future__ import annotations

import asyncio
import logging
from typing import Callable, Awaitable, TypeVar

import telegram
from telegram.error import RetryAfter

from bob.application.ports import TelegramUploader
from bob.config import TelegramConfig

_LOG = logging.getLogger(__name__)
TIMEOUTS = dict(read_timeout=180, write_timeout=180, connect_timeout=180)

T = TypeVar("T")


async def _auto_retry(func: Callable[[], Awaitable[T]]) -> T:
    try:
        return await func()
    except RetryAfter as e:
        _LOG.debug(
            "Received RetryAfter exception, waiting for %d seconds",
            e.retry_after,
        )
        await asyncio.sleep(e.retry_after)

    return await func()


class PtbTelegramUploader(TelegramUploader):
    def __init__(self, config: TelegramConfig):
        self.config = config

    async def send_text_message(self, text: str):
        async with telegram.Bot(token=self.config.token) as bot:
            await _auto_retry(
                lambda: bot.send_message(
                    chat_id=self.config.target_chat,
                    disable_notification=True,
                    disable_web_page_preview=True,
                    text=text,
                    **TIMEOUTS,
                )
            )
