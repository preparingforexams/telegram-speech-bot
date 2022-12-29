from bob.application.ports import ImageTextRecognizer


class StubImageTextRecognizer(ImageTextRecognizer):
    async def detect_text(self, image: bytes) -> str | None:
        return None
