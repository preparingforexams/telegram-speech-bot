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
    handle_text_message: use_cases.HandleTextMessage
