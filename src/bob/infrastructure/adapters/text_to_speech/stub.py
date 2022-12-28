from langcodes import Language

from bob.application.ports import TextToSpeech


class StubTextToSpeech(TextToSpeech):
    async def get_supported_languages(self) -> set[Language]:
        return {Language.get("de_DE")}

    async def convert_to_speech(self, text: str, language: Language) -> bytes:
        return bytes(0)
