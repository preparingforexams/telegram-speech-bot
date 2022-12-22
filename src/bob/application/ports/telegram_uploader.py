import abc


class TelegramUploader(abc.ABC):
    @abc.abstractmethod
    async def send_voice_message(self, chat_id: int, voice: bytes):
        pass
