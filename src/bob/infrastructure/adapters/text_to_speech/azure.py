import asyncio

import azure.cognitiveservices.speech as speechsdk
from langcodes import Language

from bob.application.ports import TextToSpeech
from bob.config import AzureTtsConfig


class AzureTextToSpeech(TextToSpeech):
    def __init__(self, config: AzureTtsConfig):
        self.config = speechsdk.SpeechConfig(
            region=config.region,
            subscription=config.key,
        )
        self.config.set_profanity(speechsdk.ProfanityOption.Raw)
        self.config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Ogg48Khz16BitMonoOpus,
        )

    async def get_supported_voices(
        self,
        language: Language,
    ) -> list[TextToSpeech.Voice]:
        synth = speechsdk.SpeechSynthesizer(
            speech_config=self.config,
        )
        voices_future = synth.get_voices_async(language.to_tag())
        loop = asyncio.get_running_loop()
        voices: speechsdk.SynthesisVoicesResult = await loop.run_in_executor(
            None,
            voices_future.get,
        )
        return [
            TextToSpeech.Voice(
                tts=self,
                name=voice.name,
                supported_languages=[Language.get(voice.locale)],
            )
            for voice in voices.voices
        ]

    async def convert_to_speech(
        self,
        text: str,
        language: Language,
        voice: TextToSpeech.Voice,
    ) -> bytes:
        speech_config = self.config
        speech_config.speech_synthesis_voice_name = voice.name
        audio_config = speechsdk.audio.AudioOutputConfig()
        synth = speechsdk.SpeechSynthesizer(
            speech_config=self.config,
            audio_config=audio_config,
        )
        future = synth.speak_text_async(text)
        loop = asyncio.get_running_loop()
        result: speechsdk.SpeechSynthesisResult = await loop.run_in_executor(
            None,
            future.get,
        )
        return result.audio_data