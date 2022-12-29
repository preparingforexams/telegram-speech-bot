import logging
from dataclasses import dataclass

from injector import inject

from bob.application import ports
from bob.domain.model import ImageMessage

_LOG = logging.getLogger(__name__)


@inject
@dataclass
class HandleImageMessage:
    image_text_recognizer: ports.ImageTextRecognizer
    telegram: ports.TelegramUploader

    async def __call__(self, image_message: ImageMessage) -> None:
        _LOG.info("Received image message %s", image_message)
        url = await self.telegram.get_file_url(image_message.file_id)
        text = await self.image_text_recognizer.detect_text(url)

        if text is None:
            _LOG.info("Detected no text in image")
            return

        _LOG.info("Detected text: %s", text)
