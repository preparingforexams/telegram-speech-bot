from google.cloud import texttospeech

from bob.application.ports import TextToSpeech


class GcpTextToSpeech(TextToSpeech):
    def __init__(self):
        self._client: texttospeech.TextToSpeechAsyncClient | None = None

    def _get_client(self) -> texttospeech.TextToSpeechAsyncClient:
        client = self._client
        if client is not None:
            return client

        self._client = (client := texttospeech.TextToSpeechAsyncClient())
        return client

    async def convert_to_speech(self, text: str) -> bytes:
        client = self._get_client()
        synth_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            name="de-DE-Neural2-F",
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
