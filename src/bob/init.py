import logging
from pathlib import Path

import sentry_sdk
from injector import Injector, Module, provider

from bob.application import Application, repos, ports
from bob.config import load_env, Config, SentryConfig
from bob.infrastructure.adapters import (
    telegram_uploader,
    telegram_queue,
)

_LOG = logging.getLogger(__name__)


def _setup_logging():
    logging.basicConfig()

    logging.root.level = logging.WARNING
    logging.getLogger(__package__).level = logging.DEBUG


def _setup_sentry(config: SentryConfig):
    dsn = config.dsn
    if not dsn:
        _LOG.warning("Sentry DSN not found")
        return

    sentry_sdk.init(
        dsn=dsn,
        release=config.release,
    )


class PortsModule(Module):
    def __init__(self, config: Config):
        self.config = config

    @provider
    def provide_telegram_queue(self) -> ports.TelegramQueue:
        return telegram_queue.PtbTelegramQueue(self.config.telegram)

    @provider
    def provide_telegram_uploader(self) -> ports.TelegramUploader:
        return telegram_uploader.PtbTelegramUploader(self.config.telegram)


def initialize() -> Application:
    _setup_logging()

    config = Config.from_env(load_env(""))
    _setup_sentry(config.sentry)

    injector = Injector(
        modules=[
            PortsModule(config),
        ]
    )
    return injector.get(Application)
