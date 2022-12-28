import abc

from langcodes import Language


class TextToSpeech(abc.ABC):
    @abc.abstractmethod
    async def get_supported_languages(self) -> set[Language]:
        pass

    @abc.abstractmethod
    async def convert_to_speech(self, text: str, language: Language) -> bytes:
        pass
