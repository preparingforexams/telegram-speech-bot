import logging

from google.cloud.translate_v3 import TranslationServiceAsyncClient
from langcodes import Language

from bob.application.exceptions.language import LanguageException
from bob.application.ports import LanguageDetector

_LOG = logging.getLogger(__name__)

from cachetools import cached


class GoogleCloudTranslationLanguageDetector(LanguageDetector):
    def __init__(self, project_id: str):
        self._parent = f"projects/{project_id}/locations/global"

    @property
    @cached({})
    def _client(self) -> TranslationServiceAsyncClient:
        return TranslationServiceAsyncClient()

    async def detect_language(self, text: str) -> Language:
        response = await self._client.detect_language(
            content=text,
            parent=self._parent,
            mime_type="text/plain",
        )

        languages = response.languages
        if len(languages) == 0:
            raise LanguageException("No language detected!")

        if len(languages) > 1:
            # I want to be notified of that, but it doesn't matter
            _LOG.error("The Google docs fucking lied!")

        language = languages[0]
        _LOG.info(
            "Detected language %s with confidence %f",
            language.language_code,
            language.confidence,
        )

        return Language.get(language.language_code)
