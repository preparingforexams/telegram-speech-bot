import logging
from dataclasses import dataclass
from typing import Type, TypeVar

import sentry_sdk
from injector import Injector, Module, provider, multiprovider

from bob.application import Application, ports
from bob.application.app_config import AppConfig
from bob.config import load_env, Config, SentryConfig
from bob.infrastructure.adapters import (
    telegram_uploader,
    telegram_queue,
    text_to_speech,
    language_detector,
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


@dataclass(frozen=True)
class _TtsContainer:
    tts: ports.TextToSpeech


class _GcpTts(_TtsContainer):
    pass


class _AzureTts(_TtsContainer):
    pass


T = TypeVar("T")


def _try_get(injector: Injector, t: Type[T]) -> T | None:
    try:
        return injector.get(t)
    except Exception as e:
        _LOG.warning("Could not get implementation for type %s", t, exc_info=e)
        return None


class PortsModule(Module):
    def __init__(self, config: Config):
        self.config = config

    # @provider
    # def provide_gcp_text_to_speech(self) -> _GcpTts:
    #     return _GcpTts(text_to_speech.GcpTextToSpeech())

    @multiprovider
    def provide_text_to_speech_list(self) -> list[ports.TextToSpeech]:
        if self.config.use_stub_tts:
            return [text_to_speech.StubTextToSpeech()]

        return [
            text_to_speech.AzureTextToSpeech(self.config.azure_tts),
            text_to_speech.GcpTextToSpeech(),
        ]

    @provider
    def provide_telegram_queue(self) -> ports.TelegramQueue:
        return telegram_queue.PtbTelegramQueue(self.config.telegram)

    @provider
    def provide_telegram_uploader(self) -> ports.TelegramUploader:
        return telegram_uploader.PtbTelegramUploader(self.config.telegram)

    @provider
    def provide_language_detector(self) -> ports.LanguageDetector:
        config = self.config

        if config.use_stub_language_detector:
            return language_detector.StubLanguageDetector()

        if config.gcp_project is None:
            raise ValueError("GCP project not configured")

        return language_detector.GoogleCloudTranslationLanguageDetector(
            config.gcp_project,
        )


class AppConfigModule(Module):
    def __init__(self, config: Config):
        self.config = config

    @provider
    def provide_app_config(self) -> AppConfig:
        config = self.config
        return AppConfig(
            enabled_chat_id=config.telegram.target_chat,
        )


def initialize() -> Application:
    _setup_logging()

    config = Config.from_env(load_env(""))
    _setup_sentry(config.sentry)

    injector = Injector(
        modules=[
            AppConfigModule(config),
            PortsModule(config),
        ],
    )
    return injector.get(Application)
