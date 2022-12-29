from asyncache import cached
from google.cloud.firestore import AsyncClient, AsyncCollectionReference

from bob.application.repos import StateRepository


class FirestoreStateRepository(StateRepository):
    @property
    @cached({})
    async def _client(self) -> AsyncClient:
        return AsyncClient()

    async def _collection(self) -> AsyncCollectionReference:
        client = await self._client
        return client.collection("bob-state")

    async def set_value(self, key: str, value: dict) -> None:
        collection = await self._collection()
        await collection.document(key).set(value)

    async def get_value(self, key: str) -> dict | None:
        collection = await self._collection()
        doc = await collection.document(key).get()
        if doc.exists:
            return doc.to_dict()
        else:
            return None
