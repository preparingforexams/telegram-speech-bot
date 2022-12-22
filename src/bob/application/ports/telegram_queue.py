import abc
from dataclasses import dataclass
from typing import AsyncIterable


@dataclass(frozen=True)
class Message:
    id: int
    text: str | None


@dataclass(frozen=True)
class Update:
    id: int
    message: Message | None


class TelegramQueue(abc.ABC):
    @abc.abstractmethod
    def subscribe(self) -> AsyncIterable[Update]:
        pass
