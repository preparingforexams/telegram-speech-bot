import abc
from dataclasses import dataclass
from typing import AsyncIterable


@dataclass(frozen=True)
class Message:
    id: int
    chat_id: int | None
    sender_name: str | None
    text: str | None


@dataclass(frozen=True)
class Update:
    id: int
    message: Message | None


class TelegramQueue(abc.ABC):
    @abc.abstractmethod
    def subscribe(self) -> AsyncIterable[Update]:
        pass
