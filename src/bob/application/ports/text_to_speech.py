import abc
from dataclasses import dataclass

from langcodes import Language


class TextToSpeech(abc.ABC):
    @dataclass
    class Voice:
        name: str
        supported_languages: list[Language]

    @abc.abstractmethod
    async def get_supported_voices(self, language: Language) -> list[Voice]:
        pass

    @abc.abstractmethod
    async def convert_to_speech(
        self,
        text: str,
        language: Language,
        voice: Voice,
    ) -> bytes:
        pass
