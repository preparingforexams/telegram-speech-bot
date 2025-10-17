import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langcodes import Language


class LanguageDetector(abc.ABC):
    @abc.abstractmethod
    async def detect_language(self, text: str) -> Language | None:
        """
        Args:
            text: a text input

        Returns:
            the most probable language of the text

        Raises:
            IoException: if any IO error occurred

        """
        pass
