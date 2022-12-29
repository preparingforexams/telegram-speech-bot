import logging
from dataclasses import dataclass

from injector import inject

from bob.application import repos, services
from bob.domain.model import TextMessage

_LOG = logging.getLogger(__name__)


@inject
@dataclass
class HandleTextMessage:
    chat_repo: repos.ChatRepository
    initial_message_sender: services.InitialMessageSender

    async def __call__(self, message: TextMessage) -> None:
        _LOG.info("Handling text message %d", message.id)

        chat = await self.chat_repo.get_chat(message.chat_id)
        if chat is None:
            _LOG.debug("Dropping message because it's not an allowed chat")
            return

        await self.initial_message_sender.send_initial_message(
            chat,
            message,
            message.text,
        )
