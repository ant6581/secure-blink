import os
import json
from models.secret import EncryptedSecret

from redis.asyncio import Redis as AsyncRedis, ConnectionPool
from certifi import where
from typing import Any, Final


class Singleton(type):
    _instances: dict[type, object] = {}

    def __call__(cls: Any, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Redis(metaclass=Singleton):

    pool = None

    def __init__(self) -> None:
        if self.pool is None:
            self.pool = ConnectionPool.from_url(
                url=os.getenv("REDIS_URL"),
                ssl_cert_reqs="required",
                ssl_ca_certs=where(),
                decode_responses=True,
            )
            self.client = AsyncRedis(connection_pool=self.pool)

    def __call__(self) -> AsyncRedis:
        return self.client

    def __getattr__(self, name: str) -> Any:
        return getattr(self.client, name)

    async def save_encrypted_secret(self, secret: EncryptedSecret, ttl: int) -> None:
        data = secret.model_dump_json(
            include={"ciphertext", "passphrase_hash"}, exclude_unset=True
        )
        await self.setex(secret.id, ttl, data)

    async def get_encrypted_secret(self, secret_id: str) -> EncryptedSecret | None:
        data = await self.get(secret_id)
        if not data:
            return None

        ttl = await self.ttl(secret_id)

        return EncryptedSecret(id=secret_id, ttl=ttl, **json.loads(data))
