import abc


class ImageTextRecognizer(abc.ABC):
    @abc.abstractmethod
    async def detect_text(self, image_url: str) -> str | None:
        pass
