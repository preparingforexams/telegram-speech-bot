from typing import AsyncIterable

import telegram

from bob.application.ports import TelegramQueue
from bob.application.ports.telegram_queue import Update, Message
from bob.config import TelegramConfig


class PtbTelegramQueue(TelegramQueue):
    def __init__(self, config: TelegramConfig):
        self._token = config.token

    @staticmethod
    def _convert_update(native: telegram.Update) -> Update:
        if native_message := native.message:
            message = Message(
                id=native_message.message_id,
                text=native_message.text,
            )
        else:
            message = None

        return Update(id=native.update_id, message=message)

    async def subscribe(self) -> AsyncIterable[Update]:
        async with telegram.Bot(self._token) as bot:
            update_id: int | None = None
            while True:
                try:
                    native_updates: tuple[telegram.Update] = await bot.get_updates(
                        offset=None if update_id is None else update_id + 1,
                    )
                except telegram.error.TimedOut:
                    continue

                for native_update in native_updates:
                    update_id = native_update.update_id
                    update = self._convert_update(native_update)
                    if update is None:
                        continue

                    yield update
