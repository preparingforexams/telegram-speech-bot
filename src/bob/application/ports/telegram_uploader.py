import abc


class TelegramUploader(abc.ABC):
    @abc.abstractmethod
    async def send_text_message(self, text: str):
        pass
