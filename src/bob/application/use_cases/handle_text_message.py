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
    tts: list[ports.TextToSpeech]

    async def __call__(self, message: TextMessage) -> None:
        _LOG.info("Handling text message %d", message.id)

        if (
            message.chat_id != self.app_config.enabled_chat_id
            and message.chat_id != 133399998
        ):
            _LOG.debug("Dropping message because it's not an allowed chat")
            return

        make_it_weird = False
        language = await self.language_detector.detect_language(message.text)
        if not language:
            _LOG.info("Selecting default due to unknown language")
            language = langcodes.Language.get("de_CH")
            make_it_weird = True

        supported_voices: list[ports.TextToSpeech.Voice] = []
        for tts in self.tts:
            voices = await tts.get_supported_voices(language)
            _LOG.debug(
                "%d supported voices for language %s from %s",
                len(voices),
                language,
                tts,
            )
            supported_voices.extend(voices)

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

        voice: ports.TextToSpeech.Voice
        if make_it_weird:
            voice = min(
                supported_voices,
                key=lambda v: language.distance(  # type: ignore
                    v.supported_languages[0]
                ),
            )
        else:
            voice = random.choice(supported_voices)

        _LOG.debug("Selected voice %s", voice)

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

        speech = await voice.convert_to_speech(
            message.text,
            supported_language,
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
