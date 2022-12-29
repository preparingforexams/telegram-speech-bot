import logging
from dataclasses import dataclass

from injector import inject

from bob.domain.model import ImageMessage

_LOG = logging.getLogger(__name__)


@inject
@dataclass
class HandleImageMessage:
    async def __call__(self, image_message: ImageMessage) -> None:
        _LOG.info("Received image message %s", image_message)
