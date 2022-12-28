from langcodes import Language

from bob.application.ports import TextToSpeech


class StubTextToSpeech(TextToSpeech):
    async def get_supported_voices(
        self,
        language: Language,
    ) -> list[TextToSpeech.Voice]:
        return [TextToSpeech.Voice(self, "stub-voice", [Language.get("de_DE")])]

    async def convert_to_speech(
        self,
        text: str,
        language: Language,
        voice: TextToSpeech.Voice,
    ) -> bytes:
        return bytes(0)
