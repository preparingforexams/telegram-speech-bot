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
        _LOG.info("Received callback with code %s", callback.code)
