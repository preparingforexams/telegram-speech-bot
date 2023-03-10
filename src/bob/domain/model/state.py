from typing import TypedDict


class InlineMessageState(TypedDict):
    chat_id: int
    message_id: int
    replied_to: int | None
    text: str
    sender_name: str
    was_swiss: bool
    was_child: bool
    was_holland: bool
