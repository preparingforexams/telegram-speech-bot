from typing import TypedDict


class InlineMessageState(TypedDict):
    chat_id: int
    message_id: int
    replied_to: int | None
    text: str
    was_swiss: bool
    was_child: bool
