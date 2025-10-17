import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

    from bob.domain.model import Chat


class ChatRepository(abc.ABC):
    @abc.abstractmethod
    async def get_chats(self) -> Iterable[Chat]:
        pass

    async def get_chat(self, id: int) -> Chat | None:
        for chat in await self.get_chats():
            if chat.id == id:
                return chat

        return None
