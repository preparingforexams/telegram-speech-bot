import abc


class TelegramUploader(abc.ABC):
    @abc.abstractmethod
    async def send_voice_message(self, chat_id: int, voice: bytes) -> None:
        pass

    @abc.abstractmethod
    async def delete_message(self, chat_id: int, message_id: int) -> None:
        pass
