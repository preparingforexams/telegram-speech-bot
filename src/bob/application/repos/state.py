import abc
from typing import TypeAlias, Sequence, Mapping

Primitive: TypeAlias = (
    str | int | float | bool | None | Sequence["Primitive"] | Mapping[str, "Primitive"]
)


class StateRepository(abc.ABC):
    @abc.abstractmethod
    async def get_value(self, key: str) -> dict[str, Primitive] | None:
        pass

    @abc.abstractmethod
    async def set_value(self, key: str, value: Mapping[str, Primitive]) -> None:
        pass
