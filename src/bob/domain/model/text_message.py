from dataclasses import dataclass


@dataclass(frozen=True)
class TextMessage:
    id: int
    text: str
