import abc
from dataclasses import dataclass
from typing import AsyncIterable


@dataclass
class Update:
    id: int


class TelegramQueue(abc.ABC):
    @abc.abstractmethod
    def subscribe(self) -> AsyncIterable[Update]:
        pass
