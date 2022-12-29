from typing import Iterable

from bob.application.repos import ChatRepository
from bob.domain.model import Chat


class StaticChatRepository(ChatRepository):
    # Quick reference: de-DE-GiselaNeural is a kid, de-CH-LeniNeural is swiss
    async def get_chats(self) -> Iterable[Chat]:
        return {
            Chat(
                id=133399998,
                fixed_voice="de-AT-IngridNeural",
            ),
            Chat(
                id=-1001348149915,
                delete_text_message=True,
            ),
            Chat(
                id=-1001243399669,
                fixed_voice="de-CH-LeniNeural",
            ),
        }
