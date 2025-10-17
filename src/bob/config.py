from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from bs_nats_updater import NatsConfig

if TYPE_CHECKING:
    from bs_config import Env


@dataclass
class SentryConfig:
    dsn: str
    release: str

    @classmethod
    def from_env(cls, env: Env) -> Self | None:
        dsn = env.get_string("SENTRY_DSN")

        if not dsn:
            return None

        return cls(
            dsn=dsn,
            release=env.get_string("APP_VERSION", default="debug"),
        )


@dataclass
class AzureTtsConfig:
    region: str | None
    key: str | None

    @classmethod
    def from_env(cls, env: Env) -> Self:
        return cls(
            region=env.get_string("SPEECH_REGION"),
            key=env.get_string("SPEECH_KEY"),
        )


@dataclass
class TelegramConfig:
    token: str
    polling_timeout: int

    @classmethod
    def from_env(cls, env: Env) -> Self | None:
        token = env.get_string("TOKEN")
        if token is None:
            return None

        return cls(
            token=token,
            polling_timeout=env.get_int("POLLING_TIMEOUT", default=10),
        )


@dataclass
class Config:
    use_stub_tts: bool
    use_stub_image_recognizer: bool
    use_stub_language_detector: bool
    azure_tts: AzureTtsConfig
    gcp_project: str | None
    nats: NatsConfig | None
    repo_type: str
    sentry: SentryConfig | None
    telegram: TelegramConfig | None

    @classmethod
    def from_env(cls, env: Env) -> Self:
        return cls(
            use_stub_tts=env.get_bool(
                "TTS_USE_STUB",
                default=True,
            ),
            use_stub_image_recognizer=env.get_bool(
                "OCR_USE_STUB",
                default=True,
            ),
            use_stub_language_detector=env.get_bool(
                "LANGUAGE_DETECTOR_USE_STUB",
                default=True,
            ),
            azure_tts=AzureTtsConfig.from_env(env.scoped("AZURE_")),
            gcp_project=env.get_string("GOOGLE_CLOUD_PROJECT"),
            nats=NatsConfig.from_env(env.scoped("NATS_"), is_optional=True),
            repo_type=env.get_string("REPO_TYPE", default="memory"),
            sentry=SentryConfig.from_env(env),
            telegram=TelegramConfig.from_env(env.scoped("TELEGRAM_")),
        )
