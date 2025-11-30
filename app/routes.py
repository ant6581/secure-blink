from fastapi import APIRouter, Request
from models.requests.create_secret import CreateSecretRequest, CreateSecretResponse
from handlers.create_secret import CreateSecretHandler
from handlers.get_secret import GetSecretHandler
from handlers.delete_secret import DeleteSecretHandler
from models.requests.get_secret import (
    GetSecretRequest,
    GetSecretResponse,
    PassphraseRequiredResponse,
)

router = APIRouter(prefix="/api")


@router.post("/secret")
async def create_secret(request: CreateSecretRequest) -> CreateSecretResponse:
    return await CreateSecretHandler.handle(request)


@router.get("/secret/{secret_id}")
async def get_secret(
    request: Request, secret_id: str
) -> GetSecretResponse | PassphraseRequiredResponse:
    request = GetSecretRequest(
        secret_id=secret_id, verify_hash=request.query_params.get("verify_hash")
    )
    return await GetSecretHandler.handle(request)


@router.delete("/secret/{secret_id}")
async def delete_secret(secret_id: str) -> None:
    await DeleteSecretHandler.handle(secret_id)
