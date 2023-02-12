import functools
from typing import Mapping, cast

from google.cloud.firestore import AsyncClient, AsyncCollectionReference

from bob.application.repos import StateRepository
from bob.application.repos.state import Primitive


class FirestoreStateRepository(StateRepository):
    @functools.cached_property
    async def _client(self) -> AsyncClient:
        return AsyncClient()

    async def _collection(self) -> AsyncCollectionReference:
        client = await self._client
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
