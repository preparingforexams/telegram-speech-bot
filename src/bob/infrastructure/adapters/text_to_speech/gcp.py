import logging
import random

from cachetools import cached
from google.cloud import texttospeech
from langcodes import Language

from bob.application.ports import TextToSpeech

_LOG = logging.getLogger(__name__)


class GcpTextToSpeech(TextToSpeech):
    @property
    @cached({})
    def _client(self) -> texttospeech.TextToSpeechAsyncClient:
        return texttospeech.TextToSpeechAsyncClient()

    @cached({})
    async def _get_supported_voices(self) -> list[texttospeech.Voice]:
        response = await self._client.list_voices()
        return [voice for voice in response.voices if "Neural2" in voice.name]

    async def get_supported_languages(self) -> set[Language]:
        voices = await self._get_supported_voices()
        return {Language.get(code) for voice in voices for code in voice.language_codes}

    async def _get_voices_for_language(
        self,
        language: Language,
        match_threshold: float = 25,
    ) -> list[texttospeech.Voice]:
        result: list[texttospeech.Voice] = []
        for voice in await self._get_supported_voices():
            match = min(
                Language.get(code).distance(language) for code in voice.language_codes
            )
            if match <= match_threshold:
                result.append(voice)

        if not result:
            raise ValueError(f"Unsupported language: {language}")

        _LOG.info(
            "Found %d voices for language %s: %s",
            len(result),
            language,
            [voice.name for voice in result],
        )

        return result

    async def convert_to_speech(self, text: str, language: Language) -> bytes:
        client = self._client
        synth_input = texttospeech.SynthesisInput(text=text)

        voices = await self._get_voices_for_language(language)
        voice = random.choice(voices)
        voice_params = texttospeech.VoiceSelectionParams(
            language_code=language.to_tag(),
            name=voice.name,
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.OGG_OPUS,
        )
        response = await client.synthesize_speech(
            input=synth_input,
            voice=voice_params,
            audio_config=audio_config,
        )
        return response.audio_content
