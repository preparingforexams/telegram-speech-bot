import asyncio
import json
import logging
from collections.abc import AsyncIterable
from typing import TYPE_CHECKING

import telegram
from bs_nats_updater import NatsConfig
from nats.aio.client import Client
from nats.js.errors import ServiceUnavailableError
from telegram.error import BadRequest

from bob.application.ports import TelegramQueue
from bob.application.ports.telegram_queue import Message, Photo, PhotoSize, Update
from bob.config import TelegramConfig
from bob.domain.model import InlineCallback, InlineCode

if TYPE_CHECKING:
    from nats.js import JetStreamContext

_LOG = logging.getLogger(__name__)


class NatsTelegramQueue(TelegramQueue):
    def __init__(
        self,
        *,
        telegram_config: TelegramConfig,
        nats_config: NatsConfig,
    ):
        self._telegram_token = telegram_config.token
        self._config = nats_config
        self._is_closed = False

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
            elif data := native_callback.data:
                text_message_id, code = data.split("::", maxsplit=1)
                callback = InlineCallback(
                    chat_id=callback_message.chat.id,
                    text_message_id=int(text_message_id),
                    speech_message_id=callback_message.message_id,
                    code=InlineCode(code),
                )
            else:
                _LOG.error("Received callback query with no data: %s", callback_message)

            try:
                await native_callback.answer()
            except BadRequest:
                _LOG.warning("Received bad request response for callback query answer")

        return Update(
            id=native.update_id,
            message=message,
            callback_query=callback,
        )

    @staticmethod
    async def _register_webhook(
        bot: telegram.Bot,
        config: NatsConfig,
    ) -> None:
        _LOG.info("Registering webhook")
        await bot.set_webhook(
            url=config.receiver_url,
            secret_token=config.receiver_secret,
        )

    async def subscribe(self) -> AsyncIterable[Update]:
        config = self._config
        async with telegram.Bot(self._telegram_token) as bot:
            await self._register_webhook(bot, config)

            async with Client() as client:
                await client.connect(
                    config.url,
                    allow_reconnect=True,
                )
                jetstream = client.jetstream()
                sub: JetStreamContext.PullSubscription = (
                    await jetstream.pull_subscribe_bind(
                        consumer=config.consumer_name,
                        stream=config.stream_name,
                    )
                )

                while not self._is_closed:
                    try:
                        messages = await sub.fetch(timeout=10)
                    except TimeoutError:
                        continue
                    except ServiceUnavailableError as e:
                        _LOG.warning(
                            "NATS service unavailable. Retrying after a short wait...",
                            exc_info=e,
                        )
                        await asyncio.sleep(5)
                        continue
                    except Exception:
                        _LOG.exception("Unknown error while fetching messages")
                        continue

                    for message in messages:
                        native_update = telegram.Update.de_json(
                            data=json.loads(message.data),
                            bot=bot,
                        )
                        update = await self._convert_update(native_update)

                        if update is None:
                            _LOG.debug("Ignoring update that could not be converted")
                            await message.ack()
                            continue

                        yield update

                        await message.ack()

    async def stop(self) -> None:
        self._is_closed = True
