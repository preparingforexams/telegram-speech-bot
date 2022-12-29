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
        image = await self.telegram.get_file(image_message.file_id)
        _LOG.debug("Got file of size %d", len(image))
        text = await self.image_text_recognizer.detect_text(image)

        if text is None:
            _LOG.info("Detected no text in image")
            return

        _LOG.info("Detected text: %s", text)
