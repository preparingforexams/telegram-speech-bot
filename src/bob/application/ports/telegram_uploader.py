import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bob.domain.model import InlineOption


class TelegramUploader(abc.ABC):
    @abc.abstractmethod
    async def send_voice_message(
        self,
        chat_id: int,
        voice: bytes,
        caption: str | None = None,
        reply_to_message_id: int | None = None,
        inline_options: list[InlineOption] | None = None,
    ) -> None:
        pass

    @abc.abstractmethod
    async def delete_message(self, chat_id: int, message_id: int) -> None:
        pass

    @abc.abstractmethod
    async def edit_inline_options(
        self,
        chat_id: int,
        message_id: int,
        inline_options: list[InlineOption],
    ) -> None:
        pass

    @abc.abstractmethod
    async def get_file(
        self,
        file_id: str,
    ) -> bytes:
        pass
