from fastapi import APIRouter
from models.create_secret import CreateSecretRequest
from handlers.create_secret import CreateSecretHandler
from handlers.get_secret import GetSecretHandler
from handlers.delete_secret import DeleteSecretHandler

router = APIRouter(prefix="/api")


@router.post("/secret")
async def create_secret(request: CreateSecretRequest) -> dict[str, str]:
    return await CreateSecretHandler.handle(request)


@router.get("/secret/{secret_id}")
async def get_secret(secret_id: str, verify_hash: str | None = None) -> dict[str, str]:
    return await GetSecretHandler.handle(secret_id, verify_hash)


@router.delete("/secret/{secret_id}")
async def delete_secret(secret_id: str) -> None:
    return await DeleteSecretHandler.handle(secret_id)
