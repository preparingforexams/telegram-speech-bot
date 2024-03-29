import functools
import logging

from google.cloud.vision import (
    AnnotateImageRequest,
    Feature,
    Image,
    ImageAnnotatorAsyncClient,
)

from bob.application.ports import ImageTextRecognizer

_LOG = logging.getLogger(__name__)


class GoogleImageTextRecognizer(ImageTextRecognizer):
    @functools.cache
    async def _get_client(self) -> ImageAnnotatorAsyncClient:
        return ImageAnnotatorAsyncClient()

    async def detect_text(self, image: bytes) -> str | None:
        client = await self._get_client()
        request = AnnotateImageRequest(
            image=Image(
                content=image,
            ),
            features=[
                Feature(
                    type=Feature.Type.TEXT_DETECTION,
                ),
            ],
        )
        responses = await client.batch_annotate_images(requests=[request])
        response = responses.responses[0]
        if response.error.code:
            _LOG.error("Got an error: %s", response.error)
            return None

        return response.full_text_annotation.text or None
