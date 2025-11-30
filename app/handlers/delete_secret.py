from clients.redis import Redis
from fastapi import HTTPException


class DeleteSecretHandler:
    @staticmethod
    async def handle(secret_id: str) -> dict[str, str]:
        result: int = await Redis().delete(secret_id)

        if result > 0:
            return {"message": "Secret deleted"}
        raise HTTPException(status_code=404, detail="Secret not found")
