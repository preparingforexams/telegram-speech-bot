import logging
from dataclasses import dataclass

from injector import inject

from bob.application import ports
from bob.domain.model import TextMessage

_LOG = logging.getLogger(__name__)


@inject
@dataclass
class HandleTextMessage:
    telegram_uploader: ports.TelegramUploader
    text_to_speech: ports.TextToSpeech

    async def __call__(self, message: TextMessage) -> None:
        _LOG.info("Handling text message %d", message.id)

        voice = await self.text_to_speech.convert_to_speech(message.text)
        await self.telegram_uploader.send_voice_message(
            chat_id=message.chat_id,
            voice=voice,
        )
