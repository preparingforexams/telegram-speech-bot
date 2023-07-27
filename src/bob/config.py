from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, cast, overload

from dotenv import dotenv_values


class Env:
    def __init__(self, values: dict[str, str]):
        self._values = values

    @overload
    def get_string(
        self,
        key: str,
        default: str,
    ) -> str:
        pass

    @overload
    def get_string(
        self,
        key: str,
        default: None = None,
    ) -> str | None:
        pass

    def get_string(
        self,
        key: str,
        default: str | None = None,
    ) -> str | None:
        value = self._values.get(key)
        if value is None or not value.strip():
            return default

        return value

    def get_bool(
        self,
        key: str,
        default: bool,
    ) -> bool:
        value = self._values.get(key)
        if value is None:
            return default

        stripped = value.strip()
        if not stripped:
            return default

        return stripped == "true"

    @overload
    def get_int(
        self,
        key: str,
        default: int,
    ) -> int:
        pass

    @overload
    def get_int(
        self,
        key: str,
        default: None = None,
    ) -> int | None:
        pass

    def get_int(
        self,
        key: str,
        default: int | None = None,
    ) -> int | None:
        value = self._values.get(key)
        if value is None or not value.strip():
            return default

        return int(value)

    @overload
    def get_int_list(
        self,
        key: str,
        default: list[int],
    ) -> list[int]:
        pass

    @overload
    def get_int_list(
        self,
        key: str,
        default: None = None,
    ) -> list[int] | None:
        pass

    def get_int_list(
        self,
        key: str,
        default: list[int] | None = None,
    ) -> list[int] | None:
        values = self._values.get(key)

        if values is None or not values.strip():
            return default

        return [int(value) for value in values.split(",")]


def _remove_none_values(data: dict[str, str | None]) -> dict[str, str]:
    for key, value in data.items():
        if value is None:
            del data[key]

    return cast(dict[str, str], data)


def _load_env(name: str | None) -> dict[str, str]:
    if not name:
        return _remove_none_values(dotenv_values(".env"))
    else:
        return _remove_none_values(dotenv_values(f".env.{name}"))


def load_env(names: Iterable[str]) -> Env:
    result = {**_load_env(None)}

    for name in names:
        result.update(_load_env(name))

    from os import environ

    result.update(environ)

    return Env(result)


@dataclass
class SentryConfig:
    dsn: str
    release: str

    @classmethod
    def from_env(cls, env: Env) -> SentryConfig | None:
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
    def from_env(cls, env: Env) -> AzureTtsConfig:
        return cls(
            region=env.get_string("AZURE_SPEECH_REGION"),
            key=env.get_string("AZURE_SPEECH_KEY"),
        )


@dataclass
class Config:
    use_stub_tts: bool
    use_stub_image_recognizer: bool
    use_stub_language_detector: bool
    azure_tts: AzureTtsConfig
    gcp_project: str | None
    repo_type: str
    sentry: SentryConfig | None
    telegram: TelegramConfig | None

    @classmethod
    def from_env(cls, env: Env) -> Config:
        return cls(
            use_stub_tts=env.get_bool("TTS_USE_STUB", True),
            use_stub_image_recognizer=env.get_bool("OCR_USE_STUB", True),
            use_stub_language_detector=env.get_bool("LANGUAGE_DETECTOR_USE_STUB", True),
            azure_tts=AzureTtsConfig.from_env(env),
            gcp_project=env.get_string("GOOGLE_CLOUD_PROJECT"),
            repo_type=env.get_string("REPO_TYPE", "memory"),
            sentry=SentryConfig.from_env(env),
            telegram=TelegramConfig.from_env(env),
        )


@dataclass
class TelegramConfig:
    token: str
    polling_timeout: int

    @classmethod
    def from_env(cls, env: Env) -> TelegramConfig | None:
        token = env.get_string("TELEGRAM_TOKEN")
        if token is None:
            return None

        return cls(
            token=token,
            polling_timeout=env.get_int("TELEGRAM_POLLING_TIMEOUT", 10),
        )
