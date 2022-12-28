import logging
from dataclasses import dataclass

import langcodes
from injector import inject

from bob.application import ports
from bob.application.app_config import AppConfig
from bob.domain.model import TextMessage

_LOG = logging.getLogger(__name__)


@inject
@dataclass
class HandleTextMessage:
    app_config: AppConfig
    language_detector: ports.LanguageDetector
    telegram_uploader: ports.TelegramUploader
    text_to_speech: ports.TextToSpeech

    async def __call__(self, message: TextMessage) -> None:
        _LOG.info("Handling text message %d", message.id)

        if message.chat_id != self.app_config.enabled_chat_id:
            _LOG.debug("Dropping message because it's not an allowed chat")
            return

        language = await self.language_detector.detect_language(message.text)
        supported_languages = await self.text_to_speech.get_supported_languages()
        supported_language_tag = langcodes.closest_supported_match(
            language,
            [lang.to_tag() for lang in supported_languages],
        )

        if not supported_language_tag:
            _LOG.error("Unsupported message language: %s", language)
            supported_language = langcodes.Language.get("de_DE")
        else:
            supported_language = langcodes.Language.get(supported_language_tag)

        voice = await self.text_to_speech.convert_to_speech(
            message.text,
            supported_language,
        )
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
