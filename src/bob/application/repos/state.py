import abc
from collections.abc import Mapping, Sequence

type Primitive = (
    str | int | float | bool | None | Sequence["Primitive"] | Mapping[str, "Primitive"]
)


class StateRepository(abc.ABC):
    @abc.abstractmethod
    async def get_value(self, key: str) -> dict[str, Primitive] | None:
        pass

    @abc.abstractmethod
    async def set_value(self, key: str, value: Mapping[str, Primitive]) -> None:
        pass
