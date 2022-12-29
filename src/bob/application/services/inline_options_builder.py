from dataclasses import dataclass

from injector import inject

from bob.application import ports
from bob.domain.model import InlineOption, InlineMessageState, InlineCode


@inject
@dataclass
class InlineOptionsBuilder:
    def map_to_code(self, voice: ports.TextToSpeech.Voice) -> InlineCode | None:
        name = voice.name
        if name == "de-DE-GiselaNeural":
            return InlineCode.CHILD

        if name == "de-CH-LeniNeural":
            return InlineCode.SWISS

        return None

    def build(
        self,
        state: InlineMessageState,
    ) -> list[InlineOption]:
        result: list[InlineOption] = []
        if state["was_swiss"]:
            result.append(
                InlineOption(
                    text="Swiss me daddy",
                    text_message_id=state["message_id"],
                    code=InlineCode.SWISS,
                )
            )

        if state["was_child"]:
            result.append(
                InlineOption(
                    text="U18",
                    text_message_id=state["message_id"],
                    code=InlineCode.CHILD,
                )
            )

        return result
