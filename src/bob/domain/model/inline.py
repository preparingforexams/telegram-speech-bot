from dataclasses import dataclass
from enum import Enum


class InlineCode(str, Enum):
    CHILD = "u18"
    SWISS = "ch"
    HOLLAND = "nl"


@dataclass(frozen=True)
class InlineOption:
    text: str
    text_message_id: int
    code: InlineCode


@dataclass(frozen=True)
class InlineCallback:
    chat_id: int
    text_message_id: int
    speech_message_id: int
    code: InlineCode
