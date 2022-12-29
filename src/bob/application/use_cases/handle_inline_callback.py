import logging
from dataclasses import dataclass

from injector import inject
from langcodes import Language

from bob.application import repos, ports
from bob.domain.model import InlineCallback, InlineMessageState, InlineCode

_LOG = logging.getLogger(__name__)


@inject
@dataclass
class HandleInlineCallback:
    state_repo: repos.StateRepository
    telegram: ports.TelegramUploader
    tts: list[ports.TextToSpeech]

    async def __call__(self, callback: InlineCallback) -> None:
        key = f"{callback.chat_id}-{callback.text_message_id}"
        state: InlineMessageState | None = await self.state_repo.get_value(key)  # type: ignore

        if state is None:
            _LOG.warning("No state for callback query %s", callback)
            return

        if callback.code == InlineCode.CHILD:
            if state["was_child"]:
                _LOG.debug("Not sending child message because it was already sent")
                return

            await self._send_speech(
                state,
                language=Language.get("de_DE"),
                voice_name="de-DE-GiselaNeural",
            )
            state["was_child"] = True
        elif callback.code == InlineCode.SWISS:
            if state["was_swiss"]:
                _LOG.debug("Not sending swiss message because it was already sent")
                return

            await self._send_speech(
                state,
                language=Language.get("de_CH"),
                voice_name="de-CH-LeniNeural",
            )
            state["was_swiss"] = True
        else:
            raise ValueError(f"Unknown code: {callback.code}")

        await self.state_repo.set_value(key, state)  # type: ignore

    async def _find_voice(
        self,
        language: Language,
        name: str,
    ) -> ports.TextToSpeech.Voice:
        for tts in self.tts:
            for voice in await tts.get_supported_voices(language):
                if voice.name == name:
                    return voice

        raise ValueError(f"Unsupported voice for lang {language}: {name}")

    async def _send_speech(
        self,
        state: InlineMessageState,
        language: Language,
        voice_name: str,
    ) -> None:
        voice = await self._find_voice(language, voice_name)
        speech = await voice.convert_to_speech(state["text"], language)

        # TODO: caption, replyto
        await self.telegram.send_voice_message(
            chat_id=state["chat_id"],
            voice=speech,
        )
