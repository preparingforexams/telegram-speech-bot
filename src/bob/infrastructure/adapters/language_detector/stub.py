from langcodes import Language

from bob.application.ports import LanguageDetector


class StubLanguageDetector(LanguageDetector):
    async def detect_language(self, text: str) -> Language:
        return Language.get("de_DE")
