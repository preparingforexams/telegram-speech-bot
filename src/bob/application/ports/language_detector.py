import abc

from langcodes import Language


class LanguageDetector(abc.ABC):
    @abc.abstractmethod
    async def detect_language(self, text: str) -> Language:
        """
        Args:
            text: a text input

        Returns:
            the most probable language of the text

        Raises:
            LanguageException: if no language could be detected
            IoException: if any IO error occurred

        """
        pass
