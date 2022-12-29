import abc
from dataclasses import dataclass


@dataclass(frozen=True)
class Message(abc.ABC):
    chat_id: int
    id: int
    sender_name: str
    replied_to: int | None


@dataclass(frozen=True)
class TextMessage(Message):
    text: str


@dataclass(frozen=True)
class ImageMessage(Message):
    caption: str | None
    file_id: str
