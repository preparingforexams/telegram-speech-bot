from dataclasses import dataclass

from injector import inject

from bob.application import use_cases, ports


@inject
@dataclass
class Ports:
    telegram_queue: ports.TelegramQueue


@inject
@dataclass
class Application:
    ports: Ports
    handle_inline_callback: use_cases.HandleInlineCallback
    handle_image_message: use_cases.HandleImageMessage
    handle_text_message: use_cases.HandleTextMessage
