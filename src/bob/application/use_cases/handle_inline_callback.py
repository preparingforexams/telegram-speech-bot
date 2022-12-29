import logging
from dataclasses import dataclass

from injector import inject

from bob.application import repos
from bob.domain.model import InlineCallback

_LOG = logging.getLogger(__name__)


@inject
@dataclass
class HandleInlineCallback:
    state_repo: repos.StateRepository

    async def __call__(self, callback: InlineCallback) -> None:
        state = await self.state_repo.get_value(
            f"{callback.chat_id}-{callback.message_id}"
        )
        if state is None:
            _LOG.warning("No state for callback query %s", callback)
            return

        _LOG.info("Found state %s", state)
