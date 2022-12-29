import logging

from asyncache import cached
from google.cloud.vision import (
    ImageAnnotatorAsyncClient,
    Image,
    AnnotateImageRequest,
    Feature,
)

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
        request = AnnotateImageRequest(
            image=image,
            features=[
                Feature(
                    type=Feature.Type.TEXT_DETECTION,
                ),
            ],
        )
        responses = await client.batch_annotate_images(requests=[request])
        _LOG.debug("Got responses %s", responses)
        response = responses.responses[0]
        if response.error:
            _LOG.error("Got an error: %s", response.error)
            return None

        _LOG.debug("full_text: %s", response.full_text_annotation)
        return response.full_text_annotation.text or None
