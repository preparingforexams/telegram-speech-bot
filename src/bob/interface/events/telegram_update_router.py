import asyncio
import logging
import signal

from bob.application import Application
from bob.application.ports.telegram_queue import Photo, PhotoSize
from bob.domain.model import ImageMessage, TextMessage

_LOG = logging.getLogger(__name__)


class TelegramUpdateRouter:
    def __init__(self, app: Application) -> None:
        self.app = app

    async def _on_signal(
        self,
    ) -> None:
        _LOG.info("Stopping queue due to signal")
        await self.app.ports.telegram_queue.stop()

    @staticmethod
    def _select_largest_size(photo: Photo) -> PhotoSize:
        threshold = 20_000_000
        valid_sizes = (
            size
            for size in photo.sizes
            if size.file_size is not None and size.file_size <= threshold
        )
        return max(valid_sizes, key=lambda size: size.file_size or 0)

    async def _register_signal_handlers(self) -> None:
        loop = asyncio.get_running_loop()

        for sig in [signal.SIGTERM, signal.SIGINT]:
            loop.add_signal_handler(sig, self._on_signal)

    async def run(self) -> None:
        await self._register_signal_handlers()

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

        _LOG.info("Queue stopped")
