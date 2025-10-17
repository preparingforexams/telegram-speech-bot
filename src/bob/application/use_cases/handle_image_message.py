import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from injector import inject

if TYPE_CHECKING:
    from bob.application import ports, repos, services
    from bob.domain.model import ImageMessage

_LOG = logging.getLogger(__name__)


@inject
@dataclass
class HandleImageMessage:
    chat_repo: repos.ChatRepository
    image_text_recognizer: ports.ImageTextRecognizer
    initial_message_sender: services.InitialMessageSender
    telegram: ports.TelegramUploader

    async def __call__(self, message: ImageMessage) -> None:
        _LOG.info("Received image message %s", message)

        chat = await self.chat_repo.get_chat(message.chat_id)
        if chat is None:
            _LOG.debug("Dropping message because it's not an allowed chat")
            return

        image = await self.telegram.get_file(message.file_id)
        _LOG.debug("Got file of size %d", len(image))
        text = await self.image_text_recognizer.detect_text(image)

        if text is None:
            _LOG.info("Detected no text in image")
            return

        await self.initial_message_sender.send_initial_message(
            chat=chat,
            message=message,
            text=text,
        )
