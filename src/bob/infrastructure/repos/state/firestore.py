from asyncio.locks import Lock
from typing import TYPE_CHECKING, cast

from google.cloud.firestore import AsyncClient, AsyncCollectionReference

from bob.application.repos import StateRepository
from bob.application.repos.state import Primitive

if TYPE_CHECKING:
    from collections.abc import Mapping


class FirestoreStateRepository(StateRepository):
    def __init__(self) -> None:
        self._lock = Lock()
        self._client: AsyncClient | None = None

    async def _get_client(self) -> AsyncClient:
        client = self._client
        if client:
            return client

        async with self._lock:
            client = AsyncClient()
            self._client = client

        return client

    async def _collection(self) -> AsyncCollectionReference:
        client = await self._get_client()
        return client.collection("bob-state")

    async def set_value(self, key: str, value: Mapping[str, Primitive]) -> None:
        collection = await self._collection()
        await collection.document(key).set(cast(dict[str, Primitive], value))

    async def get_value(self, key: str) -> dict[str, Primitive] | None:
        collection = await self._collection()
        doc = await collection.document(key).get()
        if doc.exists:
            return doc.to_dict()
        else:
            return None
