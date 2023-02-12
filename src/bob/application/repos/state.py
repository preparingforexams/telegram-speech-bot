import abc
from typing import TypeAlias

Primitive: TypeAlias = (
    str | int | float | bool | None | list["Primitive"] | dict[str, "Primitive"]
)


class StateRepository(abc.ABC):
    @abc.abstractmethod
    async def get_value(self, key: str) -> dict[str, Primitive] | None:
        pass

    @abc.abstractmethod
    async def set_value(self, key: str, value: dict[str, Primitive]) -> None:
        pass
