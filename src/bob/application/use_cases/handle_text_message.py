import logging
import random
from dataclasses import dataclass

import langcodes
from injector import inject

from bob.application import ports, repos
from bob.domain.model import TextMessage

_LOG = logging.getLogger(__name__)


@inject
@dataclass
class HandleTextMessage:
    chat_repo: repos.ChatRepository
    language_detector: ports.LanguageDetector
    telegram_uploader: ports.TelegramUploader
    tts: list[ports.TextToSpeech]

    async def __call__(self, message: TextMessage) -> None:
        _LOG.info("Handling text message %d", message.id)

        chat = await self.chat_repo.get_chat(message.chat_id)
        if chat is None:
            _LOG.debug("Dropping message because it's not an allowed chat")
            return

        language = await self.language_detector.detect_language(message.text)
        if not language:
            _LOG.info("Selecting default due to unknown language")
            language = langcodes.Language.get("de_DE")

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
            "Found %d supported voices for language %s (%s): %s",
            len(supported_voices),
            language,
            language.language_name(),
            [v.name for v in supported_voices],
        )

        voice: ports.TextToSpeech.Voice
        if chat.fixed_voice:
            for v in supported_voices:
                if v.name == chat.fixed_voice:
                    voice = v
                    break
            else:
                _LOG.error(
                    "Did not find the fixed voice %s. Choosing randomly.",
                    chat.fixed_voice,
                )
                voice = random.choice(supported_voices)
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

        if not speech:
            _LOG.info("No speech synthesized, skipping message.")
            return

        if chat.delete_text_message:
            caption = f"(Original von {message.sender_name})"
            reply_to = message.replied_to
        else:
            caption = None
            reply_to = message.id

        await self.telegram_uploader.send_voice_message(
            chat_id=message.chat_id,
            voice=speech,
            caption=caption,
            reply_to_message_id=reply_to,
        )

        if chat.delete_text_message:
            await self.telegram_uploader.delete_message(
                chat_id=message.chat_id,
                message_id=message.id,
            )
