import abc


class ImageTextRecognizer(abc.ABC):
    @abc.abstractmethod
    async def detect_text(self, image: bytes) -> str | None:
        pass
