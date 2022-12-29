from dataclasses import dataclass


@dataclass(frozen=True)
class Chat:
    id: int
    delete_text_message: bool = False
