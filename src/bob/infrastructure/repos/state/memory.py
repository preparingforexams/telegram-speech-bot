from bob.application.repos import StateRepository


class MemoryStateRepository(StateRepository):
    def __init__(self) -> None:
        self._db: dict[str, dict] = {}

    async def get_value(self, key: str) -> dict | None:
        return self._db.get(key)

    async def set_value(self, key: str, value: dict) -> None:
        self._db[key] = value
