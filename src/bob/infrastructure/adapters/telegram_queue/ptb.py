import asyncio
import logging
from typing import AsyncIterable

import telegram

from bob.application.ports import TelegramQueue
from bob.application.ports.telegram_queue import Update, Message, Photo, PhotoSize
from bob.config import TelegramConfig
from bob.domain.model import InlineCallback, InlineCode

_LOG = logging.getLogger(__name__)


class PtbTelegramQueue(TelegramQueue):
    def __init__(self, config: TelegramConfig):
        self._token = config.token

    @staticmethod
    def _extract_sender_name(user: telegram.User | None) -> str | None:
        if not user:
            return None

        if user.id == 1365395775:
            return "Katharine"
        else:
            return user.first_name

    @staticmethod
    def _extract_photo(native_message: telegram.Message) -> Photo | None:
        if native_photo := native_message.photo:
            return Photo(
                caption=native_message.caption,
                sizes=[
                    PhotoSize(file_id=size.file_id, file_size=size.file_size)
                    for size in native_photo
                ],
            )

        return None

    def _extract_message(
        self,
        native_message: telegram.Message | None,
    ) -> Message | None:
        if not native_message:
            return None

        sender_name = self._extract_sender_name(native_message.from_user)
        reply_to_message = native_message.reply_to_message

        return Message(
            chat_id=native_message.chat.id,
            id=native_message.message_id,
            text=native_message.text,
            sender_name=sender_name,
            replied_to_id=reply_to_message.message_id if reply_to_message else None,
            photo=self._extract_photo(native_message),
        )

    async def _convert_update(self, native: telegram.Update) -> Update:
        message = self._extract_message(native.message)

        callback: InlineCallback | None = None
        if native_callback := native.callback_query:
            callback_message = native_callback.message
            if not callback_message:
                _LOG.warning("Did not receive message for callback query")
            else:
                text_message_id, code = native_callback.data.split("::", maxsplit=1)
                callback = InlineCallback(
                    chat_id=callback_message.chat.id,
                    text_message_id=int(text_message_id),
                    speech_message_id=callback_message.message_id,
                    code=InlineCode(code),
                )

            await native_callback.answer()

        return Update(
            id=native.update_id,
            message=message,
            callback_query=callback,
        )

    async def subscribe(self) -> AsyncIterable[Update]:
        async with telegram.Bot(self._token) as bot:
            update_id: int | None = None
            while True:
                try:
                    native_updates: tuple[telegram.Update] = await bot.get_updates(
                        offset=None if update_id is None else update_id + 1,
                    )
                except telegram.error.TimedOut as e:
                    _LOG.warning("Received timeout from Telegram", exc_info=e)
                    continue
                except telegram.error.RetryAfter as e:
                    _LOG.warning("Am sending too many requests to telegram")
                    await asyncio.sleep(e.retry_after)
                    continue

                for native_update in native_updates:
                    update_id = native_update.update_id
                    update = await self._convert_update(native_update)
                    if update is None:
                        continue

                    yield update
