import abc


class TextToSpeech(abc.ABC):
    @abc.abstractmethod
    async def convert_to_speech(self, text: str) -> bytes:
        pass
