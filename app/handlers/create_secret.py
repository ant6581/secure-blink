import uuid
from fastapi import APIRouter
from models.create_secret import CreateSecretRequest
from clients.redis import Redis


class CreateSecretHandler:
    @staticmethod
    async def handle(request: CreateSecretRequest) -> dict[str, str]:
        secret_id = str(uuid.uuid4())

        await Redis().create_secret(secret_id=secret_id, secret=request)

        return {"id": secret_id}
