import logging
import random
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

        supported_voices = await self.text_to_speech.get_supported_voices(language)

        if not supported_voices:
            _LOG.warning(
                "Unsupported message language %s (%s)",
                language,
                language.language_name(),
            )
            return

        _LOG.debug(
            "Found %d supported voices for language %s (%s)",
            len(supported_voices),
            language,
            language.language_name(),
        )

        voice = random.choice(supported_voices)

        supported_language_tag = langcodes.closest_supported_match(
            language,
            [lang.to_tag() for lang in voice.supported_languages],
        )

        if not supported_language_tag:
            _LOG.error(
                "Got voice %s for language %s that doesn't support it.",
                voice.name,
                language,
            )
            return

        supported_language = langcodes.Language.get(supported_language_tag)

        speech = await self.text_to_speech.convert_to_speech(
            message.text,
            supported_language,
            voice,
        )
        await self.telegram_uploader.send_voice_message(
            chat_id=message.chat_id,
            voice=speech,
            caption=f"(Original von {message.sender_name})",
            reply_to_message_id=message.replied_to,
        )
        await self.telegram_uploader.delete_message(
            chat_id=message.chat_id,
            message_id=message.id,
        )
