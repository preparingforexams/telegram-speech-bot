import random

from cachetools import cachedmethod
from google.cloud import texttospeech
from langcodes import Language

from bob.application.ports import TextToSpeech


class GcpTextToSpeech(TextToSpeech):
    @property
    @cachedmethod
    def _client(self) -> texttospeech.TextToSpeechAsyncClient:
        return texttospeech.TextToSpeechAsyncClient()

    @cachedmethod
    async def get_supported_languages(self) -> set[Language]:
        client = self._client
        voices = await client.list_voices()
        return {
            Language.get(code)
            for voice in voices.voices
            for code in voice.language_codes
            if "Neural2" in voice.name
        }

    async def convert_to_speech(self, text: str) -> bytes:
        client = self._client
        synth_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="de-DE",
            name=random.choice(["de-DE-Neural2-F", "de-DE-Neural2-D"]),
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.OGG_OPUS
        )
        response = await client.synthesize_speech(
            input=synth_input,
            voice=voice,
            audio_config=audio_config,
        )
        return response.audio_content
