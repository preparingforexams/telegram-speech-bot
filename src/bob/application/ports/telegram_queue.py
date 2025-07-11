import abc
from collections.abc import AsyncIterable
from dataclasses import dataclass

from bob.domain.model import InlineCallback


@dataclass(frozen=True)
class PhotoSize:
    file_id: str
    file_size: int | None


@dataclass(frozen=True)
class Photo:
    caption: str | None
    sizes: list[PhotoSize]


@dataclass(frozen=True)
class Message:
    id: int
    chat_id: int | None
    sender_name: str | None
    text: str | None
    replied_to_id: int | None
    photo: Photo | None


@dataclass(frozen=True)
class Update:
    id: int
    message: Message | None
    callback_query: InlineCallback | None


class TelegramQueue(abc.ABC):
    @abc.abstractmethod
    def subscribe(self) -> AsyncIterable[Update]:
        pass

    @abc.abstractmethod
    async def stop(self) -> None:
        pass
