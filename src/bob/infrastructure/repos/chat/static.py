from collections.abc import Iterable

from bob.application.repos import ChatRepository
from bob.domain.model import Chat


class StaticChatRepository(ChatRepository):
    async def get_chats(self) -> Iterable[Chat]:
        return {
            Chat(
                id=133399998,
                enable_ocr=True,
                enable_inline_options=True,
            ),
            Chat(
                id=-1001348149915,
                enable_ocr=True,
                delete_text_message=True,
            ),
            Chat(
                id=-1001243399669,
                enable_ocr=True,
                enable_inline_options=True,
            ),
        }
