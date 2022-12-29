from __future__ import annotations

import asyncio
import logging
from typing import Callable, Awaitable, TypeVar

import telegram
from telegram.error import RetryAfter, TelegramError

from bob.application.exceptions.io import IoException
from bob.application.ports import TelegramUploader
from bob.config import TelegramConfig
from bob.domain.model import InlineOption

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

    async def send_voice_message(
        self,
        chat_id: int,
        voice: bytes,
        caption: str | None = None,
        reply_to_message_id: int | None = None,
        inline_options: list[InlineOption] | None = None,
    ) -> None:
        keyboard = self._build_keyboard(inline_options)

        async with telegram.Bot(token=self.config.token) as bot:
            await _auto_retry(
                lambda: bot.send_voice(
                    chat_id=chat_id,
                    voice=voice,
                    caption=caption,
                    reply_to_message_id=reply_to_message_id,
                    allow_sending_without_reply=True,
                    reply_markup=keyboard,
                )
            )

    async def delete_message(self, chat_id: int, message_id: int) -> None:
        try:
            async with telegram.Bot(token=self.config.token) as bot:
                await _auto_retry(
                    lambda: bot.delete_message(
                        chat_id=chat_id,
                        message_id=message_id,
                    )
                )
        except TelegramError as e:
            _LOG.error("Could not delete message", exc_info=e)

    async def edit_inline_options(
        self,
        chat_id: int,
        message_id: int,
        inline_options: list[InlineOption],
    ) -> None:
        try:
            async with telegram.Bot(token=self.config.token) as bot:
                await _auto_retry(
                    lambda: bot.edit_message_reply_markup(
                        chat_id=chat_id,
                        message_id=message_id,
                        reply_markup=self._build_keyboard(inline_options),
                    )
                )
        except TelegramError as e:
            _LOG.error("Could not edit message", exc_info=e)

    @staticmethod
    def _build_button(option: InlineOption) -> telegram.InlineKeyboardButton:
        return telegram.InlineKeyboardButton(
            text=option.text,
            callback_data=f"{option.text_message_id}::{option.code.value}",
        )

    def _build_keyboard(
        self,
        inline_options: list[InlineOption] | None,
    ) -> telegram.InlineKeyboardMarkup | None:
        if not inline_options:
            return None

        return telegram.InlineKeyboardMarkup(
            [
                [self._build_button(option) for option in inline_options],
            ],
        )

    async def get_file_url(
        self,
        file_id: str,
    ) -> str:
        try:
            async with telegram.Bot(token=self.config.token) as bot:
                file: telegram.File = await _auto_retry(lambda: bot.get_file(file_id))
                return file.file_path
        except TelegramError as e:
            raise IoException(f"Could not get URL for file {file_id}") from e
