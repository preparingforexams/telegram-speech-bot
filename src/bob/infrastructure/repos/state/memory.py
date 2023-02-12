from bob.application.repos import StateRepository
from bob.application.repos.state import Primitive


class MemoryStateRepository(StateRepository):
    def __init__(self) -> None:
        self._db: dict[str, dict[str, Primitive]] = {}

    async def get_value(self, key: str) -> dict[str, Primitive] | None:
        return self._db.get(key)

    async def set_value(self, key: str, value: dict[str, Primitive]) -> None:
        self._db[key] = value
