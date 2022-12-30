import logging
from dataclasses import dataclass

import sentry_sdk
from injector import Injector, Module, provider, multiprovider

from bob.application import Application, ports, repos
from bob.config import load_env, Config, SentryConfig
from bob.infrastructure.adapters import (
    telegram_uploader,
    telegram_queue,
    text_to_speech,
    language_detector,
    image_text_recognizer,
)
from bob.infrastructure.repos import chat, state

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


class PortsModule(Module):
    def __init__(self, config: Config):
        self.config = config

    @provider
    def provide_image_text_recognizer(self) -> ports.ImageTextRecognizer:
        if self.config.use_stub_image_recognizer:
            return image_text_recognizer.StubImageTextRecognizer()

        return image_text_recognizer.GoogleImageTextRecognizer()

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


class ReposModule(Module):
    def __init__(self, config: Config):
        self.config = config

    @provider
    def provide_chat_repo(self) -> repos.ChatRepository:
        return chat.StaticChatRepository()

    @provider
    def provide_state_repo(self) -> repos.StateRepository:
        match self.config.repo_type:
            case "memory":
                return state.MemoryStateRepository()
            case "firestore":
                return state.FirestoreStateRepository()
            case repo_type:
                raise ValueError(f"Unknown repo type: {repo_type}")


def initialize() -> Application:
    _setup_logging()

    config = Config.from_env(load_env(""))
    _setup_sentry(config.sentry)

    injector = Injector(
        modules=[
            PortsModule(config),
            ReposModule(config),
        ],
    )
    return injector.get(Application)
