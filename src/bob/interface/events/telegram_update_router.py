import logging
import signal
from typing import Any

from bob.application import Application
from bob.application.ports.telegram_queue import Photo, PhotoSize
from bob.domain.model import TextMessage, ImageMessage

_LOG = logging.getLogger(__name__)


class TelegramUpdateRouter:
    def __init__(self, app: Application) -> None:
        self.app = app
        self._should_kill = False

    def _on_signal(self, sig: int, _: Any) -> None:
        if sig == signal.SIGTERM:
            self._should_kill = True

    @staticmethod
    def _select_largest_size(photo: Photo) -> PhotoSize:
        threshold = 20_000_000
        valid_sizes = (
            size
            for size in photo.sizes
            if size.file_size is not None and size.file_size <= threshold
        )
        return max(valid_sizes, key=lambda size: size.file_size or 0)

    async def run(self) -> None:
        signal.signal(signal.SIGTERM, self._on_signal)

        async for update in self.app.ports.telegram_queue.subscribe():
            _LOG.info(f"Received update {update.id}")

            if message := update.message:
                if message.text and message.sender_name and message.chat_id:
                    text_message = TextMessage(
                        chat_id=message.chat_id,
                        id=message.id,
                        text=message.text,
                        sender_name=message.sender_name,
                        replied_to=message.replied_to_id,
                    )
                    await self.app.handle_text_message(text_message)
                elif message.photo and message.sender_name and message.chat_id:
                    size = self._select_largest_size(message.photo)
                    image_message = ImageMessage(
                        chat_id=message.chat_id,
                        id=message.id,
                        sender_name=message.sender_name,
                        replied_to=message.replied_to_id,
                        caption=message.photo.caption,
                        file_id=size.file_id,
                    )
                    await self.app.handle_image_message(image_message)

            if callback := update.callback_query:
                await self.app.handle_inline_callback(callback)

            if self._should_kill:
                _LOG.warning("Shutting down because of signal")
                break
