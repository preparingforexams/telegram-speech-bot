import logging

from bob.application.ports import ImageTextRecognizer

_LOG = logging.getLogger(__name__)


class GoogleImageTextRecognizer(ImageTextRecognizer):
    async def detect_text(self, image_url: str) -> str | None:
        # TODO
        return None
