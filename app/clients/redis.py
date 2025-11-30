import os
import json
from models.create_secret import CreateSecretRequest
from redis.asyncio import Redis as AsyncRedis, ConnectionPool
from certifi import where
from typing import Final


class Singleton(type):
    _instances: dict[type, object] = {}

    def __call__(cls, *args, **kwargs):
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
            )
            self.client = AsyncRedis(connection_pool=self.pool)

    def __call__(self) -> AsyncRedis:
        return self.client

    def __getattr__(self, name):
        return getattr(self.client, name)

    async def create_secret(self, secret_id: str, secret: CreateSecretRequest) -> None:
        data = {
            "ciphertext": secret.ciphertext,
            "passphrase_hash": secret.config.passphrase_hash,
        }
        await self.setex(secret_id, secret.config.ttl, json.dumps(data))
