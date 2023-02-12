from dataclasses import dataclass

from injector import inject, Injector

from bob.application import use_cases, ports


@inject
@dataclass
class Ports:
    telegram_queue: ports.TelegramQueue


class Application:
    def __init__(self, injector: Injector) -> None:
        self._injector = injector

    @property
    def ports(self) -> Ports:
        return self._injector.get(Ports)

    @property
    def handle_inline_callback(self) -> use_cases.HandleInlineCallback:
        return self._injector.get(use_cases.HandleInlineCallback)

    @property
    def handle_image_message(self) -> use_cases.HandleImageMessage:
        return self._injector.get(use_cases.HandleImageMessage)

    @property
    def handle_text_message(self) -> use_cases.HandleTextMessage:
        return self._injector.get(use_cases.HandleTextMessage)
