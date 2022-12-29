from dataclasses import dataclass
from enum import Enum


class InlineCode(str, Enum):
    CHILD = "u18"
    SWISS = "ch"


@dataclass
class InlineOption:
    text: str
    code: InlineCode
