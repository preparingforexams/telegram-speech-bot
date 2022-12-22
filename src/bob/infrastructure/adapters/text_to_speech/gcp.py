import asyncio

from google.cloud import texttospeech

from bob.application.ports import TextToSpeech


class GcpTextToSpeech(TextToSpeech):
    def __init__(self):
        self._client = texttospeech.TextToSpeechClient()

    async def convert_to_speech(self, text: str) -> bytes:
        synth_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="de-DE",
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.OGG_OPUS
        )
        response = await asyncio.get_running_loop().run_in_executor(
            None,
            lambda: self._client.synthesize_speech(
                input=synth_input,
                voice=voice,
                audio_config=audio_config,
            ),
        )
        return response.audio_content
