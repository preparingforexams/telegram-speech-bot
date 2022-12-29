from dataclasses import dataclass


@dataclass(frozen=True)
class Chat:
    id: int
    enable_inline_options: bool = False
    delete_text_message: bool = False
    fixed_voice: str | None = None
    enable_ocr: bool = False
