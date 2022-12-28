import logging

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

    async def get_supported_voices(
        self,
        language: Language,
    ) -> list[TextToSpeech.Voice]:
        response = await self._client.list_voices(language_code=language.to_tag())
        return [
            TextToSpeech.Voice(
                name=voice.name,
                supported_languages=[Language.get(c) for c in voice.language_codes],
            )
            for voice in response.voices
            if "Neural2" in voice.name
        ]

    async def convert_to_speech(
        self,
        text: str,
        language: Language,
        voice: TextToSpeech.Voice,
    ) -> bytes:
        client = self._client
        synth_input = texttospeech.SynthesisInput(text=text)
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
