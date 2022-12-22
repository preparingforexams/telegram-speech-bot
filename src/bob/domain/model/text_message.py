from dataclasses import dataclass


@dataclass(frozen=True)
class TextMessage:
    chat_id: int
    id: int
    text: str
    sender_name: str
