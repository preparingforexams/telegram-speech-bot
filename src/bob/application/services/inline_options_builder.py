from dataclasses import dataclass

from injector import inject

from bob.application import ports
from bob.domain.model import InlineCode, InlineMessageState, InlineOption


@inject
@dataclass
class InlineOptionsBuilder:
    def map_to_code(self, voice: ports.TextToSpeech.Voice) -> InlineCode | None:
        name = voice.name
        if name == "de-DE-GiselaNeural":
            return InlineCode.CHILD

        if name == "de-CH-LeniNeural":
            return InlineCode.SWISS

        if name == "nl-NL-MaartenNeural":
            return InlineCode.HOLLAND

        return None

    def build(
        self,
        state: InlineMessageState,
    ) -> list[InlineOption]:
        result: list[InlineOption] = []
        if not state["was_swiss"]:
            result.append(
                InlineOption(
                    text="🫕🇨🇭",
                    text_message_id=state["message_id"],
                    code=InlineCode.SWISS,
                )
            )

        if not state["was_child"]:
            result.append(
                InlineOption(
                    text="👶🏼",
                    text_message_id=state["message_id"],
                    code=InlineCode.CHILD,
                )
            )

        if not state["was_holland"]:
            result.append(
                InlineOption(
                    text="🧀",
                    text_message_id=state["message_id"],
                    code=InlineCode.HOLLAND,
                )
            )

        return result
