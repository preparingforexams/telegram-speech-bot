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
        dsn = env.get_string("sentry-dsn")

        if not dsn:
            return None

        return cls(
            dsn=dsn,
            release=env.get_string("app-version", default="debug"),
        )


@dataclass
class AzureTtsConfig:
    region: str | None
    key: str | None

    @classmethod
    def from_env(cls, env: Env) -> Self:
        return cls(
            region=env.get_string("speech-region"),
            key=env.get_string("speech-key"),
        )


@dataclass
class TelegramConfig:
    token: str
    polling_timeout: int

    @classmethod
    def from_env(cls, env: Env) -> Self | None:
        token = env.get_string("token")
        if token is None:
            return None

        return cls(
            token=token,
            polling_timeout=env.get_int("polling-timeout", default=10),
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
                "tts-use-stub",
                default=True,
            ),
            use_stub_image_recognizer=env.get_bool(
                "ocr-use-stub",
                default=True,
            ),
            use_stub_language_detector=env.get_bool(
                "language-detector-use-stub",
                default=True,
            ),
            azure_tts=AzureTtsConfig.from_env(env / "azure"),
            gcp_project=env.get_string("google-cloud-project"),
            nats=NatsConfig.from_env(env / "nats", is_optional=True),
            repo_type=env.get_string("repo-type", default="memory"),
            sentry=SentryConfig.from_env(env),
            telegram=TelegramConfig.from_env(env / "telegram"),
        )
