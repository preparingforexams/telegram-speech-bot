import logging

from asyncache import cached
from google.cloud.vision import ImageAnnotatorAsyncClient, Image, ImageSource

from bob.application.ports import ImageTextRecognizer

_LOG = logging.getLogger(__name__)


class GoogleImageTextRecognizer(ImageTextRecognizer):
    @cached({})
    async def _get_client(self) -> ImageAnnotatorAsyncClient:
        return ImageAnnotatorAsyncClient()

    async def detect_text(self, image_url: str) -> str | None:
        client = await self._get_client()
        image = Image()
        image.source.image_uri = image_url
        response = await client.text_detection(image=image)  # type: ignore
        return response.full_text_annotation.text
