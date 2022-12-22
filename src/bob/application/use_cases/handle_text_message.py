import logging
from dataclasses import dataclass

from injector import inject

from bob.application import ports
from bob.application.app_config import AppConfig
from bob.domain.model import TextMessage

_LOG = logging.getLogger(__name__)


@inject
@dataclass
class HandleTextMessage:
    app_config: AppConfig
    telegram_uploader: ports.TelegramUploader
    text_to_speech: ports.TextToSpeech

    async def __call__(self, message: TextMessage) -> None:
        _LOG.info("Handling text message %d", message.id)

        if message.chat_id != self.app_config.enabled_chat_id:
            _LOG.debug("Dropping message because it's not an allowed chat")
            return

        voice = await self.text_to_speech.convert_to_speech(message.text)
        await self.telegram_uploader.send_voice_message(
            chat_id=message.chat_id,
            voice=voice,
            caption=f"(Original von {message.sender_name})",
            reply_to_message_id=message.replied_to,
        )
        await self.telegram_uploader.delete_message(
            chat_id=message.chat_id,
            message_id=message.id,
        )
