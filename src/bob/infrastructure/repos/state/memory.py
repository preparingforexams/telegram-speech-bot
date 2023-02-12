from typing import Mapping

from bob.application.repos import StateRepository
from bob.application.repos.state import Primitive


class MemoryStateRepository(StateRepository):
    def __init__(self) -> None:
        self._db: dict[str, Mapping[str, Primitive]] = {}

    async def get_value(self, key: str) -> dict[str, Primitive] | None:
        result = self._db.get(key)
        if result is None:
            return None

        return dict(result)

    async def set_value(self, key: str, value: Mapping[str, Primitive]) -> None:
        self._db[key] = value
