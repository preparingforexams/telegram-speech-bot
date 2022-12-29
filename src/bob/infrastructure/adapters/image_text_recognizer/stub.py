from bob.application.ports import ImageTextRecognizer


class StubImageTextRecognizer(ImageTextRecognizer):
    async def detect_text(self, image_url: str) -> str | None:
        return None
