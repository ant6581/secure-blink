from clients.redis import Redis
from fastapi import HTTPException


class DeleteSecretHandler:
    @staticmethod
    async def handle(secret_id: str) -> None:
        keys_deleted = await Redis().delete(secret_id)

        if keys_deleted:
            return

        raise HTTPException(status_code=404, detail="Secret not found")
